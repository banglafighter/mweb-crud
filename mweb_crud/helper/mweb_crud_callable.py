from typing import Protocol
from mweb_orm import MWebBaseModel, MWebIDModel, MWebDatedModel, MWebModel


class BeforeAfterSaveCallable(Protocol):
    async def __call__(self, *, data: dict, model: MWebModel | MWebBaseModel | MWebIDModel | MWebDatedModel) -> None: ...


class BeforeAfterDeleteCallable(Protocol):
    async def __call__(self, *, record_id: int, existing_model: MWebModel | MWebBaseModel | MWebIDModel | MWebDatedModel) -> None: ...
