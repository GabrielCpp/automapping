from collections import defaultdict
from .abstractions import IMapper
from .updater import ObjectDictTypeUpdater, ObjectUpdater, ObjectDictDictUpdater, DictDictTypeUpdater


class Mapper(IMapper):
    class MapperStepProxy(IMapper):
        def __init__(self, real_mapper):
            self.mapper = real_mapper

        def map(self, from_value, to_type, updater_type=ObjectUpdater):
            return self.mapper.map(from_value, to_type, updater_type)

    def __init__(self):
        self.mappings = defaultdict(lambda: defaultdict(lambda: None))
        self.updaters = {
            ObjectDictDictUpdater: ObjectDictDictUpdater(),
            ObjectDictTypeUpdater: ObjectDictTypeUpdater(),
            ObjectUpdater: ObjectUpdater(),
            DictDictTypeUpdater: DictDictTypeUpdater()
        }

    def has_mapping(self, from_type, to_type):
        return not self.mappings[from_type][to_type] is None

    def add_mapper(self, mapper):
        mappings = mapper.build(self)

        for (fromType, toType, instructions) in mappings:
            self.mappings[fromType][toType] = instructions

    def map(self, from_value, to_type, updater_type=ObjectUpdater):
        steps = self._get_mapping(type(from_value), to_type)
        updater = self.updaters[updater_type]
        to_value = updater.create(to_type)
        mapper_proxy = Mapper.MapperStepProxy(self)

        for step in steps:
            step(
                from_value,
                to_value,
                updater,
                mapper_proxy
            )

        return updater.finalize(to_type, to_value)

    def _get_mapping(self, from_type, to_type):
        steps = self.mappings[from_type][to_type]

        if steps is None:
            raise Exception('Not mapping for {} to type {}'.format(
                self._get_name(from_type), self._get_name(to_type)))

        return steps

    def _get_name(self, obj):
        if hasattr(obj, '__name__'):
            return obj.__name__

        return str(obj)
