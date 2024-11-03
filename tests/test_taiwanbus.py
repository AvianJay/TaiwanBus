import asyncio
import unittest
import taiwanbus


class TestTaiwanBus(unittest.TestCase):

    def test_taiwanbus(self):
        taiwanbus.update_database()
        data = asyncio.run(taiwanbus.fetch_route(304030))
        self.assertIsInstance(data, list, "fetch_route() should return a list")


if __name__ == '__main__':
    unittest.main()
