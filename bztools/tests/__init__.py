import unittest

def all_tests():
    test_loader = unittest.TestLoader()
    return test_loader.discover('bztools.tests', pattern='test_*.py')
