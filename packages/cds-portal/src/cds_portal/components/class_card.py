import solara
from pydantic import AwareDatetime
from solara.alias import rv

_STORY_URL = "/hubbles-law/"


@solara.component
def ClassCard(
    class_name: str,
    class_code: str,
    expected_size: int,
    created: AwareDatetime,
    active: bool,
):
    progress = solara.use_reactive(50)
    story_name = "Hubble's Law"  # story_name.replace("_", " ").title()

    with rv.Card(outlined=True, style_="width: 100%", class_="mb-6"):
        with rv.Row(class_="ma-0 pa-0"):
            with rv.Col(
                class_="ma-0 pa-0 d-flex flex-column justify-content-between", md=9
            ):
                with rv.ListItem(three_line=True):
                    with rv.ListItemContent():
                        rv.Html(
                            tag="div",
                            class_="text-overline mb-4",
                            # style_="font-weight: 500; line-height: 2rem; letter-spacing: .1666666667em !important; text-transform: uppercase !important; font-size: .75rem !important; font-family: Roboto, sans-serif !important;",
                            children=[story_name.upper()],
                        )
                        rv.ListItemTitle(
                            class_="text-h5 mb-1",
                            children=[class_name],
                        )
                        rv.ListItemSubtitle(children=[class_name])

                with rv.CardText():
                    rv.Chip(
                        label=True,
                        color="blue darken-4",
                        class_="mr-2",
                        children=[
                            rv.Icon(left=True, children=["mdi-code-greater-than"]),
                            f"{class_code}",
                        ],
                    )
                    rv.Chip(
                        label=True,
                        color="blue darken-4",
                        class_="mr-2",
                        children=[
                            rv.Icon(left=True, children=["mdi-calendar"]),
                            created.strftime("%Y-%m-%d"),
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
                            f"{expected_size}",
                        ],
                    )

            with rv.Col(md=3, class_="d-flex flex-column align-end"):
                rv.Btn(class_="mb-2", style_="width: 200px;", children=["Dashboard"])
                rv.Btn(class_="mb-2", style_="width: 200px;", children=["View"])
                rv.Btn(class_="mb-2", style_="width: 200px;", children=["Modify"])
                rv.Btn(style_="width: 200px;", children=["Deactivate"])

        with rv.CardActions():
            rv.ProgressLinear(
                v_model=progress.value,
                v_slots=[{"name": "default", "children": [f"{progress.value}%"]}],
                height=20,
                rounded=True
            )
