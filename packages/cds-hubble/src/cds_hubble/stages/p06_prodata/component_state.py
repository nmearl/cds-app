import enum
from typing import Any

from pydantic import field_validator
from solara.lab import Ref

from cds_core.base_states import BaseMarker, BaseStageState, register_model


class Marker(BaseMarker):
    pro_dat0 = enum.auto()
    pro_dat1 = enum.auto()
    pro_dat2 = enum.auto()
    # pro_dat3 = enum.auto()
    pro_dat4 = enum.auto()
    pro_dat5 = enum.auto()
    pro_dat6 = enum.auto()
    pro_dat7 = enum.auto()
    pro_dat8 = enum.auto()
    pro_dat9 = enum.auto()
    sto_fin1 = enum.auto()
    sto_fin2 = enum.auto()
    sto_fin3 = enum.auto()


@register_model("stage", "professional_data")
class ComponentState(BaseStageState):
    current_step: Marker = Marker.pro_dat0
    stage_id: str = "professional_data"
    pro_data_1_answered: bool = False
    pro_data_2_answered: bool = False
    pro_data_4_answered: bool = False
    pro_data_6_answered: bool = False
    pro_data_7_answered: bool = False
    pro_data_9_answered: bool = False

    # TODO: I don't think our_age is used anywhere
    our_age: float = 0
    class_age: float = 0

    ages_within: float = 0.15
    allow_too_close_correct: bool = True

    fit_line_shown: bool = False

    @field_validator("current_step", mode="before")
    def convert_int_to_enum(cls, v: Any) -> Marker:
        if isinstance(v, int):
            return Marker(v)
        return v

    @property
    def pro_dat2_gate(self) -> bool:
        return self.pro_data_1_answered

    @property
    def pro_dat4_gate(self) -> bool:
        return self.pro_data_2_answered

    @property
    def pro_dat5_gate(self) -> bool:
        return self.pro_data_4_answered

    @property
    def pro_dat7_gate(self) -> bool:
        return self.pro_data_6_answered

    @property
    def pro_dat8_gate(self) -> bool:
        return self.pro_data_7_answered

    # @property
    # def pro_dat9_gate(self) -> bool:
    #     return LOCAL_STATE.value.question_completed("prodata-reflect-8a") #and LOCAL_STATE.value.question_completed("prodata-reflect-8b") and LOCAL_STATE.value.question_completed("prodata-reflect-8c")

    @property
    def sto_fin1_gate(self) -> bool:
        return self.pro_data_9_answered
