import enum
from typing import Any

from pydantic import BaseModel, field_validator, computed_field
from solara.lab import Ref

from cds_core.base_states import BaseMarker, BaseStageState, register_model


class Marker(BaseMarker):
    wwt_wait = enum.auto()
    exp_dat1 = enum.auto()
    tre_dat1 = enum.auto()  # MC tre-dat-mc1
    tre_dat2 = enum.auto()
    tre_dat3 = enum.auto()  # MC tre-dat-mc3
    rel_vel1 = enum.auto()  # MC galaxy-trend
    hub_exp1 = enum.auto()
    tre_lin1 = enum.auto()
    tre_lin2 = enum.auto()
    bes_fit1 = enum.auto()
    age_uni1 = enum.auto()
    hyp_gal1 = enum.auto()
    age_rac1 = enum.auto()
    age_uni2 = enum.auto()
    age_uni3 = enum.auto()
    age_uni4 = enum.auto()
    you_age1 = enum.auto()
    sho_est1 = enum.auto()
    sho_est2 = enum.auto()
    end_sta4 = (
        enum.auto()
    )  # This avoids the last guideline "next" being locked by the can_transition logic.


class HubbleSlideshow(BaseModel):
    step: int = 0
    max_step_completed: int = 0


@register_model("stage", "explore_data")
class ComponentState(BaseStageState):
    current_step: Marker = Marker.first()
    stage_id: str = "explore_data"
    show_hubble_slideshow_dialog: bool = False
    hubble_slideshow_finished: bool = False
    hubble_slideshow_state: HubbleSlideshow = HubbleSlideshow()
    draw_click_count: int = 0
    best_fit_click_count: int = 0
    best_fit_gal_vel: float = 100
    best_fit_gal_dist: float = 8000
    class_data_displayed: bool = False
    tre_data_mc1_answered: bool = False
    tre_data_mc3_answered: bool = False
    galaxy_trend_answered: bool = False

    _max_step: int = 0  # not included in model

    # computed fields are included in the model when serialized
    @computed_field
    @property
    def total_steps(self) -> int:
        # ignore the last marker, which is a dummy marker
        return len(Marker) - 1

    @field_validator("current_step", mode="before")
    def convert_int_to_enum(cls, v: Any) -> Marker:
        if isinstance(v, int):
            return Marker(v)
        return v

    @property
    def tre_dat2_gate(self) -> bool:
        return self.tre_data_mc1_answered

    @property
    def tre_dat3_gate(self) -> bool:
        return self.class_data_displayed

    @property
    def rel_vel1_gate(self) -> bool:
        return self.tre_data_mc3_answered

    @property
    def hub_exp1_gate(self) -> bool:
        return self.galaxy_trend_answered

    @property
    def tre_lin1_gate(self) -> bool:
        return self.hubble_slideshow_finished

    @property
    def bes_fit1_gate(self) -> bool:
        return self.draw_click_count > 0

    @property
    def age_uni1_gate(self) -> bool:
        return self.best_fit_click_count > 0

    # @property
    # def sho_est2_gate(self) -> bool:
    #     return LOCAL_STATE.value.question_completed("shortcoming-1") and LOCAL_STATE.value.question_completed("shortcoming-2")
