import json
import logging
import os

import pandas as pd

from ast2vec.pickleable_logger import PickleableLogger
from modelforge.progress_bar import progress_bar

dependencies_filename = 'repository_dependencies-1.0.0-2017-06-15.csv'
repos_filename = 'repositories-1.0.0-2017-06-15.csv'
projects_filename = 'projects-1.0.0-2017-06-15.csv'


class LibIO(PickleableLogger):
    """
    Class to get useful information from Libraries.io dataset
    """

    DEFAULT_PLATFORM = 'Pypi'
    CHUNKSIZE = 1000000

    def __init__(self, librariesio_path, log_level=logging.INFO):
        """
        :param librariesio_path: Path to a folder where librariesio dataset is stored.
        :param log_level: log level of current class.
        """
        super(LibIO, self).__init__(log_level=log_level)
        self._librariesio_path = librariesio_path
        self._host2link = {'GitHub': 'github.com/',
                           'GitLab': 'gitlab.com/',
                           'Bitbucket': 'bitbucket.org/', }

    def get_lib_info(self, libraries, platform, save_to=None):
        """
        Creates pandas dataframe with information about ecosystems from specified platform
        from Libraries.io.

        :param libraries: Dict of names and urls to repo or homepage. You can use empty url if \
            you do not sure about the link.
        :param platform: Package platform where the library is published. You can use empty \
            platform if you do not sure about a link.
        :param save_to: Path to save pandas dataframe with all information about libraries
        :return: Pandas dataframe with all information about libraries.
        """

        libs_info = pd.DataFrame()
        projects_path = os.path.join(self._librariesio_path, projects_filename)
        self._log.info("Looking for libraries info...")
        for chunk in pd.read_csv(projects_path, chunksize=LibIO.CHUNKSIZE,
                                              index_col=False, dtype=object):
            for lib_name in libraries:
                indxs = (chunk["Name"] == lib_name)
                if platform != "":
                    indxs = indxs & (chunk["Platform"] == platform)
                if libraries[lib_name] != "":
                    indxs = indxs & ((chunk["Repository URL"] == libraries[lib_name]) |
                                     pd.isnull(chunk["Repository URL"]))
                    res = chunk[indxs]
                    if len(res) > 0:
                        self._log.info("%s library entry is found!", lib_name)
                    libs_info = pd.concat([libs_info, res])
                    if save_to:
                        libs_info.to_csv(save_to, index=False)

        return libs_info

    def get_dependent_reps(self, libs_info, save_to=None):
        """
        Creates pandas dataframe with all information about dependent repositories from libraries.

        :param libs_info: Pandas dataframe with all information about libraries.
        :param save_to: Path to save pandas dataframe with all information about libraries if you \
            want to save it.
        :return: Pandas dataframe with all information about dependent repositories.
        """
        self._log.info("Creating list of dependent repos...")
        if hasattr(libs_info['ID'], "tolist"):
            eco_id2name = dict(zip(libs_info['ID'].tolist(), libs_info['Name'].tolist()))
        else:
            eco_id2name = {libs_info['ID']: libs_info['Name']}
        pd_result = []
        dependencies_path = os.path.join(self._librariesio_path, dependencies_filename)
        for chunk in progress_bar(pd.read_csv(dependencies_path, chunksize=LibIO.CHUNKSIZE,
                                              index_col=False), self._log, expected_size=100):
            for eco_id in eco_id2name:
                res = chunk[chunk["Dependency Project ID"] == int(eco_id)]
                if len(res) > 0:
                    pd_result.append(res)

        pd_result = pd.concat(pd_result)
        pd_result['url'] = 'https://' + \
                           pd_result['Host Type'].map(self._host2link) + \
                           pd_result['Repository Name with Owner']
        if save_to:
            pd_result.to_csv(save_to, index=False)

        return pd_result

    def save_urls_only(self, dependent_reps, libs_info, save_to):
        """
        Create urls for repositories from dependent_reps for libraries from libs_info.

        :param dependent_reps: Pandas dataframe with information about dependent repositories \
            from libraries in libs_info dataframe.
        :param libs_info: Pandas dataframe with all information about libraries.
        :param save_to: Save location for urls. Specify folder if you have several libraries. \
            Then urls will be stored in the file <library name>.txt . You can specify file, then
            all urls will be saved in one file.
        """
        if not os.path.isdir(save_to) and os.path.exists(save_to):
            os.remove(save_to)
        for i, eco in libs_info.iterrows():
            lib_id = int(eco['ID'])
            lib_name = eco['Name']
            cur_dependent_reps = dependent_reps[dependent_reps['Dependency Project ID'] == lib_id]
            res = cur_dependent_reps['url'].tolist()
            res = list(set(res))

            if os.path.isdir(save_to):
                save_path = os.path.join(save_to, lib_name + '.txt')
            else:
                save_path = save_to

            with open(save_path, 'a') as f:
                for line in res:
                    f.write(line + '\n')

    def get_dependent_rep_urls(self, libraries, platform, output):
        """
        Extract and save dependent urls of dependent repositories.

        :param libraries: Dict of names and urls to repo or homepage. You can use empty url if \
            you do not sure about the link.
        :param platform: Package platform where the library is published. You can use empty
        platform if you do not sure about a link.
        :param output: Save location for urls. Specify folder if you have several libraries. \
            Then urls will be stored in the file <library name>.txt . You can specify file, then
            all urls will be saved in one file.
        :return:
        """
        ecosystem_info = self.get_lib_info(libraries, platform)
        dependent_reps = self.get_dependent_reps(ecosystem_info)
        self.save_urls_only(dependent_reps, ecosystem_info, save_to=output)

    def _get_log_name(self):
        return 'LibIO'


def dependent_reps_entry(args):
    if args.libraries:
        libraries = dict(lib.split(":", maxsplit=1) for lib in args.libraries)
    else:
        libraries = json.load(open(args.libraries_json))

    libio = LibIO(args.librariesio_data, args.log_level)
    libio.get_dependent_rep_urls(libraries, args.platform, args.output)
