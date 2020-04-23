from dataclasses import dataclass
from typing import List
from automapping import Mapper, AutoMap, Rename, ObjectDictTypeUpdater


@dataclass
class InnerA:
    number: int
    list_of_values: List[str]
    untyped_list: list


@dataclass
class A:
    name: str
    id_a: int
    inner: InnerA


@dataclass
class InnerB:
    number: int
    list_of_values: List[str]
    untyped_list: list


@dataclass
class B:
    name: str
    id_b: int
    inner: InnerB


def test_given_():
    input_a = A(name='Paul', id_a=6, inner=InnerA(
        number=10, list_of_values=['a', 'b'], untyped_list=[1, True]))

    expected_b = B(name='Paul', id_b=6, inner=InnerB(
        number=10, list_of_values=['a', 'b'], untyped_list=[1, True]))

    mapper = Mapper()
    mapper.add_mapper(AutoMap(A, B, [
        Rename('id_a', 'id_b')
    ]))

    mapper.add_mapper(AutoMap(InnerA, InnerB))

    actual_b = mapper.map(input_a, B, ObjectDictTypeUpdater)

    assert actual_b == expected_b
