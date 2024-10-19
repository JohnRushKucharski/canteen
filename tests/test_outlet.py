'''
Test the reservoir module.
'''
import unittest

from plugins.outlets.basic import BasicOutlet
from canteen.outlet import OUTLETS, ReleaseRange, load_outlet_plugins, outlet_factory, format_outlets

class TestOutletPlugins(unittest.TestCase):
    '''Tests functionality of plugin arthetecture for outlets'''
    def test_load_outlet_plugins_registers_basic_outlet(self):
        '''test'''
        load_outlet_plugins()
        self.assertDictEqual({'BasicOutlet': BasicOutlet}, OUTLETS)
    def test_outlet_factory_returns_basic_outlet(self):
        '''test'''
        load_outlet_plugins()
        outlet = outlet_factory('BasicOutlet')
        self.assertIsInstance(outlet, BasicOutlet)

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

class TestFormatOutlets(unittest.TestCase):
    '''Test the format_outlets function.'''
    def test_format_outlets_sort_by_location(self):
        '''Test the format_outlets function.'''
        outlets = [BasicOutlet(location=1), BasicOutlet(location=2)]
        formatted_outlets = format_outlets(outlets)
        self.assertEqual([outlet.name for outlet in formatted_outlets],
                         ['outlet@2', 'outlet@1'], )

    def test_format_outlets_renaming_basic_case(self):
        '''Test the format_outlets function.'''
        outlets = [BasicOutlet(), BasicOutlet()]
        formatted_outlets = format_outlets(outlets)
        self.assertEqual([outlet.name for outlet in formatted_outlets],
                         ['outlet1@0.0', 'outlet2@0.0'])

    def test_fomat_outlets_rename_not_required(self):
        '''Test the format_outlets function when renaming is not required.'''
        outlets = [BasicOutlet(name='outlet1'), BasicOutlet(name='outlet2')]
        formatted_outlets = format_outlets(outlets)
        self.assertEqual([outlet.name for outlet in formatted_outlets], ['outlet1', 'outlet2'])

    def test_format_outlets_2pass_rename(self):
        '''Test the format_outlets function with a 2-pass rename.'''
        outlets = [BasicOutlet(name='', location=1), BasicOutlet(name=''), BasicOutlet()]
        formatted_outlets = format_outlets(outlets)
        self.assertEqual([outlet.name for outlet in formatted_outlets],
                         ['outlet@1', 'outlet1@0.0', 'outlet2@0.0'])
