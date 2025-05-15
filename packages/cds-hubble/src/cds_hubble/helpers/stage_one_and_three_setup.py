from glue.core.data import Data
from glue_jupyter import JupyterApplication
from solara.toestand import Ref, Reactive

from cds_core.app_state import AppState
from .data_management import (
    EXAMPLE_GALAXY_SEED_DATA,
    EXAMPLE_GALAXY_MEASUREMENTS,
    STUDENT_ID_COMPONENT,
)
from .example_measurement_helpers import (
    create_example_subsets,
    link_example_seed_and_measurements,
    _init_second_example_measurement,
    load_and_create_seed_data,
)
from .viewer_marker_colors import MY_DATA_COLOR
from ..story_state import LocalState
from ..utils import models_to_glue_data, _add_or_update_data


def initialize_second_example_measurement(local_state: Reactive[LocalState]):
    example_measurements = Ref(local_state.fields.example_measurements)
    if len(example_measurements.value) < 2:
        return

    changed, updated = _init_second_example_measurement(example_measurements.value)

    if changed != "":
        if updated is not None:
            example_measurements.set([example_measurements.value[0], updated])


def _add_or_update_example_measurements_to_glue(
    local_state: Reactive[LocalState], gjapp: JupyterApplication
):
    if len(local_state.value.example_measurements) > 0:
        # make the glue data object
        example_measurements_glue = models_to_glue_data(
            local_state.value.example_measurements,
            label=EXAMPLE_GALAXY_MEASUREMENTS,
        )
        example_measurements_glue.style.color = MY_DATA_COLOR
        create_example_subsets(gjapp, example_measurements_glue)

        # add or update it in glue
        use_this = _add_or_update_data(gjapp, example_measurements_glue)
        use_this.style.color = MY_DATA_COLOR

        # link the measurements to the seed data
        link_example_seed_and_measurements(gjapp)


def _glue_setup(
    global_state: Reactive[AppState], local_state: Reactive[LocalState]
) -> JupyterApplication:
    gjapp = gjapp = JupyterApplication(
        global_state.value.glue_data_collection, global_state.value.glue_session
    )

    # Get the example seed data
    if EXAMPLE_GALAXY_SEED_DATA not in gjapp.data_collection:
        load_and_create_seed_data(gjapp, local_state)

    return gjapp


def _update_seed_data_with_examples(
    global_state: Reactive[AppState], gjapp, example_data
):
    label = EXAMPLE_GALAXY_SEED_DATA + "_first"
    if label not in gjapp.data_collection:
        return

    student = Ref(global_state.fields.student)
    data = gjapp.data_collection[label]
    keep = data[STUDENT_ID_COMPONENT] != student.value.id
    update = {c.label: list(data[c][keep]) for c in data.main_components}

    examples_count = len(example_data)
    if examples_count == 1:
        measurement = example_data[0]
    elif examples_count >= 2:
        numbers = ("first", "second")
        measurement = sorted(
            example_data,
            key=lambda v: (
                numbers.index(v.measurement_number)
                if v.measurement_number in numbers
                else len(numbers)
            ),
        )[1]

        for component in data.main_components:
            value = getattr(measurement, component.label, None)
            if value is None:
                value = float("nan")
            update[component.label].append(value)

    new_data = Data(label=data.label, **update)
    data.update_values_from_data(new_data)
