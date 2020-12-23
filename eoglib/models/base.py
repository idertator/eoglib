class Model:

    def __init__(
        self,
        **parameters
    ):
        assert isinstance(parameters, dict)
        self._parameters = parameters

    @property
    def parameters(self) -> dict:
        return self._parameters

    @parameters.setter
    def parameters(self, value: dict):
        assert isinstance(value, dict)
        self._parameters = value

    @classmethod
    def from_json(cls, json: dict):
        parameters = json.pop('parameters')
        return cls(**parameters)

    def to_json(self) -> dict:
        return {
            'parameters': self._parameters,
        }
