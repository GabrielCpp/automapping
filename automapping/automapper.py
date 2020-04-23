from typing import List
from abc import ABC, abstractmethod
from itertools import chain
from dataclasses import is_dataclass
from inspect import isabstract, isclass
from .abstractions import IMappingStep, IReverseMappingStep, IMappingBuilder, IMapper, IUpdater, ITypePatternMatching
from .helpers import get_dataclass_field_type_by_name
from .mapper_steps import Rename, SubMapping, SubListMapping
from .partial_mapper import PartialMap
from .updater import ObjectDictTypeUpdater, ObjectUpdater
from .exceptions import MissingMappingException


class MatchExactType(ITypePatternMatching):
    def is_matching(self, from_type, to_type):
        return (
            from_type == to_type
            and isclass(from_type)
            and issubclass(from_type, (str, int, float, dict, list, bool, set))
        )

    def create(self, from_name, to_name, from_type, to_type):
        return Rename(from_name, from_name)


class MatchSubMappableObject(ITypePatternMatching):
    def is_matching(self, from_type, to_type):
        return (
            (is_dataclass(from_type) or isabstract(from_type))
            and (is_dataclass(to_type) or isabstract(to_type))
        )

    def create(self, from_name, to_name, from_type, to_type):
        return SubMapping(from_name, to_name, from_type, to_type)


class MatchListType(ITypePatternMatching):
    def is_matching(self, from_type, to_type):
        if not hasattr(from_type, '__origin__') or not hasattr(to_type, '__origin__'):
            return False

        are_both_list = getattr(from_type, '__origin__') is list and getattr(
            to_type, '__origin__') is list

        if not are_both_list:
            return False

        from_list_element_type = getattr(from_type, '__args__')[0]

        if is_dataclass(from_list_element_type):
            return True

        to_list_element_type = getattr(to_type, '__args__')[0]

        return issubclass(from_list_element_type, (str, int, float, dict, list, bool, set)) and from_list_element_type is to_list_element_type

    def create(self, from_name, to_name, from_type, to_type):
        from_list_element_type = getattr(from_type, '__args__')[0]
        to_list_element_type = getattr(to_type, '__args__')[0]

        if is_dataclass(from_list_element_type):
            return SubListMapping(from_name, to_name, from_list_element_type, to_list_element_type, list_element_mapping_strategy=SubListMapping.MapWithMapper(ObjectDictTypeUpdater))

        return SubListMapping(from_name, to_name, from_list_element_type, to_list_element_type, list_element_mapping_strategy=SubListMapping.MapBytInitAsValue())


class AutoMap(IMappingBuilder):
    type_mapper_patterns = [
        MatchExactType(),
        MatchListType(),
        MatchSubMappableObject(),
    ]

    def __init__(
        self,
        from_type: type,
        to_type: type,
        common_steps: List[IReverseMappingStep] = None,
        forward_steps: List[IMappingStep] = None,
        reverse_steps: List[IMappingStep] = None,
        inspect_members=get_dataclass_field_type_by_name
    ):
        self.from_type = from_type
        self.to_type = to_type
        self.common_steps = common_steps or []
        self.forward_steps = forward_steps or []
        self.reverse_steps = reverse_steps or []
        self.inspect_members = inspect_members

    def build(self, mapper):
        from_members = self.inspect_members(self.from_type)
        source_member_names = set(from_members.keys())

        to_members = self.inspect_members(self.to_type)
        destination_member_names = set(to_members.keys())

        common_member_names = source_member_names.intersection(
            destination_member_names)

        common_steps = self._build_common_steps(
            common_member_names, from_members, to_members)

        missing_source_members = source_member_names - destination_member_names
        missing_destination_members = destination_member_names - source_member_names

        self._raise_exception_if_some_attributes_are_forgotten(
            self.forward_steps, missing_source_members, missing_destination_members)

        self._raise_exception_if_some_attributes_are_forgotten(
            self.reverse_steps, missing_source_members, missing_destination_members)

        return PartialMap(
            self.from_type,
            self.to_type,
            common_steps=[
                *common_steps,
                *self.common_steps
            ],
            forward_steps=self.forward_steps,
            backward_steps=self.reverse_steps
        ).build(mapper)

    def _build_common_steps(self, common_member_names, from_members, to_members):
        common_steps = []

        for name in common_member_names:
            mapping_step = None

            for step in self.common_steps:
                if (name, name) in step.supported_members:
                    continue

            for type_mapper_pattern in AutoMap.type_mapper_patterns:
                if type_mapper_pattern.is_matching(from_members[name], to_members[name]):
                    mapping_step = type_mapper_pattern.create(
                        name, name, from_members[name], to_members[name]
                    )

                    mapper_found = True
                    break

            if mapping_step is None:
                raise MissingMappingException(
                    'No mapper found for attribute {} of type {} -> {}'.format(name, from_members[name], to_members[name]))
            else:
                common_steps.append(mapping_step)

        return common_steps

    def _raise_exception_if_some_attributes_are_forgotten(self, steps, from_member_names, to_member_names):
        tagged_from_member_names = set()
        tagged_to_member_names = set()

        for step in chain(self.common_steps, steps):
            for from_name, to_name in step.supported_members:
                tagged_from_member_names.add(from_name)
                tagged_to_member_names.add(to_name)

        source_members_without_mapping = from_member_names - tagged_from_member_names

        if len(source_members_without_mapping) > 0:
            raise MissingMappingException('Missing mapping for members {} for type {}'.format(
                source_members_without_mapping, self.from_type))

        destination_members_without_mapping = to_member_names - tagged_to_member_names

        if len(destination_members_without_mapping) > 0:
            raise MissingMappingException('Missing mapping for members {} for type {}'.format(
                source_members_without_mapping, self.to_type))
