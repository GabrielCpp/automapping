from typing import List, Type
from dataclasses import is_dataclass
from .abstractions import IMappingStep, IReverseMappingStep, IMappingBuilder, IMapper, IUpdater
from .updater import ObjectDictTypeUpdater
from .helpers import get_dataclass_field_type_by_name


class PartialMap(IMappingBuilder):
    def __init__(self, from_type, to_type, common_steps: List[IReverseMappingStep], forward_steps: List[IMappingStep] = None, backward_steps: List[IMappingStep] = None):
        self.from_type = from_type
        self.to_type = to_type
        self.common_steps = common_steps or []
        self.forward_steps = forward_steps or []
        self.backward_steps = backward_steps or []

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


class Rename(IReverseMappingStep):
    def __init__(self, from_member_name, to_member_name):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.from_member_name)
        updater.set_destination_attr(destination, self.to_member_name, value)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.to_member_name)
        updater.set_destination_attr(destination, self.from_member_name, value)


class BiMorph(IReverseMappingStep):
    def __init__(self, from_member_name, to_member_name, forward_mapper, reverse_mapper):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.forward_mapper = forward_mapper
        self.reverse_mapper = reverse_mapper

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.from_member_name)
        morphed_value = self.forward_mapper(value)
        updater.set_destination_attr(
            destination, self.to_member_name, morphed_value)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.to_member_name)
        morphed_value = self.reverse_mapper(value)
        updater.set_destination_attr(
            destination, self.from_member_name, morphed_value)


class NaturalCopy(IReverseMappingStep):
    def __init__(self, members):
        self.members = members

    @property
    def supported_members(self):
        return [
            (name, name) for name in members
        ]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        for memberName in self.members:
            value = updater.get_source_attr(source, memberName)
            updater.set_destination_attr(destination, memberName, value)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        return self.map_forward(source, destination, updater, mapper)


class NaturalCopyAllField(NaturalCopy):
    def __init__(self, dataclass_type: Type):
        assert is_dataclass(
            dataclass_type), 'Type {} must be dataclass'.format(dataclass_type)

        members = list(get_dataclass_field_type_by_name(dataclass_type).keys())

        NaturalCopy.__init__(self, members)


class SubListMapping(IReverseMappingStep):
    def __init__(self, from_member_name, source_type, to_member_name, destination_type, updater_Type=ObjectDictTypeUpdater):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.destination_type = destination_type
        self.source_type = source_type
        self.updater_Type = updater_Type

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        source_values = updater.get_source_attr(source, self.from_member_name)
        mapped_values = []

        for source_value in source_values:
            mapped_sub_object = mapper.map(
                source_value, self.destination_type, self.updater_Type)
            mapped_values.append(mapped_sub_object)

        updater.set_destination_attr(
            destination, self.to_member_name, mapped_values)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        source_values = updater.get_source_attr(source, self.to_member_name)
        mapped_values = []

        for source_value in source_values:
            mapped_sub_object = mapper.map(
                source_value, self.source_type, self.updater_Type)
            mapped_values.append(mapped_sub_object)

        updater.set_destination_attr(
            destination, self.from_member_name, mapped_values)


class SubMapping(IReverseMappingStep):
    def __init__(self, from_member_name, source_type, to_member_name, destination_type, updater_Type=ObjectDictTypeUpdater):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.destination_type = destination_type
        self.source_type = source_type
        self.updater_Type = updater_Type

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        sub_object = updater.get_source_attr(source, self.from_member_name)
        mapped_sub_object = None if sub_object is None else mapper.map(
            sub_object, self.destination_type, self.updater_Type)
        updater.set_destination_attr(
            destination, self.to_member_name, mapped_sub_object)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        sub_object = updater.get_source_attr(source, self.to_member_name)
        mapped_sub_object = None if sub_object is None else mapper.map(
            sub_object, self.source_type, self.updater_Type)
        updater.set_destination_attr(
            destination, self.from_member_name, mapped_sub_object)


class Morph(IMappingStep):
    def __init__(self, member_name, custom_value_creator):
        self.member_name = member_name
        self.custom_value_creator = custom_value_creator

    @property
    def supported_members(self):
        return []

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        mapped_value = self.custom_value_creator(source, updater)
        updater.set_destination_attr(
            destination, self.member_name, mapped_value)


class NaturalCopyWithFilter(IMappingStep):
    def __init__(self, dataclass_type: Type, should_ignore: callable):
        assert is_dataclass(
            dataclass_type), 'Type {} must be dataclass'.format(dataclass_type)

        self.should_ignore = should_ignore
        self.members = list(
            get_dataclass_field_type_by_name(dataclass_type).keys())

    @property
    def supported_members(self):
        return [(name, name) for name in self.members]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        for memberName in self.members:
            value = updater.get_source_attr(source, memberName)

            if self.should_ignore(value):
                continue

            updater.set_destination_attr(destination, memberName, value)


class Ignore(IMappingStep):
    def __init__(from_member_name, to_member_name):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name

    @property
    def supported_members(self):
        return [(self.from_member_name, self.to_member_name)]

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        pass
