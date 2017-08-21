import argparse
import logging
import sys

from modelforge.logs import setup_logging
from ast2vec.__main__ import one_arg_parser

from snippet_ranger.model2.source2func import source2func_entry
from snippet_ranger.librariesio_fetcher import dependent_reps_entry, LibrariesIOFetcher

def get_parser() -> argparse.ArgumentParser:
    """
    Create main parser.

    :return: Parser
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-level", default="INFO",
                        choices=logging._nameToLevel,
                        help="Logging verbosity.")

    # Create all common arguments

    model2input_arg = one_arg_parser(
        "input", help="Directory to scan recursively for asdf files.")

    process_arg = one_arg_parser(
        "-p", "--processes", type=int, default=0,
        help="Number of processes to use. 0 means CPU count.")

    filter_arg = one_arg_parser(
        "--filter", default="**/*.asdf", help="File name glob selector.")

    library_name_arg = one_arg_parser(
        "--library_name", help="Provide the name of the library.")

    # Create and construct subparsers

    subparsers = parser.add_subparsers(help="Commands", dest="command")

    source2func_parser = subparsers.add_parser(
        "source2func",
        help="Decompose source model to functions were specified library is used. It makes model "
             "entry from each function that uses library and produce one Function model from one "
             "Source model, but it has more entries because of decomposition.",
        parents=[model2input_arg, filter_arg, process_arg, library_name_arg])
    source2func_parser.set_defaults(handler=source2func_entry)
    source2func_parser.add_argument(
        "--library_source",
        help="Provide the source model of the library. "
             "You can build it via ast2vec repo2source call.")
    source2func_parser.add_argument("-o", "--output", help="Where to write decomposed models.")

    dependent_reps_parser = subparsers.add_parser(
        "dependent_reps",
        help="Create a list of repositories, that are dependent from some specified libraries "
             "using libraries.io dataset.")
    dependent_reps_parser.set_defaults(handler=dependent_reps_entry)
    group = dependent_reps_parser.add_argument_group("libraries")
    group_ex = group.add_mutually_exclusive_group(required=True)
    group_ex.add_argument(
        "--libraries_json",
        help="Provide the input file in json format. It should represent dictionary of library "
             "name, url pairs. You can specify empty url if you not sure. "
             "Excludes --libraries flag.")
    group_ex.add_argument(
        "--libraries", nargs="+",
        help="The name-url pair of the library in format <library name>:<library url>. You can "
             "specify empty url if you not sure. Excludes --libraries_json flag.")
    dependent_reps_parser.add_argument(
        '-o', '--output', required=True,
        help="Where to write the list of dependent repos links. Save location for urls. "
             "Specify folder if you have several libraries. Then urls will be stored in the file "
             "<library name>.txt . You can specify file, then all urls will be saved in one file.")
    dependent_reps_parser.add_argument(
        '--librariesio_data', required=True,
        help="Provide the path to libraries.io dataset.")
    dependent_reps_parser.add_argument(
        '--platform', default=LibrariesIOFetcher.DEFAULT_PLATFORM,
        help="The name of package manager.")

    return parser


def main():
    """
    Creates all the argparse-rs and invokes the function from set_defaults().

    :return: The result of the function from set_defaults().
    """

    parser = get_parser()
    args = parser.parse_args()
    args.log_level = logging._nameToLevel[args.log_level]
    setup_logging(args.log_level)
    try:
        handler = args.handler
    except AttributeError:
        def print_usage(_):
            parser.print_usage()

        handler = print_usage
    return handler(args)

if __name__ == "__main__":
    sys.exit(main())
