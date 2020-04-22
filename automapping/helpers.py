from inspect import getmembers
from typing import get_type_hints
from dataclasses import fields
from .mapper import Mapper
from .abstractions import IMapper, IMappingBuilder


def get_dataclass_field_type_by_name(dataclass_type):
    resolved_hints = get_type_hints(dataclass_type)
    field_names = [field.name for field in fields(dataclass_type)]
    resolved_field_types = {name: resolved_hints[name] for name in field_names}
    return resolved_field_types


def add_all_mapper_from_module(mapper: Mapper, modules: list):
    for module in modules:
        members = getmembers(module)

        for (member_name, *other) in members:
            member = getattr(module, member_name)

            if issubclass(type(member), IMappingBuilder):
                mapper.add_mapper(member)

    return mapper


def map_to_type(mapper: IMapper, to_type, *args, **kargs):
    return lambda from_value: mapper.map(from_value, to_type, *args, **kargs)
