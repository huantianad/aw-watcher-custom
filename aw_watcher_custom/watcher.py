import logging
from datetime import datetime, timedelta, timezone
from time import sleep

import psutil
from aw_client import ActivityWatchClient
from aw_core.models import Event

from .config import load_config


logger = logging.getLogger(__name__)
td1ms = timedelta(milliseconds=1)


def is_process_running(process_name: str) -> bool:
    """
    Check if there is any running process that contains the given name.
    """
    for proc in psutil.process_iter():
        try:
            if process_name.lower() in proc.name().lower():
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


class Settings:
    # How often we should poll for input activity
    poll_time: int
    # Substring of names of processes to check
    process_name: str

    def __init__(self, config_section, poll_time=None, process_name=None):
        self.poll_time = poll_time or config_section["poll_time"]
        self.process_name = process_name or config_section["process_name"]


class Watcher:
    def __init__(self, args, testing=False):
        # Read settings from config
        self.settings = Settings(
            load_config(testing),
            poll_time=args.poll_time,
            process_name=args.process_name,
        )

        self.client = ActivityWatchClient(
            "aw-watcher-custom", host=args.host, port=args.port, testing=testing
        )
        self.bucketname = f"{self.client.client_name}_{self.client.client_hostname}"

    def run(self) -> None:
        logger.info("aw-watcher-custom started")

        # Initialization
        sleep(1)

        eventtype = "unitystatus"
        self.client.create_bucket(self.bucketname, eventtype, queued=True)

        # Start loop
        with self.client:
            self.heartbeat_loop()

    def ping(self, active: bool, timestamp: datetime, duration: float = 0):
        data = {"status": "active" if active else "not-active"}
        e = Event(timestamp=timestamp, duration=duration, data=data)
        pulsetime = self.settings.poll_time + 1
        self.client.heartbeat(self.bucketname, e, pulsetime=pulsetime, queued=True)

    def heartbeat_loop(self) -> None:
        was_active = False
        last_change = datetime.now(timezone.utc)

        while True:
            try:
                now = datetime.now(timezone.utc)
                now_active = is_process_running(self.settings.process_name)

                seconds_since_change = (now - last_change).seconds

                # State changed!
                if was_active != now_active:
                    # Send a heartbeat
                    self.ping(was_active, timestamp=last_change)

                    # Then send the new event, just a bit later in the queue
                    was_active = now_active
                    self.ping(was_active, timestamp=last_change + td1ms, duration=0)
                    last_change = now
                # Send a heartbeat if no state change was made
                else:
                    if was_active:
                        self.ping(
                            was_active,
                            timestamp=last_change,
                            duration=seconds_since_change,
                        )
                    else:
                        self.ping(was_active, timestamp=last_change)

                sleep(self.settings.poll_time)

            except KeyboardInterrupt:
                logger.info("aw-watcher-custom stopped by keyboard interrupt")
                break
