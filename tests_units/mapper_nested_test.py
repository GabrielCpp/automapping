from dataclasses import dataclass
from automapping import Mapper, PartialMap, Rename, BiMorph, NaturalCopy, SubListMapping, SubMapping, Morph, ObjectDictDictUpdater, ObjectDictTypeUpdater


@dataclass
class PersonDto:
    response_id: str
    name: str
    age: int
    siblings: list
    mother: 'PersonDto'


@dataclass
class PersonDomain:
    name: str
    age: int
    siblings: list
    mother: 'PersonDomain'


def test_given_nested_object_mapped_to_similar_object_should_match_all_common_properties():
    expect_object = PersonDomain(
        name='Gabriel',
        age=26,
        siblings=[
            PersonDomain(name='Sarah', age=23, siblings=[], mother=None)
        ],
        mother=PersonDomain(name='Huguette', age=61, siblings=[], mother=None)
    )

    input_object = PersonDto(
        response_id='12345',
        name='Gabriel',
        age=26,
        siblings=[
            PersonDto(response_id='12345', name='Sarah',
                      age=23, siblings=[], mother=None)
        ],
        mother=PersonDto(response_id='12345', name='Huguette',
                         age=61, siblings=[], mother=None)
    )

    mapper = Mapper()
    mapper.add_mapper(PartialMap(PersonDto, PersonDomain, [
        NaturalCopy(['age', 'name']),
        SubListMapping('siblings', 'siblings', PersonDto, PersonDomain),
        SubMapping('mother',  'mother', PersonDto, PersonDomain)
    ]))

    actual_object = mapper.map(
        input_object, PersonDomain, updater_type=ObjectDictTypeUpdater)

    assert actual_object == expect_object


def test_given_nested_object_mapped_to_similar_object_should_match_all_common_properties_when_mapped_backward():
    expect_object = PersonDto(
        response_id='12345',
        name='Gabriel',
        age=26,
        siblings=[
            PersonDto(response_id='12345', name='Sarah',
                      age=23, siblings=[], mother=None)
        ],
        mother=PersonDto(response_id='12345', name='Huguette',
                         age=61, siblings=[], mother=None)
    )

    input_object = PersonDomain(
        name='Gabriel',
        age=26,
        siblings=[
            PersonDomain(name='Sarah', age=23, siblings=[], mother=None)
        ],
        mother=PersonDomain(name='Huguette', age=61, siblings=[], mother=None)
    )

    mapper = Mapper()
    mapper.add_mapper(PartialMap(PersonDto, PersonDomain, [
        NaturalCopy(['age', 'name']),
        SubListMapping('siblings', 'siblings', PersonDto, PersonDomain),
        SubMapping('mother', 'mother', PersonDto, PersonDomain)
    ], backward_steps=[
        Morph('response_id', lambda source, updater: '12345')
    ]))

    actual_object = mapper.map(
        input_object, PersonDto, updater_type=ObjectDictTypeUpdater)

    assert actual_object == expect_object
