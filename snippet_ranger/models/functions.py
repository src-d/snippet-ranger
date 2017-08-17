from ast2vec import Source


class Functions(Source):
    """
    Model for function from source-code.
    It is the same source model but have start and end line positions of function location in file.
    """

    def construct(self, repository, filenames, sources, uasts, positions_start, positions_end):
        super(Functions, self).construct(repository=repository, filenames=filenames,
                                         sources=sources, uasts=uasts)
        self._positions_start = positions_start
        self._positions_end = positions_end

    @property
    def positions_start(self):
        """
        Return start line position of function.
        """
        return self._positions_start

    @property
    def positions_end(self):
        """
        Return end line position of function.
        """
        return self._positions_end

    def _to_dict_to_save(self):
        save_dict = super(Functions, self)._to_dict_to_save()
        save_dict["positions_start"] = self._positions_start
        save_dict["positions_end"] = self._positions_end
        return save_dict
