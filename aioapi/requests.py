class Request:
    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            self.__setattr__(key.lower().replace("-", "_"), value)