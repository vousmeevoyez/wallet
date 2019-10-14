"""
    Base Factory
"""

class Factory:
    """ Factory """
    def __init__(self):
        self._creators = {}

    def register(self, type_, creator):
        """ register all known creator using this method """
        self._creators[type_] = creator

    def get(self, type_):
        """ get creator """
        creator = self._creators.get(type_)
        if not creator:
            raise ValueError(type_)
        return creator()