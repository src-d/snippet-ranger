import os
import logging

from ast2vec.bow import BOW
from ast2vec.model2.source2bow import UastModel2BOW, Uasts2BOW
from ast2vec.df import DocumentFrequencies
import numpy
from scipy.sparse import csr_matrix

from snippet_ranger.models.snippet import Snippet


class SnippetModel2BOW(UastModel2BOW):
    MODEL_FROM_CLASS = Snippet

    def convert_model(self, model: Snippet) -> BOW:
        # TODO(zurk): It is better to replace _uasts2bow in future.
        bags = [self._uasts2bow([uast]) for uast in model.uasts]
        data = list(zip(*[(bag_[x], i, x) for i, bag_ in enumerate(bags) for x in bag_]))
        matrix = csr_matrix((data[0], (data[1], data[2])),
                            shape=(len(bags), len(self._uasts2bow.vocabulary)),
                            dtype=numpy.float32)
        bow = BOW(log_level=logging.WARNING)
        bow.construct(repos=model.names, matrix=matrix, tokens=self._tokens)
        bow.meta["dependencies"] = [self._uasts2bow.docfreq]
        return bow


def snippet2bow_entry(args):
    df = DocumentFrequencies().load(args.docfreq)
    os.makedirs(args.output, exist_ok=True)
    converter = SnippetModel2BOW(args.vocabulary_size, df, num_processes=args.processes,
                                 overwrite_existing=args.overwrite_existing)
    converter.convert(args.input, args.output, pattern=args.filter)
