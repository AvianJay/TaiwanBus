import unittest
import taiwanbus
from taiwanbus.session import BusSession
import time


class TestTaiwanBus(unittest.TestCase):

    def test_database(self):
        taiwanbus.api.update_database()
        data = taiwanbus.api.fetch_route(304030)
        self.assertIsInstance(data, list, "fetch_route() should return a list")

    def test_session(self):
        taiwanbus.api.update_database()
        bus = BusSession(304030)
        bus.update()
        self.assertIsInstance(
            bus.get_info(),
            dict,
            "get_info() should return a dict"
        )
        bus.start_simulate()
        time.sleep(3)
        self.assertNotEqual(
            bus.get_info(),
            bus.get_simulated_info(),
            "Simulated data shouldn't equal"
        )
        bus.stop_simulate()


if __name__ == '__main__':
    unittest.main()
