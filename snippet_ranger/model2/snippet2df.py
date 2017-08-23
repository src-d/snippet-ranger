import tempfile
from typing import Union

from ast2vec.model2.source2df import Uast2DocFreq, MergeDocFreq
from ast2vec.df import DocumentFrequencies
from modelforge import Model

from snippet_ranger.models.snippet import Snippet


class Snippet2DocFreq(Uast2DocFreq):
    MODEL_FROM_CLASS = Snippet
    MODEL_TO_CLASS = Snippet

    def convert_model(self, model: Model) -> Union[Model, None]:
        for uast in model.uasts:
            contained = set()
            for key in self._uast2bag.uast_to_bag(uast):
                contained.add(key)
            for word in contained:
                self._df[word] += 1
            self._docs += 1


def snippet2df_entry(args):
    converter = Snippet2DocFreq(num_processes=args.processes)
    with tempfile.TemporaryDirectory(dir=args.tmpdir, prefix="snippet2df") as tmpdir:
        converter.convert(args.input, tmpdir, pattern=args.filter)
        joiner = MergeDocFreq(num_processes=1)
        joiner.convert(tmpdir, args.output,
                       pattern="%s*.asdf" % DocumentFrequencies.NAME)
