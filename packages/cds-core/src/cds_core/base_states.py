import enum
import os
from typing import (
    Dict,
    TypeVar,
    ClassVar,
    Type,
    Optional,
    Annotated,
    Union,
    Literal,
    Callable,
)

from pydantic import BaseModel, Field, computed_field
from solara import Reactive
from solara.toestand import Ref

from cds_core.logger import setup_logger

logger = setup_logger("STATE")

debug_mode_init = os.getenv("CDS_DEBUG_MODE", "false").strip().lower() == "true"

logger.info(f"Debug mode is {'enabled' if debug_mode_init else 'disabled'}. ")


# Create separate registries
STAGE_REGISTRY: Dict[str, Type["BaseStageState"]] = {}
STORY_REGISTRY: Dict[str, Type["BaseStoryState"]] = {}


def register_model(state_type: str, state_name: str):
    if state_type == "stage":

        def decorator(cls: Type["BaseStageState"]) -> Type["BaseStageState"]:
            if "type" not in cls.__annotations__:
                cls.__annotations__["type"] = Literal[state_name]
                setattr(cls, "type", state_name)

            STAGE_REGISTRY[state_name] = cls
            return cls

    elif state_type == "story":

        def decorator(cls: Type["BaseStoryState"]) -> Type["BaseStoryState"]:
            if "type" not in cls.__annotations__:
                cls.__annotations__["type"] = Literal[state_name]
                setattr(cls, "type", state_name)

            STORY_REGISTRY[state_name] = cls
            return cls

    else:
        raise ValueError(
            f"Invalid state type: {state_type}. Must be 'stage' or 'story'."
        )

    return decorator


class BaseState(BaseModel):
    def as_dict(self):
        return self.model_dump()

    def update(self, new):
        return self.model_copy(update=new)


class BaseMarker(enum.Enum):

    def __lt__(self, other):
        if type(other) is type(self):
            return self.value < other.value
        return NotImplemented

    def __gt__(self, other):
        if type(other) is type(self):
            return self.value > other.value
        return NotImplemented

    # We don't want to just do e.g. `not self.__lt__(other)` because __lt__ might return NotImplemented.
    # NotImplemented is truthy so `not NotImplemented` is False (with a `DeprecationWarning`)
    # but I think we want to actually return NotImplemented (for consistency with above)
    # and not a coerced boolean
    def __ge__(self, other):
        if type(other) is type(self):
            return self.value >= other.value
        return NotImplemented

    def __le__(self, other):
        if type(other) is type(self):
            return self.value <= other.value
        return NotImplemented

    @classmethod
    def next(cls, step):
        return cls(step.value + 1)

    @classmethod
    def previous(cls, step):
        return cls(step.value - 1)

    @classmethod
    def first(cls):
        return cls(1)

    @classmethod
    def last(cls):
        return cls(len(cls))

    def is_between(self, start: "BaseMarker", end: "BaseMarker"):
        return start.value <= self.value <= end.value

    @classmethod
    # Check if the given marker is at the specified marker or earlier.
    def is_at_or_before(cls, marker: "BaseMarker", end: "BaseMarker"):
        return marker.value <= end.value


BaseStageStateT = TypeVar("BaseStageStateT", bound="BaseStageState")


def transition_to(
    component_state: Reactive[BaseStageStateT], step: BaseMarker, force=False
):
    if component_state.value.can_transition(step) or force:
        Ref(component_state.fields.current_step).set(step)
    else:
        logger.warning(
            f"Conditions not met to transition from "
            f"{component_state.value.current_step.name} to {step.name}."
        )


def transition_next(component_state: Reactive[BaseStageStateT], force=False):
    next_marker = component_state.value.current_step.next(
        component_state.value.current_step
    )
    transition_to(component_state, next_marker, force=force)


def transition_previous(component_state: Reactive[BaseStageStateT], force=True):
    previous_marker = component_state.value.current_step.previous(
        component_state.value.current_step
    )
    transition_to(component_state, previous_marker, force=force)


class BaseStageState(BaseState):
    current_step: BaseMarker
    stage_id: str
    _max_step: int = 0  # not included in model

    # computed fields are included in the model when serialized
    @computed_field
    @property
    def max_step(self) -> int:
        self._max_step = max(self.current_step.value, self._max_step)  # type: ignore
        return self._max_step

    @computed_field
    @property
    def total_steps(self) -> int:
        # compute the total number of steps based on current_steps
        # this may be overridden in subclasses
        return len(self.current_step.__class__)

    @computed_field
    @property
    def progress(self) -> float:
        # first enum value is always 1
        first = 1  # self.current_step.first().value
        # last = self.total_steps + first #self.current_step.last().value
        current = self.current_step.value
        return (current - first + 1) / self.total_steps

    def is_current_step(self, step: BaseMarker):
        return self.current_step.value == step.value

    def current_step_in(self, steps: list[BaseMarker]):
        return self.current_step in steps

    def can_transition(
        self,
        step: BaseMarker = None,
        next: bool = False,
        prev: bool = False,
    ):
        if next:
            if self.current_step is self.current_step.last():
                return False  # TODO: Fix once we sort out transitions between stages
            step = self.current_step.next(self.current_step)
        elif prev:
            if self.current_step is self.current_step.first():
                return False  # TODO: Fix once we sort out transitions between stages
            step = self.current_step.previous(self.current_step)

        return getattr(self, f"{step.name}_gate", True)

    def current_step_between(self, start: BaseMarker, end: BaseMarker = None):
        end = end or self.current_step.last()
        return self.current_step.is_between(start, end)

    def current_step_at_or_before(self, end):
        return self.current_step <= end

    def current_step_at_or_after(self, start):
        return self.current_step >= start


StageStateUnionFactory: Callable[[], object] = lambda: BaseModel
StoryStateUnionFactory: Callable[[], object] = lambda: BaseModel


class BaseStoryState(BaseState):
    debug_mode: bool = Field(debug_mode_init, exclude=True)
    title: str
    story_id: str
    piggybank_total: int = 0
    max_route_index: int | None = None
    stage_states: Dict[str, Annotated[object, ...]] = Field(default_factory=dict)

    def __init__(self, **data):
        super().__init__(**data)
        for stage_name, stage_cls in STAGE_REGISTRY.items():
            if stage_name not in self.stage_states:
                self.stage_states[stage_name] = stage_cls()

    @classmethod
    def patch_union_type(cls):
        cls.__annotations__["stage_states"] = dict[str, StageStateUnionFactory()]
        cls.model_rebuild()


class BaseAppState(BaseState):
    story_state: Optional[Annotated[object, ...]] = None

    def __init__(self, **data):
        super().__init__(**data)
        for story_name, story_cls in STORY_REGISTRY.items():
            self.story_state = story_cls()

    @classmethod
    def patch_union_type(cls):
        cls.__annotations__["story_states"] = StoryStateUnionFactory()
        cls.model_rebuild()
