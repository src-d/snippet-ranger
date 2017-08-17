from collections import defaultdict

from ast2vec import Source
from ast2vec.bblfsh_roles import get_role_id


def uast_to_bag(uast, bag=None, role="SIMPLE_IDENTIFIER"):
    """
    Convert UAST to bag of words for certain role.

    :param uast: Uast to process.
    :param bag: Specify existing bag of words if you want to update it.
    :param role: Role or list of roles to get from uast and convert to bag of words.
    :return: bag of words for tokens of nodes.
    """
    if bag is None:
        bag = defaultdict(int)
    # (Konst) Can be optimised if we need
    for node in uast_role_nodes(uast, roles=role):
        if node.token != "":
            bag[node.token] += 1
    return bag


def uast_role_nodes(uast, roles=None):
    """
    Filter UAST by provided roles and iterate trough corresponding nodes of uast.

    :param uast:
    :param roles: roles to filter.
    :return: iterator trough corresponding nodes.
    """
    if roles is None:
        roles = ["SIMPLE_IDENTIFIER"]
    if isinstance(roles, str):
        role_ids = [get_role_id(roles)]
    elif isinstance(roles, int):
        role_ids = [roles]
    elif isinstance(roles, list):
        role_ids = [get_role_id(r) if isinstance(r, str) else r for r in roles]
    else:
        raise TypeError()
    stack = [uast]
    while stack:
        node = stack.pop(0)
        for role_id in role_ids:
            if role_id in node.roles:
                yield node
                break
        stack.extend(node.children)


def _iter_imports(uast):
    """
    Itrernal helper function to iterate through uast's imports
    """
    for n in uast_role_nodes(uast, ["IMPORT_PATH", "IMPORT_ALIAS"]):
        for x in n.token.split('.'):
            yield x


def get_imports(uast):
    """
    Return all module imports from the uast.
    It is specific for Python because imports should be splited by dot.

    :param uast:
    :return: set of import names
    """
    return set([x for x in _iter_imports(uast)])


def has_import(libname, uast) -> bool:
    """
    Check `libname` import in the uast

    :param libname: name of library to check
    :param uast:
    :return:
    """
    for imp in _iter_imports(uast):
        if imp == libname:
            return True
    return False


def get_func_names_bow(source_model: Source) -> dict:
    """
    Returns bag of words for functions in all Source model.

    :param source_model: Source model
    :return: dictionary with words as keys
    """
    func_names = None
    for filename, uast, source in source_model:
        func_names = uast_to_bag(uast, func_names, "FUNCTION_DECLARATION_NAME")
    return func_names
