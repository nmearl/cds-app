import enum
from typing import Any, Optional

from pydantic import field_validator, Field, computed_field
from solara.lab import Ref

from cds_core.base_states import BaseMarker, BaseStageState, register_model


class Marker(BaseMarker):
    ang_siz1 = enum.auto()
    cho_row1 = enum.auto()
    ang_siz2 = enum.auto()
    ang_siz2b = enum.auto()
    ang_siz3 = enum.auto()
    ang_siz4 = enum.auto()
    ang_siz5 = enum.auto()
    est_dis1 = enum.auto()
    est_dis2 = enum.auto()
    est_dis3 = enum.auto()
    est_dis4 = enum.auto()
    dot_seq1 = enum.auto()
    dot_seq2 = enum.auto()  # MC ang_meas_consensus
    dot_seq3 = enum.auto()
    dot_seq4 = enum.auto()
    dot_seq4a = enum.auto()  # MC ang_meas_dist_relation
    ang_siz5a = enum.auto()
    # ang_siz6  = enum.auto() We skipped this in the voila version
    dot_seq5 = enum.auto()
    dot_seq5a = enum.auto()
    dot_seq5b = enum.auto()
    dot_seq5c = enum.auto()
    # dot_seq6  = enum.auto()	# MC ang_meas_consensus_2
    # dot_seq7 = enum.auto()
    rep_rem1 = enum.auto()
    fil_rem1 = enum.auto()
    end_sta3 = (
        enum.auto()
    )  # This guideline doesn't actually exist - just including it to allow an exit gate on the previous guideline.


@register_model("stage", "distance_measurements")
class ComponentState(BaseStageState):
    current_step: Marker = Marker.ang_siz1
    stage_id: str = "distance_measurements"

    example_angular_sizes_total: int = 0
    angular_sizes_total: int = 0
    dosdonts_tutorial_opened: bool = False
    selected_galaxy: dict = {}
    selected_example_galaxy: dict = {}
    show_ruler: bool = False
    meas_theta: float = 0.0
    ruler_click_count: int = 0
    n_meas: int = 0
    bad_measurement: bool = Field(False, exclude=True)
    distances_total: int = 0
    fill_est_dist_values: bool = False
    show_dotplot_lines: bool = True
    angular_size_line: Optional[float | int] = None
    distance_line: Optional[float | int] = None
    ang_meas_consensus_answered: bool = False
    ang_meas_dist_relation_answered: bool = False
    ang_meas_consensus_2_answered: bool = False
    wwt_ready: bool = Field(False, exclude=True)

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
    def cho_row1_gate(self) -> bool:
        return self.wwt_ready

    @property
    def ang_siz2_gate(self):
        return bool(self.selected_example_galaxy)

    @property
    def ang_siz4_gate(self):
        return self.ruler_click_count == 1

    @property
    def ang_siz5_gate(self):
        return self.n_meas > 0

    @property
    def dot_seq3_gate(self):
        return self.ang_meas_consensus_answered

    @property
    def ang_siz5a_gate(self):
        return self.ang_meas_consensus_answered

    @property
    def dot_seq7_gate(self):
        return self.ang_meas_consensus_2_answered

    @property
    def dot_seq5_gate(self):
        return bool(self.dosdonts_tutorial_opened)

    @property
    def fil_rem1_gate(self):
        return self.angular_sizes_total >= 5

    @property
    def end_sta3_gate(self):
        return self.distances_total >= 5
