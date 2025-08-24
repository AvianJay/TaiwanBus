# My code is shit.
# Bus session
import time
import copy
import threading
from . import api
from datetime import datetime


class BusSession:
    def __init__(self, route_key, provider=api.Provider.TWN, simulate_rate=1):
        self.BUSINFO = None
        self.SIMULATED_BUSINFO = None
        self.LAST_UPDATE = 0
        self.ROUTE_KEY = route_key
        self.SIMULATE_THREAD = threading.Thread(
            target=self.simulate_runner,
            daemon=True,
        )
        self.SIMULATE_STOPPED = True
        self.SIMULATE_RATE = simulate_rate
        self.SIMULATE_TIME_DIFF = 0
        api.update_provider(provider)

    def update(self):
        self.BUSINFO = api.get_complete_bus_info(self.ROUTE_KEY)
        self.LAST_UPDATE = datetime.now().timestamp()

    def get_stop(self, stopid: int):
        if self.BUSINFO is None:
            return None
        for path in self.BUSINFO.values():
            for stop in path["stops"]:
                if stop.get("stop_id") == stopid:
                    return stop

    def get_path(self, pathid: int):
        return self.BUSINFO.get(pathid)

    def simulate_runner(self):
        while True:
            if self.SIMULATE_STOPPED:
                break
            now = datetime.now().timestamp()
            self.SIMULATE_TIME_DIFF = int(now - self.LAST_UPDATE)
            self.SIMULATED_BUSINFO = copy.deepcopy(self.BUSINFO)
            for path in self.SIMULATED_BUSINFO.values():
                for stop in path["stops"]:
                    if stop["sec"] > self.SIMULATE_TIME_DIFF:
                        stop["sec"] -= self.SIMULATE_TIME_DIFF
            time.sleep(self.SIMULATE_RATE)

    def start_simulate(self):
        if self.SIMULATE_STOPPED:
            self.SIMULATE_STOPPED = False
            self.SIMULATE_THREAD.start()

    def stop_simulate(self):
        self.SIMULATE_STOPPED = True

    def get_simulated_info(self):
        return self.SIMULATED_BUSINFO

    def get_info(self):
        return self.BUSINFO

    def stop_get_next_bus(self, stopid: int, buses=1):
        stop = self.get_stop(stopid)
        path_info = self.get_path(stop["path_id"])
        if not path_info or "stops" not in path_info:
            return -1
        path = path_info["stops"]
        stopindex = stop["sequence"]
        stopsec = stop["sec"]
        lastsec = 999999
        if stopsec >= 0:
            for i in range(stopindex - 1, -1, -1):
                if path[i]["sec"] > lastsec:
                    buses -= 1
                    if buses == 0:
                        return stopsec + path[i]["sec"]
                    else:
                        stopsec += path[i]["sec"]
                lastsec = path[i]["sec"]
        return -1
