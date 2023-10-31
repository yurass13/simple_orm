from dataclasses import dataclass

from typing import TypeVar, Generic


M = TypeVar('M', bound='Model')

class ForeignKey(Generic[M]):
    # TODO need more info and checks                                                ????????
    def __init__(self, model:M) -> None:
        self._related_model = model

    def __repr__(self) -> str:
        return str(self._related_model.id)

# TODO try use metaclass instead of dataclass decorator                             IMPORTANT
# TODO try create a new solution based on Fields family and metaclass ModelCreator  FUTURE IDEA
@dataclass
class Model:
    id: int
