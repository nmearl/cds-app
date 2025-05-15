import enum

from pydantic import BaseModel, computed_field
from solara.lab import Ref

from cds_core.base_states import BaseMarker, BaseStageState, register_model
from ...components import STAGE_2_SLIDESHOW_LENGTH


class Marker(BaseMarker):
    mea_dis1 = enum.auto()


class DistanceSlideshow(BaseModel):
    step: int = 0
    max_step_completed: int = 0


@register_model("stage", "distance_introduction")
class ComponentState(BaseStageState):
    current_step: Marker = Marker.mea_dis1
    stage_id: str = "distance_introduction"
    distance_slideshow_state: DistanceSlideshow = DistanceSlideshow()

    @computed_field
    @property
    def total_steps(self) -> int:
        return STAGE_2_SLIDESHOW_LENGTH

    @computed_field
    @property
    def progress(self) -> float:
        return (self.distance_slideshow_state.max_step_completed + 1) / self.total_steps
