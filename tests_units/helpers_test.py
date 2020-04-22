import tests_units.fixtures.mapper_module_fixture as mapper_module_fixture
from automapping import add_all_mapper_from_module, Mapper
from dataclasses import dataclass
from typing import List
from automapping import get_dataclass_field_type_by_name


def test_given_class_should_gather_type_by_member_name():
    @dataclass
    class Test:
        a: int
        b: List[str]

    expected_members = {
        'a': int,
        'b': List[str]
    }

    actual_members = get_dataclass_field_type_by_name(Test)

    assert actual_members == expected_members


def test_given_module_mapper_import_defined_mappers():
    mapper = Mapper()
    add_all_mapper_from_module(mapper, [
        mapper_module_fixture
    ])

    actual_mapping_existance = mapper.has_mapping(dict, list)

    assert actual_mapping_existance == True
