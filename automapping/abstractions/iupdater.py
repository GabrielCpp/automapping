from abc import ABC, abstractmethod


class IUpdater(ABC):
    @abstractmethod
    def set_destination_attr(self, target, member_name, value):
        pass

    @abstractmethod
    def get_source_attr(self, target, member_name):
        pass

    @abstractmethod
    def create(self, type):
        pass

    @abstractmethod
    def finalize(self, type, value):
        pass
