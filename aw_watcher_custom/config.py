import sys
import argparse

from aw_core.config import load_config_toml

default_config = """
[aw-watcher-custom]
poll_time = 5
process_name = ""
[aw-watcher-custom-testing]
poll_time = 1
process_name = ""
""".strip()


def load_config(testing: bool):
    section = "aw-watcher-custom" + ("-testing" if testing else "")
    return load_config_toml("aw-watcher-custom", default_config)[section]


def parse_args():
    # get testing in a dirty way, because we need it for the config lookup
    testing = "--testing" in sys.argv
    config = load_config(testing)

    default_poll_time = config["poll_time"]
    default_process_name = config["process_name"]

    parser = argparse.ArgumentParser("huantian's custom Activity Watch watcher.")
    parser.add_argument("--host", dest="host", type=str)
    parser.add_argument("--port", dest="port", type=int)
    parser.add_argument(
        "--testing", dest="testing", action="store_true", help="run in testing mode"
    )
    parser.add_argument(
        "--verbose",
        dest="verbose",
        action="store_true",
        help="run with verbose logging",
    )
    parser.add_argument(
        "--poll-time", dest="poll_time", type=float, default=default_poll_time
    )
    parser.add_argument(
        "--process-name", dest="process_name", type=str, default=default_process_name
    )
    return parser.parse_args()
