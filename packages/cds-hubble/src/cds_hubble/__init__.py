import importlib
import pkgutil
from typing import Union, Annotated

from pydantic import Field
from solara.lab import Ref
from solara.lab import Ref

from cds_core.base_states import (
    STAGE_REGISTRY,
    STORY_REGISTRY,
    BaseAppState,
    BaseStoryState,
)
from cds_core.logger import setup_logger
from .remote import LOCAL_API
from .story_state import LocalState

logger = setup_logger("CDS-HUBBLE INITIALIZE")


StageStateUnionFactory = lambda: Annotated[
    Union[tuple(STAGE_REGISTRY.values())], Field(discriminator="type")
]

StoryStateUnionFactory = lambda: Annotated[
    Union[tuple(STORY_REGISTRY.values())], Field(discriminator="type")
]


def import_all_stage_modules():
    import cds_hubble.stages

    for _, module_name, _ in pkgutil.iter_modules(cds_hubble.stages.__path__):
        importlib.import_module(f"cds_hubble.stages.{module_name}.component_state")


import_all_stage_modules()

# Patch the base models
BaseStoryState.patch_union_type()
BaseAppState.patch_union_type()
