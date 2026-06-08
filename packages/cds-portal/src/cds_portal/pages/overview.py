import solara
from cds_client import CDSClient, ClassCreationInfo
from cds_core.components.location_helper.location_helper import LocationHelper
from solara.alias import rv

from cds_portal.components.class_card import ClassCard

from ..components.classes_table import ClassesTable
from ..components.create_class_dialog import CreateClassDialog
from ..components.overview_header import OverviewHeader
from ..components.story_card import StoryCard
from ..state import get_auth_state, get_portal_state, get_registration_pending


@solara.component
def EducatorOverview():
    portal_state = get_portal_state()
    active_tab = solara.use_reactive(0)

    search_query = solara.use_reactive("")
    status_filter = solara.use_reactive("All")

    educator = portal_state.educator.value
    verified = educator is not None and not educator.verification_code

    OverviewHeader(role="educator")

    with rv.Container():
        with rv.Row():
            create_button = rv.Btn(
                children=["Create"],
                class_="mr-2",
                style_="height: 40px",
                elevation=0,
                color="success",
                disabled=not verified,
            )

            solara.v.use_event(create_button, "click", lambda *_: CreateClassDialog())

            filter_field = rv.TextField(
                label="Filter",
                v_model=search_query.value,
                on_v_model=search_query.set,
                outlined=True,
                append_icon="mdi-close-circle" if search_query.value else "",
                dense=True,
            )
            rv.BtnToggle(
                class_="ml-2",
                style_="background: none !important",
                v_model=status_filter.value,
                on_v_model=status_filter.set,
                dense=True,
                children=[
                    rv.Btn(children=["All"], style_="height: 40px"),
                    rv.Btn(children=["Active"], style_="height: 40px"),
                    rv.Btn(children=["Inactive"], style_="height: 40px"),
                ],
            )

            solara.v.use_event(
                filter_field,
                "click:append",
                lambda *_: search_query.set(""),
            )

        classrooms = [
            filtered_classroom
            for classroom in portal_state.educator_classes.value
            if (
                filtered_classroom := dict(
                    class_name=classroom.name,
                    class_code=classroom.code,
                    expected_size=classroom.expected_size,
                    created=classroom.created,
                    active=classroom.active,
                )
            )
            and any(
                [
                    search_query.value.lower() in f"{value}".lower()
                    or not search_query.value
                    for value in filtered_classroom.values()
                ]
            )
        ]

        for classroom in classrooms:
            with rv.Row():
                ClassCard(**classroom)


@solara.component
def StudentOverview():
    portal_state = get_portal_state()

    OverviewHeader(role="student")

    with rv.Container():
        with rv.Card(color="primary"):
            with rv.Html(tag="div", class_="d-flex flex-no-wrap justify-space-between"):
                with rv.Html(tag="div"):
                    with rv.ListItem(three_line=True):
                        with rv.ListItemContent():
                            rv.Html(
                                tag="div",
                                class_="mb-2",
                                style_="font-weight: 500; line-height: 2rem; letter-spacing: .1666666667em !important; text-transform: uppercase !important; font-size: .75rem !important; font-family: Roboto, sans-serif !important;",
                                children=[portal_state.story_name.value.upper()],
                            )
                            rv.ListItemTitle(
                                class_="text-h5 mb-1",
                                children=[portal_state.student_classes.value[0].name],
                            )
                            rv.ListItemSubtitle(
                                children=[portal_state.student_classes.value[0].name]
                            )

                    with rv.CardActions():
                        rv.Chip(
                            label=True,
                            color="blue darken-4",
                            class_="mr-2",
                            children=[
                                rv.Icon(left=True, children=["mdi-code-greater-than"]),
                                f"{portal_state.student_classes.value[0].code}",
                            ],
                        )
                        rv.Chip(
                            label=True,
                            color="blue darken-4",
                            class_="mr-2",
                            children=[
                                rv.Icon(left=True, children=["mdi-calendar"]),
                                portal_state.student_classes.value[0].created.strftime(
                                    "%Y-%m-%d"
                                ),
                            ],
                        )
                        rv.Chip(
                            label=True,
                            color="blue darken-4",
                            children=[
                                rv.Icon(
                                    left=True,
                                    class_="mr-4",
                                    children=["mdi-account-group"],
                                ),
                                f"{portal_state.student_classes.value[0].expected_size}",
                            ],
                        )

                with rv.Avatar(size=125, class_="ma-0 pa-0"):
                    completed_stages = portal_state.completed_stages.value
                    total_stages = portal_state.total_stages.value
                    progress = (
                        int(completed_stages / total_stages * 100)
                        if total_stages > 0
                        else 0
                    )
                    rv.ProgressCircular(
                        color="white",
                        value=progress,
                        size=100,
                        width=15,
                        children=[f"{progress}"],
                    )


@solara.component
def LearnerOverview():
    portal_state = get_portal_state()

    OverviewHeader(role="learner")

    with rv.Container():
        StoryCard(
            story_name=portal_state.story_name.value,
            completed_stages=portal_state.completed_stages.value,
            total_stages=portal_state.total_stages.value,
        )


@solara.component
def Page():
    auth_state = get_auth_state()
    portal_state = get_portal_state()

    authenticated = auth_state.authenticated.value
    loading = portal_state.loading.value

    if authenticated:
        if loading:
            with rv.Container():
                with rv.Row(justify="center", class_="mt-12"):
                    rv.ProgressCircular(indeterminate=True, size=64, color="primary")
        elif portal_state.is_educator.value:
            EducatorOverview()
        elif auth_state.auth_type.value == "student":
            StudentOverview()
        else:
            LearnerOverview()
        return

    LocationHelper(url="/")
