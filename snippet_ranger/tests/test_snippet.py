import unittest

import asdf
import numpy as np
from bblfsh.github.com.bblfsh.sdk.uast.generated_pb2 import Node

from modelforge import split_strings
from snippet_ranger.models.snippet import Snippet
from snippet_ranger.tests import models


def validate_asdf_file(obj, filename):
    data = asdf.open(filename)
    obj.assertIn("meta", data.tree)
    obj.assertIn("filenames", data.tree)
    obj.assertIn("sources", data.tree)
    obj.assertIn("uasts", data.tree)
    obj.assertIn("repository", data.tree)
    obj.assertIn("positions", data.tree)
    Node.FromString(split_strings(data.tree["uasts"])[0])
    obj.assertEqual(data.tree["sources"]["lengths"].shape[0],
                    data.tree["uasts"]["lengths"].shape[0])
    obj.assertEqual(0, len(data.tree["meta"]["dependencies"]))
    obj.assertEqual(data.tree["meta"]["model"], "snippet")


class TestSnippet(unittest.TestCase):
    def setUp(self):
        self.model = Snippet().load(source=models.SNIPPET)

    def assert_np_arrays(self, arr1, arr2):
        self.assertEquals(type(arr1), np.ndarray)
        self.assertEquals(type(arr2), np.ndarray)
        self.assertTrue(np.all(arr1 == arr2))

    def test_item(self):
        model_item = self.model[0]
        self.assertEqual(len(model_item), 4)
        self.assertEqual(model_item[0], "example.py")
        self.assertEqual(type(model_item[1]), Node)
        self.assertEqual(model_item[2],
                         "def f():\n    f2()\n    f2()\n    f3()\n    f1()\n    f3()\n    f3()")
        self.assert_np_arrays(model_item[3], np.array([4, 11]))

    def test_positions_start(self):
        self.assert_np_arrays(self.model.positions_start, np.array([4]))

    def test_positions_end(self):
        self.assert_np_arrays(self.model.positions_end, np.array([11]))

    def test_positions(self):
        self.assert_np_arrays(self.model.positions, np.array([[4, 11]]))


if __name__ == "__main__":
    unittest.main()
