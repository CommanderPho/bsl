import sys
import time

from PyQt5.QtWidgets import QApplication

from ..stream_receiver import StreamEEG, StreamReceiver
from ..utils._checks import check_type
from ..utils.logs import logger
from ..utils.lsl import search_lsl
from .control_gui.control_eeg import ControlGUI_EEG
from .scope.scope_eeg import ScopeEEG


class StreamViewer:
    """Class for visualizing the signals coming from an LSL stream.

    The stream viewer will connect to only one LSL stream. If ``stream_name``
    is set to ``None``, an automatic search is performed followed by a prompt
    if multiple non-markers streams are found.

    Parameters
    ----------
    stream_name : str | None
        Servers' name to connect to. ``None`` will prompt the user.
    record_dir : str | None
        Directory to save recordings to. ``None`` leaves the recording
        directory unset.
    bp_low : float | None
        Bandpass filter low cutoff frequency in Hz. ``None`` uses default
        configuration.
    bp_high : float | None
        Bandpass filter high cutoff frequency in Hz. ``None`` uses default
        configuration.
    bp_off : bool
        Disable bandpass filtering (equivalent to unchecking bandpass filter box).
    """

    def __init__(self, stream_name=None, record_dir=None, bp_low=None, bp_high=None, bp_off=False):
        self._stream_name = StreamViewer._check_stream_name(stream_name)
        self._record_dir = record_dir
        self._bp_low = bp_low
        self._bp_high = bp_high
        self._bp_off = bp_off

    def start(self, bufsize=0.2):
        """Connect to the selected amplifier and plot the streamed data.

        If ``stream_name`` is not provided, look for available streams on the
        network.

        Parameters
        ----------
        bufsize : int | float
            Buffer/window size of the attached StreamReceiver.
            The default ``0.2`` should work in most cases since data is fetched
            every 20 ms.
        """
        logger.info("Connecting to the stream: %s", self.stream_name)
        self._sr = StreamReceiver(
            bufsize=bufsize, winsize=bufsize, stream_name=self._stream_name
        )
        self._sr.streams[self._stream_name].blocking = False
        time.sleep(bufsize)  # Delay to fill the LSL buffer.

        if isinstance(self._sr.streams[self._stream_name], StreamEEG):
            self._scope = ScopeEEG(self._sr, self._stream_name)
            app = QApplication(sys.argv)
            self._ui = ControlGUI_EEG(self._scope)
            
            # Apply command line parameters if provided
            if self._record_dir is not None:
                self._ui._ui.lineEdit_recording_dir.setText(self._record_dir)
                self._ui._ui.pushButton_start_recording.setEnabled(True)
            
            if self._bp_off:
                self._ui._ui.checkBox_bandpass.setChecked(False)
                self._scope.apply_bandpass = False
                
            if (self._bp_low is not None) and (self._bp_high is not None):
                self._ui._ui.doubleSpinBox_bandpass_low.setValue(self._bp_low)
                self._ui._ui.doubleSpinBox_bandpass_high.setValue(self._bp_high)
                if not self._bp_off:
                    self._scope.init_bandpass_filter(low=self._bp_low, high=self._bp_high)
                    self._ui._ui.checkBox_bandpass.setChecked(True)
                    self._scope.apply_bandpass = True
            
            sys.exit(app.exec_())
        else:
            logger.error(
                "Unsupported stream type %s",
                type(self._sr.streams[self._stream_name]),
            )

    # --------------------------------------------------------------------
    @staticmethod
    def _check_stream_name(stream_name):  # noqa
        """
        Check that the stream_name is valid or search for a valid stream on
        the network.
        """
        check_type(stream_name, (None, str), item_name="stream_name")
        if stream_name is None:
            stream_name = search_lsl(ignore_markers=True)
            if stream_name is None:
                raise RuntimeError("No LSL stream found.")
        return stream_name

    # --------------------------------------------------------------------
    @property
    def stream_name(self):
        """Connected stream's name.

        :type: str
        """
        return self._stream_name

    @property
    def sr(self):
        """Connected StreamReceiver.

        :type: StreamReceiver
        """
        return self._sr
