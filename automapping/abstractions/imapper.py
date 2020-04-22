from abc import ABC, abstractmethod


class IMapper(ABC):
    @abstractmethod
    def map(self, from_value, to_type, updater_type=None):
        pass
