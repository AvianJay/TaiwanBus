# My code is shit.
# Custom exceptions for TaiwanBus.


class DatabaseNotFoundError(Exception):
    pass


class RouteNotFoundError(Exception):
    pass


class StopNotFoundError(Exception):
    pass