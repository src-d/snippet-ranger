import os
import re

from ast2vec.source import Source
from snippet_ranger.model2.base_decompose import Model2BaseDecompose
from snippet_ranger.models.functions import Functions
from snippet_ranger.utils import uast_role_nodes, has_import, uast_to_bag, get_func_names_bow


class Source2Func(Model2BaseDecompose):
    """
    Converter for source model decomposition to topic modeling documents or snippets.
    It makes document from each function that satisfies the rule in output_model_entry_criteria
    for every file that satisfies the rule in input_model_entry_criteria.
    """
    MODEL_FROM_CLASS = Source
    MODEL_TO_CLASS = Functions

    def __init__(self, libname, lib_funcs_bow=None, *args, **kwargs):
        """
        :param libname: Name of the library. All files without library usage are not handled.
        :param lib_funcs_bow: dictionary of functions (bag of words) which can be used from the \
            library. You can use just all function names or preprocess it somehow. For example, \
            remove functions that are common for language or internal functions.
        :param args: positional arguments to pass to :class:`Model2BaseDecompose`.
        :param kwargs: key arguments to pass to :class:`Model2BaseDecompose`.
        """
        super(Source2Func, self).__init__(*args, **kwargs)
        self.libname = libname
        self.lib_funcs_bow = lib_funcs_bow
        self.threshold = 0

    def input_model_entry_criteria(self, model_entry):
        """
        Input model entry filter criteria. Filter all files that are not use the library.

        :param model_entry: entry of Source model.
        :return: library usage indicator.
        """
        filename, uast, source = model_entry
        return has_import(self.libname, uast)

    def decompose_model_entry(self, model_from, model_entry):
        """
        Iterator of parameters for __init__ of Function model decomposed from Source entry.

        :param model_from: Full Source model.
        :param model_entry: Current Source model entry.
        :return: parameters for Function model __init__.
        """
        filename, uast, source = model_entry
        func_nodes = uast_role_nodes(uast, "FUNCTION_DECLARATION")
        for func_node in func_nodes:
            pos_start, pos_end = func_node.start_position.line-1, func_node.end_position.line
            func_source = '\n'.join(source.splitlines()[pos_start:pos_end])
            yield model_from.repository, filename, func_source, func_node, pos_start, pos_end

    def output_model_entry_criteria(self, model_entry):
        """
        Output model entry filter criteria. Filter all Function model entries that has no calls
        from the library bag of words are not use the library.

        :param model_entry: Source model entry.
        :return: library functions usage indicator.
        """
        func_node = model_entry[3]
        func_names = uast_to_bag(func_node, role="CALL_CALLEE")
        func_names = uast_to_bag(func_node, func_names, role="CALL")

        common = set(self.lib_funcs_bow) & set(func_names)
        if len(common) > self.threshold:
            return True
        return False


def process_lib_functions(functions_bow):
    """
    Clear function bag of words from bad function names. Specific for Python.
    Removes internal functions and test functions.
    """
    exclude = ["^\_\w*", '^test\w*']
    pattern = re.compile("(" + "|".join(exclude) + ")")
    clear_functions_bow = {k: v for k, v in functions_bow.items() if not pattern.match(k)}
    return clear_functions_bow


def source2func_entry(args):
    lib_model = Source().load(args.library_source)
    functions_bow = get_func_names_bow(lib_model)
    functions_bow = process_lib_functions(functions_bow)

    os.makedirs(args.output, exist_ok=True)
    converter = Source2Func(args.library_name, functions_bow, log_level=args.log_level,
                            num_processes=args.processes)
    converter.convert(args.input, args.output, pattern=args.filter)
