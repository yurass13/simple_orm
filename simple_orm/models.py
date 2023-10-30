from dataclasses import dataclass

from typing import TypeVar, Generic


M = TypeVar('M', bound='ModelBase')

class ForeignKey(Generic[M]):
    # TODO need more info and checks
    def __init__(self, model:M) -> None:
        self._related_model = model

    def __repr__(self) -> str:
        return str(self._related_model.id)


@dataclass
class ModelBase:
    id: int
