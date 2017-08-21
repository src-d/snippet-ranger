import argparse
import logging
import os
import unittest
import tempfile

import asdf
from ast2vec import Source
from bblfsh.github.com.bblfsh.sdk.uast.generated_pb2 import Node
from modelforge import split_strings

from snippet_ranger.model2.source2func import Source2Func
from snippet_ranger.model2.source2func import process_lib_functions, source2func_entry
from snippet_ranger.models.snippet import Snippet
from snippet_ranger.tests import models
from snippet_ranger.utils import get_func_names_bow


def validate_asdf_file(obj, filename):
    data = asdf.open(filename)
    obj.assertIn("meta", data.tree)
    obj.assertIn("filenames", data.tree)
    obj.assertIn("sources", data.tree)
    obj.assertIn("uasts", data.tree)
    obj.assertIn("repository", data.tree)
    obj.assertIn("positions_start", data.tree)
    obj.assertIn("positions_end", data.tree)
    Node.FromString(split_strings(data.tree["uasts"])[0])
    obj.assertEqual(data.tree["sources"]["lengths"].shape[0],
                    data.tree["uasts"]["lengths"].shape[0])
    obj.assertEqual(0, len(data.tree["meta"]["dependencies"]))
    obj.assertEqual(data.tree["meta"]["model"], "source")


class Source2FuncTests(unittest.TestCase):
    def test_get_func_names_bow(self):
        in_bow = {
            '_xxx': 1,
            'xxx': 1,
            '_yyy': 1,
            'yyy': 1,
            'test_x': 1,
            'test_y': 1,
        }
        out_bow = process_lib_functions(in_bow)
        self.assertEqual(out_bow, {'xxx': 1, 'yyy': 1})

    def test_convert_model(self):
        from bblfsh.github.com.bblfsh.sdk.uast.generated_pb2 import Node

        lib_model = Source().load(models.TEST_LIB)
        functions_bow = get_func_names_bow(lib_model)
        functions_bow = process_lib_functions(functions_bow)
        self.assertEqual(functions_bow, {'f1': 1, 'f2': 1, "f3": 1, "f35": 1})

        repo_model = Source().load(models.TEST_REPO)

        converter = Source2Func(models.LIB_NAME, functions_bow)
        functons = converter.convert_model(repo_model)

        self.assertEqual(len(functons), 1)
        functon_obj = functons[0]
        self.assertEqual(functon_obj[0], "example.py")
        self.assertEqual(type(functon_obj[1]), Node)
        self.assertEqual(functon_obj[2],
                         "def f():\n    f2()\n    f2()\n    f3()\n    f1()\n    f3()\n    f3()")
        self.assertEqual(functon_obj[3], 3)
        self.assertEqual(functon_obj[4], 10)

    def test_source2func_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            args = argparse.Namespace(library_source=models.TEST_LIB,
                                      library_name=models.LIB_NAME,
                                      input=models.DATA_DIR,
                                      output=tmpdir,
                                      filter="**/*.asdf",
                                      log_level=logging.INFO,
                                      processes=1)
            source2func_entry(args)
            validate_asdf_file(self, os.path.join(tmpdir, "test_repo.asdf"))


if __name__ == '__main__':
    unittest.main()
