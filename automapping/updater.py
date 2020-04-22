from .abstractions import IUpdater


class ObjectDictTypeUpdater(IUpdater):
    def set_destination_attr(self, target, member_name, value):
        target[member_name] = value

    def get_source_attr(self, target, member_name):
        return getattr(target, member_name)

    def create(self, type_t):
        return {}

    def finalize(self, type_t, value):
        return type_t(**value)


class DictDictTypeUpdater(IUpdater):
    def set_destination_attr(self, target, member_name, value):
        target[member_name] = value

    def get_source_attr(self, target, member_name):
        return target[member_name]

    def create(self, type_t):
        return {}

    def finalize(self, type_t, value):
        return type_t(**value)


class ObjectDictDictUpdater(IUpdater):
    def set_destination_attr(self, target, member_name, value):
        target[member_name] = value

    def get_source_attr(self, target, member_name):
        return getattr(target, member_name)

    def create(self, type_t):
        return {}

    def finalize(self, type_t, value):
        return value


class ObjectUpdater(IUpdater):
    def set_destination_attr(self, target, member_name, value):
        setattr(target, member_name, value)

    def get_source_attr(self, target, member_name):
        return getattr(target, member_name)

    def create(self, type_t):
        return type_t()

    def finalize(self, type_t, value):
        return value
