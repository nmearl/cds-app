from typing import Callable

import reacton.ipyvuetify as rv
import solara
from pydantic import AwareDatetime


def EducatorButtonList(
    active: bool, on_deactivate: Callable[[], None] | None, class_id: int
):
    rv.Btn(
        class_="mb-2",
        style_="width: 200px;",
        children=["Dashboard"],
        href=f"/educator-dashboard?id={class_id}",
    )
    rv.Btn(
        class_="mb-2",
        style_="width: 200px;",
        children=["Preview"],
        href="/hubbles-law",  # TODO: this needs to depend on the chosen story
    )
    rv.Btn(class_="mb-2", style_="width: 200px;", children=["Modify"])
    deactivate_btn = rv.Btn(
        style_="width: 200px;",
        children=["Deactivate"],
        disabled=not active,
    )
    if on_deactivate is not None:
        rv.use_event(deactivate_btn, "click", lambda *_: on_deactivate())


@solara.component
def ClassCard(
    class_name: str,
    class_id: int,
    story_name: str,
    educator_name: str,
    class_code: str,
    expected_size: int,
    created: AwareDatetime,
    active: bool,
    progress: float = 50.0,
    is_educator: bool = False,
    on_deactivate: Callable[[], None] | None = None,
):
    with rv.Card(
        outlined=True,
        style_=f"width: 100%; opacity: {'1' if active else '0.6'}",
        class_="mb-6",
    ):
        with rv.Row(class_="ma-0 pa-0"):
            with rv.Col(
                class_="ma-0 pa-0 d-flex flex-column justify-content-between", md=9
            ):
                with rv.ListItem(three_line=True):
                    with rv.ListItemContent():
                        with rv.Html(tag="div", class_="d-flex align-center mb-2"):
                            rv.Html(
                                tag="div",
                                class_="text-overline",
                                children=[story_name.upper()],
                            )
                            if not active:
                                rv.Chip(
                                    children=["Inactive"],
                                    color="grey",
                                    small=True,
                                    class_="ml-2",
                                )
                        rv.ListItemTitle(
                            class_="text-h5 mb-1",
                            children=[class_name],
                        )
                        rv.ListItemSubtitle(
                            children=[
                                rv.Html(
                                    tag="div",
                                    class_="d-inline-flex align-center mr-4",
                                    children=[
                                        rv.Icon(
                                            left=True,
                                            children=["mdi-account-box"],
                                            small=True,
                                        ),
                                        f"{educator_name}",
                                    ],
                                ),
                                rv.Html(
                                    tag="div",
                                    class_="d-inline-flex align-center mr-4",
                                    children=[
                                        rv.Icon(
                                            left=True,
                                            children=["mdi-calendar"],
                                            small=True,
                                        ),
                                        created.strftime("%Y-%m-%d"),
                                    ],
                                ),
                                rv.Html(
                                    tag="div",
                                    class_="d-inline-flex align-center",
                                    children=[
                                        rv.Icon(
                                            left=True,
                                            children=["mdi-account-group"],
                                            small=True,
                                        ),
                                        f"{expected_size}",
                                    ],
                                ),
                            ]
                        )

                with rv.CardText():
                    class_code_field = rv.TextField(
                        value=f"{class_code}",
                        outlined=True,
                        readonly=True,
                        dense=True,
                        style_="width:300px",
                        solo=True,
                        hide_details=True,
                        append_icon="mdi-content-copy",
                        v_slots=[
                            {
                                "name": "prepend-inner",
                                "children": [
                                    rv.Chip(
                                        color="blue darken-4",
                                        label=True,
                                        class_="mr-4",
                                        small=True,
                                        children=["Class Code"],
                                    )
                                ],
                            },
                        ],
                    )
                    rv.use_event(
                        class_code_field,
                        "click:append",
                        lambda *_: print("COPY"),
                    )

            with rv.Col(md=3, class_="d-flex flex-column align-end"):
                if is_educator:
                    EducatorButtonList(
                        active=active, on_deactivate=on_deactivate, class_id=class_id
                    )
                else:
                    rv.Btn(
                        class_="mb-2",
                        style_="width: 200px;",
                        children=["Continue" if progress > 0 else "Start"],
                    )

        with rv.CardActions():
            rv.ProgressLinear(
                value=progress,
                v_slots=[{"name": "default", "children": [f"{progress:.1f}%"]}],
                height=20,
                rounded=True,
            )
