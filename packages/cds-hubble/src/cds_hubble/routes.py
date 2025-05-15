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
from .state import GLOBAL_STATE, LOCAL_STATE

MetaLayout = solara.component(
    lambda *args, **kwargs: Layout(
        *args, **kwargs, local_state=LOCAL_STATE, global_state=GLOBAL_STATE
    )
)

routes = [
    solara.Route(
        path="/",
        component=solara.component(
            lambda: IntroductionPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Introduction",
        layout=MetaLayout,
    ),
    solara.Route(
        path="spectra-and-velocity",
        component=solara.component(
            lambda: SpectraAndVelocityPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Spectra and Velocity",
        # layout=MetaLayout,
    ),
    solara.Route(
        path="distance-introduction",
        component=solara.component(
            lambda: DistanceIntroductionPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Distance Introduction",
        # layout=MetaLayout,
    ),
    solara.Route(
        path="distance-measurements",
        component=solara.component(
            lambda: DistanceMeasurementsPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Distance Measurements",
        # layout=MetaLayout,
    ),
    solara.Route(
        path="explore-data",
        component=solara.component(
            lambda: ExploreDataPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Explore Data",
        # layout=MetaLayout,
    ),
    solara.Route(
        path="class-results",
        component=solara.component(
            lambda: ClassResultsPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="Class Results",
        # layout=MetaLayout,
    ),
    solara.Route(
        path="prodata",
        component=solara.component(
            lambda: ProDataPage(
                **{"global_state": GLOBAL_STATE, "local_state": LOCAL_STATE}
            )
        ),
        label="ProData",
        # layout=MetaLayout,
    ),
]
