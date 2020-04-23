from abc import ABC, abstractmethod


class ITypePatternMatching(ABC):
    @abstractmethod
    def is_matching(self, from_type, to_type):
        pass

    @abstractmethod
    def create(self, from_name, to_name, from_type, to_type):
        pass
