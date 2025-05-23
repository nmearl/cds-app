import solara
from solara import Reactive
from solara.toestand import Ref
import reacton.ipyvuetify as rv

from ..remote import BaseAPI

from .refresh_button import RefreshButton
from ..base_states import BaseStoryState, BaseState, BaseAppState

from enum import Enum
from functools import partial
from typing import Type, TypeVar


BS = TypeVar("BS", bound=BaseState, covariant=True)
BLS = TypeVar("BLS", bound=BaseStoryState, covariant=True)
BAS = TypeVar("BAS", bound=BaseAppState, covariant=True)


@solara.component
def MarkerSelector(marker_cls: Type[Enum], component_state: Reactive[BS]):

    markers_list = [marker.name for marker in marker_cls]

    with solara.Row():
        with solara.Column():
            rv.Select(
                label="Select Marker",
                v_model=component_state.value.current_step.name,
                on_v_model=lambda value: Ref(component_state.fields.current_step).set(
                    marker_cls[value]
                ),
                items=markers_list,
            )


@solara.component
def FieldList(component_state: Reactive[BS]):

    def _reactive_set_field(field, value):
        Ref(getattr(component_state.fields, field)).set(value)

    field_names = [
        {
            "name": name,
            "type": info.annotation,
        }
        for name, info in component_state.value.model_fields.items()
    ]

    for field in field_names:
        field_type = field["type"]
        field_name = field["name"]
        field_value = getattr(component_state.value, field_name)
        field_ref = Ref(getattr(component_state.fields, field_name))
        if field_name == "current_step":
            continue
        elif field_type == bool:
            rv.Switch(
                label=field_name,
                v_model=field_ref.value,
                on_v_model=partial(field_ref.set),
            )
        elif field_type == Reactive[str]:
            solara.InputText(label=field_name, value=field_ref)
        elif field_type == Reactive[int]:
            solara.InputInt(label=field_name, value=field_ref)
        elif field_type == Reactive[float]:
            solara.InputFloat(label=field_name, value=field_ref)
        elif isinstance(field_value, Reactive):
            # just print it out
            solara.Markdown(f"{field_name}: {field_value.value}")
        elif isinstance(field_value, BaseState):
            # recursively call this function
            with solara.Card(
                style="border-radius: 5px; border: 2px solid #40ECB2; max-width: 400px"
            ):
                with solara.Details(summary=f"{field_name}:"):
                    FieldList(Ref(field_value))
        elif isinstance(field_value, Reactive) and isinstance(
            field_value.value, BaseState
        ):
            # recursively call this function
            with solara.Card(
                style="border-radius: 5px; border: 2px solid #40ECB2; max-width: 400px"
            ):
                with solara.Details(summary=f"{field_name}:"):
                    FieldList(field_value)
        else:
            solara.Markdown(f"{field_name}: {field_value}")


@solara.component
def StateEditor(
    marker_cls: Type[Enum],
    component_state: Reactive[BS],
    local_state: Reactive[BLS],
    global_state: Reactive[BAS],
    api: BaseAPI,
    show_all: bool = True,
):
    show_dialog, set_show_dialog = solara.use_state(False)
    with solara.Card(
        style="border-radius: 5px; border: 2px solid #EC407A; max-width: 400px"
    ):
        if show_all:
            with solara.Row():
                with solara.Column():
                    solara.Markdown(f"**User id:** {global_state.value.student.id}")
                with solara.Column():
                    next_marker = (
                        marker_cls(component_state.value.current_step.value + 1)
                        if component_state.value.current_step is not marker_cls.last()
                        else None
                    )
                    current = f"**Current**: {component_state.value.current_step.name} ( {component_state.value.current_step.value})"
                    if next_marker:
                        solara.Markdown(
                            current
                            + "\n"
                            + f" **Next**: {next_marker.name} ( {next_marker.value})"
                        )
                    else:
                        solara.Markdown(current)

        with solara.Row():
            MarkerSelector(marker_cls, component_state)
            if show_all:
                with solara.Column():
                    solara.Button(
                        children="Edit State",
                        on_click=lambda: set_show_dialog(not show_dialog),
                    )
            with solara.Column():
                with rv.Dialog(
                    v_model=show_dialog, on_v_model=set_show_dialog, max_width="500px"
                ):
                    with solara.Card():
                        with solara.Column():
                            FieldList(component_state)

        if show_all:
            with solara.Row():
                RefreshButton(
                    event_before_refresh=lambda _: api.delete_stage_state(
                        global_state, local_state, component_state
                    ),
                    button_text="Reset Stage State",
                )
