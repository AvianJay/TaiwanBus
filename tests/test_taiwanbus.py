import unittest
import taiwanbus


class TestTaiwanBus(unittest.TestCase):

    def test_taiwanbus(self):
        taiwanbus.api.update_database()
        data = taiwanbus.api.fetch_route(304030)
        self.assertIsInstance(data, list, "fetch_route() should return a list")


if __name__ == '__main__':
    unittest.main()
