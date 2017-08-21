from ast2vec import Source


class Snippet(Source):
    """
    This model can store code snippets. In general, code snippet is any part of source code file.
    For example, function declaration is a code snippet. So, this class is the same as source model
    but have start and end line positions of snippet location in file.
    You can use :class:`Source2Function` transformer to create function snippets from source model.
    """

    def construct(self, repository, filenames, sources, uasts, positions_start, positions_end):
        super(Snippet, self).construct(repository=repository, filenames=filenames,
                                       sources=sources, uasts=uasts)
        self._positions_start = positions_start
        self._positions_end = positions_end

    @property
    def positions_start(self):
        """
        Return start line position of snippets.
        """
        return self._positions_start

    @property
    def positions_end(self):
        """
        Return end line position of snippets.
        """
        return self._positions_end

    def __getitem__(self, item):
        """
        Returns file name, uast, source code, start and end position for the given snippet index.

        :param item: Snippet index.
        :return: file name, source code, uast, start and end position
        """
        return super(Snippet, self).__getitem__(item) + \
            (self._positions_start[item], self._positions_end[item])

    def _to_dict_to_save(self):
        save_dict = super(Snippet, self)._to_dict_to_save()
        save_dict["positions_start"] = self._positions_start
        save_dict["positions_end"] = self._positions_end
        return save_dict
