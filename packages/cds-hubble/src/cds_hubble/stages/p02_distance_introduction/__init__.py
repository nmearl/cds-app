import solara
from solara import Reactive
from solara.toestand import Ref
from typing import cast

from cds_core.base_states import MultipleChoiceResponse
from cds_core.logger import setup_logger
from cds_core.app_state import AppState
from ...components import Stage2Slideshow, STAGE_2_SLIDESHOW_LENGTH
from ...remote import LOCAL_API
from ...story_state import StoryState, mc_callback, get_mc_response
from .stage_state import StageState
from ...utils import get_image_path, DISTANCE_CONSTANT, push_to_route

logger = setup_logger("STAGE 2")


@solara.component
def Page(app_state: Reactive[AppState]):
    story_state = Ref(cast(StoryState, app_state.fields.story_state))
    stage_state = Ref(
        cast(StageState, story_state.fields.stage_states["distance_introduction"])
    )

    loaded_component_state = solara.use_reactive(False)
    router = solara.use_router()
    location = solara.use_context(solara.routing._location_context)

    def _load_component_state():
        # Load stored component state from database, measurement data is
        # considered higher-level and is loaded when the story starts
        LOCAL_API.get_stage_state(app_state, story_state, stage_state)

        # TODO: What else to we need to do here?
        logger.info("Finished loading component state for stage 2.")
        loaded_component_state.set(True)

    solara.use_memo(_load_component_state, dependencies=[])

    def _write_component_state():
        if not loaded_component_state.value:
            return

        # Listen for changes in the states and write them to the database
        res = LOCAL_API.put_stage_state(app_state, story_state, stage_state)

        if res:
            logger.info("Wrote component state for stage 2 to database.")
        else:
            logger.info("Did not write component state for stage 2 to database.")

    logger.info("Trying to write component state for stage 2.")
    solara.lab.use_task(_write_component_state, dependencies=[stage_state.value])

    step = Ref(stage_state.fields.distance_slideshow_state.step)
    max_step_completed = Ref(
        stage_state.fields.distance_slideshow_state.max_step_completed
    )

    speech = Ref(app_state.fields.speech)
    Stage2Slideshow(
        step=stage_state.value.distance_slideshow_state.step,
        max_step_completed=stage_state.value.distance_slideshow_state.max_step_completed,
        length=STAGE_2_SLIDESHOW_LENGTH,
        titles=[
            "1920's Astronomy",
            "1920's Astronomy",
            "How can we know how far away something is?",
            "How can we know how far away something is?",
            "How can we know how far away something is?",
            "How can we know how far away something is?",
            "Galaxy Distances",
            "Galaxy Distances",
            "Galaxy Distances",
            "Galaxy Distances",
            "Galaxy Distances",
            "Galaxy Distances",
            "Galaxy Distances",
        ],
        interact_steps=[7, 9],
        distance_const=DISTANCE_CONSTANT,
        image_location=get_image_path(router, "stage_two_intro"),
        event_set_step=step.set,
        event_set_max_step_completed=max_step_completed.set,
        event_mc_callback=lambda event: mc_callback(event, story_state, stage_state),
        state_view={
            "mc_score_1": get_mc_response("which-galaxy-closer", stage_state),
            "score_tag_1": "which-galaxy-closer",
            "mc_score_2": get_mc_response("how-much-closer-galaxies", stage_state),
            "score_tag_2": "how-much-closer-galaxies",
        },
        event_return_to_stage1=lambda _: push_to_route(
            router, location, "spectra-&-velocity"
        ),
        event_slideshow_finished=lambda _: push_to_route(
            router, location, "distance-measurements"
        ),
        debug=app_state.value.show_team_interface,
        speech=speech.value.model_dump(),
    )
