# My code is shit.
# Bus session
from . import api
from datetime import datetime


class BusSession:
    def __init__(self, route_key, provider=api.Provider.TWN):
        super()
        self.BUSINFO = None
        self.LAST_UPDATE = 0
        self.ROUTE_KEY = route_key
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
