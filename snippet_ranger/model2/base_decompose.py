from typing import Iterable

from modelforge import Model
from ast2vec import Model2Base


class Model2BaseDecompose(Model2Base):
    """
    Class for model entry filtration, decomposition, filtration again and merging.
    Produce exactly one model from one, but it has more entries because of decomposition.
    MODEL_FROM should be iterable.
    """
    def __init__(self, *args, **kwargs):
        super(Model2BaseDecompose, self).__init__(*args, **kwargs)

    def filter_input_model_entry(self, model: Model) -> Iterable:
        """
        Filter input model entry by criteria in input_model_entry_criteria
        :return:
        """
        return filter(self.input_model_entry_criteria, model)

    def input_model_entry_criteria(self, model_entry):
        """
        Criteria for input model filtering.
        No filtration by default
        :param model_entry: model entry
        :return:
        """
        return True

    def filter_output_model_entry(self, model: Model) -> Iterable:
        """
        Filter output model entry by criteria in output_model_entry_criteria
        :return:
        """
        return filter(self.output_model_entry_criteria, model)

    def output_model_entry_criteria(self, model_entry):
        """
        Criteria for input model filtering.
        No filtration by default
        :param model_entry: model entry
        :return:
        """
        return True

    def convert_model(self, model_from: Model) -> Model:
        result = []
        for model_entry in self.filter_input_model_entry(iter(model_from)):
            out_model_part = self.decompose_model_entry(model_from, model_entry)
            for out_model_entry in self.filter_output_model_entry(out_model_part):
                result.append(out_model_entry)
        out_model = self.MODEL_TO_CLASS()
        if result:
            out_model.construct(*zip(*result))
        else:
            raise ValueError("All functions are filtered and you get empty model.")
        return out_model

    def decompose_model_entry(self, model_from, model_entry) -> iter:
        """
        This function must be implemented in the child classes.

        :param model_from: full input model instance.
        :param model_entry: The current model entry instance to decompose.
        :return: List of parameters for __init__ of new converted model instances.
        """
        raise NotImplementedError
