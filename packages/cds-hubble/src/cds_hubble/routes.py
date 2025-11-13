import solara
from solara.lab import Ref
from cds_core.logger import setup_logger

import solara
from solara.lab import Ref

from .stages.p00_introduction import Page as IntroductionPage
from .stages.p01_spectra_and_velocity import Page as SpectraAndVelocityPage
from .stages.p02_distance_introduction import Page as DistanceIntroductionPage
from .stages.p03_distance_measurements import Page as DistanceMeasurementsPage
from .stages.p04_explore_data import Page as ExploreDataPage
from .stages.p05_class_results import Page as ClassResultsPage
from .stages.p06_prodata import Page as ProDataPage
from .layout import Layout
from .state import APP_STATE, LOCAL_STATE

MetaLayout = solara.component(
    lambda *args, **kwargs: Layout(
        *args, **kwargs, story_state=LOCAL_STATE, app_state=APP_STATE
    )
)

routes = [
    solara.Route(
        path="/",
        component=solara.component(
            lambda: IntroductionPage(**{"app_state": APP_STATE})
        ),
        label="Introduction",
        layout=MetaLayout,
    ),
    solara.Route(
        path="spectra-and-velocity",
        component=solara.component(
            lambda: SpectraAndVelocityPage(**{"app_state": APP_STATE})
        ),
        label="Spectra and Velocity",
    ),
    solara.Route(
        path="distance-introduction",
        component=solara.component(
            lambda: DistanceIntroductionPage(**{"app_state": APP_STATE})
        ),
        label="Distance Introduction",
    ),
    solara.Route(
        path="distance-measurements",
        component=solara.component(
            lambda: DistanceMeasurementsPage(**{"app_state": APP_STATE})
        ),
        label="Distance Measurements",
    ),
    solara.Route(
        path="explore-data",
        component=solara.component(lambda: ExploreDataPage(**{"app_state": APP_STATE})),
        label="Explore Data",
    ),
    solara.Route(
        path="class-results",
        component=solara.component(
            lambda: ClassResultsPage(**{"app_state": APP_STATE})
        ),
        label="Class Results",
    ),
    solara.Route(
        path="prodata",
        component=solara.component(lambda: ProDataPage(**{"app_state": APP_STATE})),
        label="ProData",
    ),
]
