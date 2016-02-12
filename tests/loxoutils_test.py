import unittest
from json import *
from loxoutils import *

class LoxoTest(unittest.TestCase):
    """TestCase for the API conversiontools module"""

    def meters_to_radians_test(self):
        """ Testing that meters correctly converts to radians """
        self.assertAlmostEqual(meters_to_radians(3500), 0.0004703595114532541)

    def get_WGS84_distance_test(self):
        """ Testing that distance calculations between WGS84 coordinates are correct """
        self.assertAlmostEqual(get_WGS84_distance(55.5, -0.5, 55.0, 0), 64105.67608673149)


if __name__ == '__main__':
    unittest.main()