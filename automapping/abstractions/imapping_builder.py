from abc import ABC, abstractmethod
from .imapper import IMapper


class IMappingBuilder(ABC):
    @abstractmethod
    def build(self, mapper: IMapper):
        pass
