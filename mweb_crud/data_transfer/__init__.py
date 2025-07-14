from .base_dto import (
    MWebBaseDTO,
    MWebMasterDTO,
    MWebDTO,
    MWebDatedDTO,
    MWebIDDTO
)

from .df_helper import BaseEnum

from marshmallow import (
    validates_schema as marsh_validates_schema,
    pre_dump as marsh_pre_dump,
    post_load as marsh_post_load,
    post_dump as marsh_post_dump,
    pre_load as marsh_pre_load,
)

validates_schema = marsh_validates_schema,
pre_dump = marsh_pre_dump,
post_load = marsh_post_load,
post_dump = marsh_post_dump,
pre_load = marsh_pre_load,

__all__ = [
    "MWebBaseDTO",
    "MWebMasterDTO",
    "MWebDTO",
    "MWebDatedDTO",
    "MWebIDDTO",
    "validates_schema",
    "pre_dump",
    "post_load",
    "post_dump",
    "pre_load",
]
