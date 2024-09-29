'''
Test the reservoir module.
'''
import unittest

from canteen.reservoir import ReleaseRange, BasicOutlet

class TestBasicOutlet(unittest.TestCase):
    '''Test the BasicOutlet class.'''
    def test_expected_range_below_location(self):
        '''Test when the fill state is below the outlet location.'''
        outlet = BasicOutlet()
        self.assertEqual(outlet.operations(0), ReleaseRange(0, 0))

    def test_expected_range_above_location(self):
        '''Test when the fill state is above the outlet location.'''
        outlet = BasicOutlet()
        self.assertEqual(outlet.operations(20), ReleaseRange(0, 20))

    def test_expected_range_above_location_with_design_range(self):
        '''Test when the fill state is above the outlet location with a design range.'''
        outlet = BasicOutlet(design_range=ReleaseRange(5, 15))
        self.assertEqual(outlet.operations(20), ReleaseRange(5, 15))

    def test_expected_range_below_location_with_design_range(self):
        '''Test when the fill state is below the outlet location with a design range.'''
        outlet = BasicOutlet(design_range=ReleaseRange(5, 15))
        self.assertEqual(outlet.operations(0), ReleaseRange(0, 0))

    def test_expected_range_above_location_with_location(self):
        '''Test when the fill state is above the outlet location with a location.'''
        outlet = BasicOutlet(location=5)
        self.assertEqual(outlet.operations(20), ReleaseRange(0, 15))
