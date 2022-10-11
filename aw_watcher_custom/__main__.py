from aw_core.log import setup_logging

from aw_watcher_custom.config import parse_args
from aw_watcher_custom.watcher import Watcher


def main() -> None:
    args = parse_args()

    # Set up logging
    setup_logging(
        "aw-watcher-custom",
        testing=args.testing,
        verbose=args.verbose,
        log_stderr=True,
        log_file=True,
    )

    # Start watcher
    watcher = Watcher(args, testing=args.testing)
    watcher.run()


if __name__ == "__main__":
    main()
