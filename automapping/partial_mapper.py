from typing import List, Type
from .abstractions import IMappingStep, IReverseMappingStep, IMappingBuilder


class PartialMap(IMappingBuilder):
    def __init__(self, from_type, to_type, common_steps: List[IReverseMappingStep], forward_steps: List[IMappingStep] = None, backward_steps: List[IMappingStep] = None):
        self.from_type = from_type
        self.to_type = to_type
        self.common_steps = common_steps or []
        self.forward_steps = forward_steps or []
        self.backward_steps = backward_steps or []
        self._configure()

    def build(self, mapper):
        forward_instructions = [
            step.map_forward for step in self.common_steps
        ]

        for forward_step in self.forward_steps:
            forward_instructions.append(forward_step.map_forward)

        backward_instructions = [
            step.map_backward for step in self.common_steps
        ]

        for backward_step in self.backward_steps:
            backward_instructions.append(backward_step.map_forward)

        return [
            (self.from_type, self.to_type, forward_instructions),
            (self.to_type, self.from_type, backward_instructions)
        ]

    def _configure(self):
        for step in self.common_steps:
            step.configure(self.from_type, self.to_type)

        for step in self.forward_steps:
            step.configure(self.from_type, self.to_type)

        for step in self.backward_steps:
            step.configure(self.from_type, self.to_type)
