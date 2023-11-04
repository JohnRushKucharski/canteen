'''Tests the data module.'''

import unittest

from src.data import Log
#from src.node import Inflow

class TestLog(unittest.TestCase):
    '''Test the log class.'''
    def test_default_data(self):
        '''Test that the default data is an empty list.'''
        self.assertEqual([], Log().data)

    def test_default_csv_path(self):
        '''Test that the default csv path is an empty string.'''
        self.assertEqual('', Log().csv_path)

    def test_default_data_headers(self):
        '''Test that the default data headers is an empty tuple.'''
        self.assertEqual((), Log().data_headers)

# class TestLogger(unittest.TestCase):
#     '''Tests the logger decorator.'''

#     def test_logger(self):
#         '''Test that the logger decorator stores the output of a function.'''
#         log = Log()
#         inflow = Inflow(data=[1, 2, 3])
#         # pylint: disable=unexpected-keyword-arg
#         inflow.send(log=log)
#         inflow.send(log=log)
#         inflow.send(log=log)
#         self.assertEqual([1, 2, 3], log.data)
