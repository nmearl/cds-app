import enum

from pydantic import BaseModel, computed_field
from solara.lab import Ref

from cds_core.base_states import BaseMarker, BaseStageState, register_model
from ...components import INTRO_SLIDESHOW_LENGTH


class Marker(BaseMarker):
    int_sli1 = enum.auto()
    end_intro1 = enum.auto()


class IntroSlideshow(BaseModel):
    step: int = 0
    max_step_completed: int = 0


@register_model("stage", "introduction")
class ComponentState(BaseStageState):
    current_step: Marker = Marker.int_sli1
    stage_id: str = "introduction"
    intro_slideshow_state: IntroSlideshow = IntroSlideshow()

    _max_step: int = 0  # not included in model

    @computed_field
    @property
    def total_steps(self) -> int:
        return INTRO_SLIDESHOW_LENGTH

    @computed_field
    @property
    def max_step(self) -> int:
        self._max_step = max(self.intro_slideshow_state.step, self._max_step)
        return self._max_step

    @computed_field
    @property
    def progress(self) -> float:
        return (self.intro_slideshow_state.max_step_completed + 1) / self.total_steps
