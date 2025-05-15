import solara
from solara import Reactive
from solara.lab import Ref
from solara.lab import Ref, task

from cds_core.app_state import AppState
from cds_core.logger import setup_logger
from .remote import LOCAL_API
from .story_state import LocalState

logger = setup_logger("CDS-HUBBLE INITIALIZE")


GLOBAL_STATE = solara.reactive(AppState())
LOCAL_STATE = Ref(GLOBAL_STATE.fields.story_state)
