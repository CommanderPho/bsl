import argparse

from bsl import StreamViewer


def run():
    """Entrypoint for bsl_stream_viewer usage."""
    parser = argparse.ArgumentParser(
        prog="BSL StreamViewer",
        description="Starts a real-time viewer for a stream on LSL network.",
    )
    parser.add_argument(
        "-s",
        "--stream_name",
        type=str,
        metavar="str",
        help="stream to display/plot.",
    )
    parser.add_argument(
        "-r",
        "--record_dir",
        type=str,
        metavar="str",
        help="directory to save recordings to.",
    )
    parser.add_argument(
        "--bp_low",
        type=float,
        metavar="float",
        help="bandpass filter low cutoff frequency in Hz.",
    )
    parser.add_argument(
        "--bp_high",
        type=float,
        metavar="float",
        help="bandpass filter high cutoff frequency in Hz.",
    )

    args = parser.parse_args()
    stream_name = args.stream_name
    record_dir = args.record_dir
    bp_low = args.bp_low
    bp_high = args.bp_high

    stream_viewer = StreamViewer(stream_name, record_dir=record_dir, bp_low=bp_low, bp_high=bp_high)
    stream_viewer.start()
