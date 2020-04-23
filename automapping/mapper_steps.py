from dataclasses import is_dataclass
from typing import Type
from .abstractions import IMappingStep, IReverseMappingStep, IMapper, IUpdater
from .updater import ObjectDictTypeUpdater
from .helpers import get_dataclass_field_type_by_name
from .exceptions import InvalidMappingException


class Rename(IReverseMappingStep):
    def __init__(self, from_member_name, to_member_name):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.source_type = None
        self.destination_type = None

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def configure(self, source_type: Type, destination_type: Type) -> None:
        assert is_dataclass(source_type)
        assert is_dataclass(destination_type)

        self.source_type = get_dataclass_field_type_by_name(
            source_type).get(self.from_member_name)

        self.destination_type = get_dataclass_field_type_by_name(
            destination_type).get(self.to_member_name)

        if self.source_type is None:
            raise MissingAttributeException(
                self.from_member_name, self.source_type)

        if self.destination_type is None:
            raise MissingAttributeException(
                self.to_member_name, self.destination_type)

        if self.source_type != self.destination_type:
            raise InvalidMappingException('Source type and destination type must be the same but received {} and {}'.format(
                self.source_type, self.destination_type))

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.from_member_name)
        new_value = self.destination_type(value)
        updater.set_destination_attr(
            destination, self.to_member_name, new_value)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        value = updater.get_source_attr(source, self.to_member_name)
        new_value = self.source_type(value)
        updater.set_destination_attr(
            destination, self.from_member_name, new_value)


class NaturalCopy(IReverseMappingStep):
    def __init__(self, members):
        self.members = members
        self._source_dataclass_fields = None
        self._target_dataclass_fields = None

    @property
    def supported_members(self):
        return [
            (name, name) for name in members
        ]

    def configure(self, source_type: Type, destination_type: Type) -> None:
        assert is_dataclass(source_type)
        assert is_dataclass(destination_type)

        self._source_dataclass_fields = get_dataclass_field_type_by_name(
            source_type)

        self._target_dataclass_fields = get_dataclass_field_type_by_name(
            destination_type)

        for member_name in self.members:
            attr_source_type = self._source_dataclass_fields.get(member_name)
            attr_destination_type = self._target_dataclass_fields.get(
                member_name)

            if attr_source_type is None:
                raise MissingAttributeException(member_name, attr_source_type)

            if attr_destination_type is None:
                raise MissingAttributeException(
                    member_name, attr_destination_type)

            if attr_source_type != attr_destination_type:
                raise InvalidMappingException('Source type and destination type for {} must be the same but received {} and {}'.format(
                    member_name, attr_source_type, attr_destination_type))

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        for member_name in self.members:
            value = updater.get_source_attr(source, member_name)
            new_value = self._target_dataclass_fields[member_name](value)
            updater.set_destination_attr(destination, member_name, new_value)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        for member_name in self.members:
            value = updater.get_source_attr(source, member_name)
            new_value = self._source_dataclass_fields[member_name](value)
            updater.set_destination_attr(destination, member_name, new_value)


class NaturalCopyAllField(NaturalCopy):
    def __init__(self):
        NaturalCopy.__init__(self, [])

    def configure(self, source_type: Type, destination_type: Type) -> None:
        assert is_dataclass(source_type)
        assert is_dataclass(destination_type)

        source_member_names = set(
            get_dataclass_field_type_by_name(source_type).keys())

        destination_member_names = set(
            get_dataclass_field_type_by_name(destination_type).keys())

        self.members = source_member_names.intersection(
            destination_member_names)

        NaturalCopy.configure(self, source_type, destination_type)


class SubListMapping(IReverseMappingStep):
    class MapWithMapper:
        def __init__(self, updater_type=ObjectDictTypeUpdater):
            self.updater_type = ObjectDictTypeUpdater

        def __call__(self, mapper: IMapper, source_value, destination_type):
            mapped_sub_object = mapper.map(
                source_value, destination_type, self.updater_type)

            return mapped_sub_object

    class MapBytInitAsValue:
        def __call__(self, mapper: IMapper, source_value, destination_type):
            return destination_type(source_value)

    def __init__(self, from_member_name, to_member_name, source_type, destination_type, list_element_mapping_strategy=MapWithMapper()):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.destination_type = destination_type
        self.source_type = source_type
        self.list_element_mapping_strategy = list_element_mapping_strategy

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def configure(self, source_type: Type, destination_type: Type) -> None:
        pass

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        source_values = updater.get_source_attr(source, self.from_member_name)
        mapped_values = []

        for source_value in source_values:
            mapped_sub_object = self.list_element_mapping_strategy(
                mapper, source_value, self.destination_type)
            mapped_values.append(mapped_sub_object)

        updater.set_destination_attr(
            destination, self.to_member_name, mapped_values)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        source_values = updater.get_source_attr(source, self.to_member_name)
        mapped_values = []

        for source_value in source_values:
            mapped_sub_object = self.list_element_mapping_strategy(
                mapper, source_value, self.source_type)
            mapped_values.append(mapped_sub_object)

        updater.set_destination_attr(
            destination, self.from_member_name, mapped_values)


class SubMapping(IReverseMappingStep):
    def __init__(self, from_member_name, to_member_name, source_type, destination_type, updater_type=ObjectDictTypeUpdater):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name
        self.destination_type = destination_type
        self.source_type = source_type
        self.updater_type = updater_type

    @property
    def supported_members(self):
        return [
            (self.from_member_name, self.to_member_name)
        ]

    def configure(self, source_type: Type, destination_type: Type) -> None:
        pass

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        sub_object = updater.get_source_attr(source, self.from_member_name)
        mapped_sub_object = None if sub_object is None else mapper.map(
            sub_object, self.destination_type, self.updater_type)
        updater.set_destination_attr(
            destination, self.to_member_name, mapped_sub_object)

    def map_backward(self, source, destination, updater: IUpdater, mapper: IMapper):
        sub_object = updater.get_source_attr(source, self.to_member_name)
        mapped_sub_object = None if sub_object is None else mapper.map(
            sub_object, self.source_type, self.updater_type)
        updater.set_destination_attr(
            destination, self.from_member_name, mapped_sub_object)


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

    def configure(self, source_type: Type, destination_type: Type) -> None:
        assert is_dataclass(source_type)
        assert is_dataclass(destination_type)

        attr_source_type = get_dataclass_field_type_by_name(
            source_type).get(self.from_member_name)

        if attr_source_type is None:
            raise MissingAttributeException(
                self.from_member_name, attr_source_type)

        attr_destination_type = get_dataclass_field_type_by_name(
            destination_type).get(self.to_member_name)

        if attr_destination_type is None:
            raise MissingAttributeException(
                self.to_member_name, attr_destination_type)

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


class Morph(IMappingStep):
    def __init__(self, member_name, custom_value_creator):
        self.member_name = member_name
        self.custom_value_creator = custom_value_creator

    @property
    def supported_members(self):
        return []

    def configure(self, source_type: Type, destination_type: Type) -> None:
        pass

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        mapped_value = self.custom_value_creator(source, updater)
        updater.set_destination_attr(
            destination, self.member_name, mapped_value)


class Ignore(IMappingStep):
    def __init__(from_member_name, to_member_name):
        self.from_member_name = from_member_name
        self.to_member_name = to_member_name

    @property
    def supported_members(self):
        return [(self.from_member_name, self.to_member_name)]

    def configure(self, source_type: Type, destination_type: Type) -> None:
        pass

    def map_forward(self, source, destination, updater: IUpdater, mapper: IMapper):
        pass
