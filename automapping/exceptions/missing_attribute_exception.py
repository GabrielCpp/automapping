
class MissingAttributeException(Exception):
    def __init__(self, attribute_name, target_type):
        Exception.__init__(self, 'Attribute {} is not member of {}'.format(
            attribute_name, target_type))
