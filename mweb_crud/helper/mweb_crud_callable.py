from typing import Protocol
from mweb_orm import MWebBaseModel


class BeforeAfterSaveCallable(Protocol):
    def __call__(self, *, data: dict, model: MWebBaseModel) -> None: ...