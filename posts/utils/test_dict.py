from django.test import TestCase
from .dict import without


class DictUtilsTestCase(TestCase):

    def test_without_removes_list_of_keys(self):
        """
        """
        result = without({"x": 1, "y": 2, "z": 3}, ['x', 'z'])
        self.assertEqual(result, {"y": 2})
