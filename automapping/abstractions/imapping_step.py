from abc import ABC, abstractmethod
from typing import Type
from .imapper import IMapper
from .iupdater import IUpdater


class IMappingStep(ABC):
    @property
    @abstractmethod
    def supported_members(self):
        pass

    @abstractmethod
    def configure(source_type: Type, destination_type: Type) -> None:
        pass

    @abstractmethod
    def map_forward(self, source_value, destination_value, updater: IUpdater, mapper: IMapper) -> list:
        pass


class IReverseMappingStep(IMappingStep):
    @abstractmethod
    def map_backward(self, source_value, destination_value, updater: IUpdater, mapper: IMapper) -> list:
        pass
