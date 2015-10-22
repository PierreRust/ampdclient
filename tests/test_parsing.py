import unittest
import ampdclient.client as c


# Test for parsing functions


class TestStatusParsing(unittest.TestCase):

    def test_parse_status(self):

        msg = ['1:a', '2: b', '3: c ']
        res = c.parse_status(msg)

        self.assertIn('1', res)
        self.assertIn('2', res)
        self.assertIn('3', res)

        self.assertEqual('a', res['1'])
        self.assertEqual('b', res['2'])
        self.assertEqual('c', res['3'])

    def test_parse_status2(self):

        msg = ['1:a:b:c']
        res = c.parse_status(msg)

        self.assertIn('1', res)

        self.assertEqual('a:b:c', res['1'])


class TestLsInfoParsing(unittest.TestCase):

    pass
