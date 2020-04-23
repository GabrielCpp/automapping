Python 3.7 helper tool to work with mapping of dataclasses.



It allow automapping a dataclass attributes

```python
from automapping import Mapper, Rename

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

mapper = Mapper()
mapper.add_mapper(AutoMap(A, B, [
    Rename('id_a', 'id_b')
]))
mapper.add_mapper(AutoMap(InnerA, InnerB))


input_a = A(name='Paul', id_a=6, inner=InnerA(
    number=10, list_of_values=['a', 'b'], untyped_list=[1, True]))
result = mapper.map(input_a, B, ObjectDictTypeUpdater)
print(result) # B(name='Paul', id_b=6, inner=InnerB(number=10, list_of_values=['a', 'b'], untyped_list=[1, True]))

```





