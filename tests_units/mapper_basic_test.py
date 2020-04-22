from automapping import Mapper, PartialMap, Rename, BiMorph, NaturalCopy, AutoMap
from dataclasses import dataclass


@dataclass
class A:
    a_name: str = None
    number_a: int = None
    a: str = None
    b: str = None


@dataclass
class B:
    b_name: str = None
    number_b: int = None
    a: str = None
    b: str = None


def a_to_b(value):
    return value + 4


def b_to_a(value):
    return value - 4


def test_given_reverse_mapped_object_should_get_be_able_to_map_both_side_correctly():
    expected_mapped_object = B(b_name='Gabriel', number_b=30, a='a', b='b')
    expected_reverse_mapped_object = A(
        a_name='Gabriel', number_a=26, a='a', b='b')

    mapper = Mapper()
    mapper.add_mapper(PartialMap(A, B, [
        Rename('a_name', 'b_name'),
        BiMorph('number_a', 'number_b', a_to_b, b_to_a),
        NaturalCopy(['a', 'b'])
    ]))

    a = A(a_name='Gabriel', number_a=26, a='a', b='b')
    actual_object = mapper.map(a, B)
    actual_reverse_object = mapper.map(actual_object, A)

    assert actual_object == expected_mapped_object
    assert actual_reverse_object == expected_reverse_mapped_object


def test_given_basic_flat_mapping_automapper_should_discover_dataclass_mapping():
    expected_mapped_object = B(b_name='Gabriel', number_b=30, a='a', b='b')
    expected_reverse_mapped_object = A(
        a_name='Gabriel', number_a=26, a='a', b='b')

    mapper = Mapper()
    mapper.add_mapper(AutoMap(A, B, [
        Rename('a_name', 'b_name'),
        BiMorph('number_a', 'number_b', a_to_b, b_to_a),
    ]))

    a = A(a_name='Gabriel', number_a=26, a='a', b='b')
    actual_object = mapper.map(a, B)
    actual_reverse_object = mapper.map(actual_object, A)

    assert actual_object == expected_mapped_object
    assert actual_reverse_object == expected_reverse_mapped_object
