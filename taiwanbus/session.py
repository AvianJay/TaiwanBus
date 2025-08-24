# My code is shit.
# Bus session
import time
import threading
from . import api
from datetime import datetime


class BusSession:
    def __init__(self, route_key, provider=api.Provider.TWN, simulate_rate=1):
        super()
        self.BUSINFO = None
        self.SIMULATED_BUSINFO = None
        self.LAST_UPDATE = 0
        self.ROUTE_KEY = route_key
        self.SIMULATE_THREAD = threading.Thread(
            target=self.simulate_runner,
            daemon=True,
        )
        self.SIMULATE_STOPED = True
        self.SIMULATE_RATE = simulate_rate
        api.update_provider(provider)

    def update(self):
        self.BUSINFO = api.get_complete_bus_info(self.ROUTE_KEY)
        self.LAST_UPDATE = datetime.now().timestamp()

    def get_stop(self, stopid):
        for path in self.BUSINFO.values():
            for stop in path["stops"]:
                if stop.get("stop_id") == stopid:
                    return stop

    def get_path(self, pathid):
        return self.BUSINFO.get(pathid)

    def simulate_runner(self):
        while True:
            if self.SIMULATE_STOPED:
                break
            now = datetime.now().timestamp()
            time_diff = int(now - self.LAST_UPDATE)
            self.SIMULATED_BUSINFO = self.BUSINFO.copy()
            for path in self.SIMULATED_BUSINFO.values():
                for stop in path["stops"]:
                    stop["sec"] += time_diff
            time.sleep(self.SIMULATE_RATE)

    def start_simulate(self):
        self.SIMULATE_STOPED = False
        self.SIMULATE_THREAD.start()

    def stop_simulate(self):
        self.SIMULATE_STOPED = True

    def get_simulated_info(self):
        return self.SIMULATED_BUSINFO

    def get_info(self):
        return self.BUSINFO
