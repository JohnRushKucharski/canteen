'''Tests for the Asset module.'''
import unittest

from canteen.asset import DepreciationParameters, Asset

class TestFt(unittest.TestCase):
    '''
    Test the ft function in the Depreciation Parameters module.

    Evaluates portion value of asset at time t.
    '''
    def test_default_build_ft_linear_shape(self):
        '''Test the build_ft function.'''
        ft = DepreciationParameters().build_ft()
        self.assertEqual(ft(0), 1.00)
        self.assertEqual(ft(1), 0.99)
        self.assertEqual(ft(5), 0.95)
        self.assertEqual(ft(50), 0.50)
        self.assertEqual(ft(100), 0.0)
        self.assertEqual(ft(101), 0.0)

    def test_default_build_ft_concave_shape_faster_than_linear(self):
        '''Test the build_ft function.'''
        ft = DepreciationParameters(k=1.1).build_ft()
        self.assertEqual(ft(0), 1.00)
        self.assertLess(ft(1), 0.99)
        self.assertLess(ft(5), 0.95)
        self.assertLess(ft(50), 0.50)
        self.assertEqual(ft(100), 0.0)
        self.assertEqual(ft(101), 0.0)

    def test_default_build_ft_convex_shape_slower_than_linear(self):
        '''Test the build_ft function.'''
        ft = DepreciationParameters(k=0.9).build_ft()
        self.assertEqual(ft(0), 1.0)
        self.assertGreater(ft(1), 0.99)
        self.assertGreater(ft(5), 0.95)
        self.assertGreater(ft(50), 0.50)
        self.assertEqual(ft(100), 0.0)
        self.assertEqual(ft(101), 0.0)

class TestInverseFt(unittest.TestCase):
    '''
    Test the inverse_ft function in the Depreciation Parameters module.

    Evaluates time t at which portion value of asset is f(t).
    '''
    def test_default_build_inverse_ft_linear_shape(self):
        '''Test the build_inverse_ft function.'''
        inverse_ft = DepreciationParameters().build_inverse_ft()
        self.assertEqual(inverse_ft(1.0), 0)
        self.assertAlmostEqual(inverse_ft(0.99), 1)
        self.assertEqual(inverse_ft(0.5), 50)
        self.assertEqual(inverse_ft(0.0), 100)

    def test_build_inverse_ft_concave_shape_faster_than_linear(self):
        '''Test the build_inverse_ft function.'''
        inverse_ft = DepreciationParameters(k=1.1).build_inverse_ft()
        self.assertEqual(inverse_ft(1.0), 0)
        self.assertGreater(inverse_ft(0.99), 1)
        self.assertGreater(inverse_ft(0.50), 50)
        self.assertGreater(inverse_ft(0.25), 75)
        self.assertGreater(inverse_ft(0.1), 90)
        self.assertEqual(inverse_ft(0.0), 100)

    def test_build_inverse_ft_convex_shape_slower_than_linear(self):
        '''Test the build_inverse_ft function.'''
        inverse_ft = DepreciationParameters(k=0.9).build_inverse_ft()
        self.assertEqual(inverse_ft(1.0), 0)
        self.assertLess(inverse_ft(0.99), 1)
        self.assertLess(inverse_ft(0.50), 50)
        self.assertLess(inverse_ft(0.25), 75)
        self.assertLess(inverse_ft(0.1), 90)
        self.assertEqual(inverse_ft(0.0), 100)

class TestAsset(unittest.TestCase):
    '''
    Test the Asset module.
    '''
    def test_portion_remaining(self):
        '''Test the portion_remaining function.'''
        asset = Asset()
        self.assertEqual(asset.portion_remaining, 1.0)
        asset = Asset(value=50)
        self.assertEqual(asset.portion_remaining, 0.5)
        asset = Asset(value=0)
        self.assertEqual(asset.portion_remaining, 0.0)

    def test_remaining_life(self):
        '''Test the remaining_life function.'''
        asset = Asset()
        self.assertEqual(asset.remaining_life, 100)
        asset = Asset(value=50)
        self.assertEqual(asset.remaining_life, 50)
        asset = Asset(value=0)
        self.assertEqual(asset.remaining_life, 0)
