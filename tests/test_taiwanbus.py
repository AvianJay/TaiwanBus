import asyncio
import unittest
import taiwanbus


class TestTaiwanBus(unittest.TestCase):

    def test_taiwanbus(self):
        taiwanbus.updatedb()
        data = youbike.getdata()
        self.assertIsInstance(data, list, "getdata() should return a list")


if __name__ == '__main__':
    unittest.main()
