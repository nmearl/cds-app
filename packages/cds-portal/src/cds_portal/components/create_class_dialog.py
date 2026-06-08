import solara
from cds_client import CDSClient, ClassCreationInfo
from solara.alias import rv

from ..state import get_portal_state


@solara.component
def CreateClassDialog():
    portal_state = get_portal_state()
    show = solara.use_reactive(False)
    class_name = solara.use_reactive("")
    expected_size = solara.use_reactive("30")
    error = solara.use_reactive("")
    loading = solara.use_reactive(False)

    def _create():
        error.set("")
        name = class_name.value.strip()
        if not name:
            error.set("Class name is required.")
            return
        try:
            size = int(expected_size.value)
        except ValueError:
            error.set("Expected size must be a number.")
            return

        educator = portal_state.educator.value
        if educator is None:
            return

        loading.set(True)
        try:
            client = CDSClient()
            client.classes.create(
                ClassCreationInfo(
                    educator_id=educator.id,
                    name=name,
                    expected_size=size,
                    story_name="hubbles_law",
                )
            )
            portal_state.educator_classes = sorted(
                client.educators.get_classes(educator.id),
                key=lambda c: (c.created is None, c.created),
                reverse=True,
            )
            class_name.set("")
            expected_size.set("30")
            show.set(False)
        except Exception as e:
            error.set(f"Could not create class: {e}")
        finally:
            loading.set(False)

    solara.Button(
        label="Create Class",
        icon_name="mdi-plus",
        color="primary",
        on_click=lambda: show.set(True),
    )

    with rv.Dialog(
        v_model=show.value,
        on_v_model=show.set,
        max_width=480,
        persistent=loading.value,
    ):
        with rv.Card():
            rv.CardTitle(children=["New Class"])
            with rv.CardText():
                solara.InputText(
                    "Class name",
                    value=class_name.value,
                    on_value=class_name.set,
                )
                solara.InputText(
                    "Expected number of students",
                    value=expected_size.value,
                    on_value=expected_size.set,
                )
                if error.value:
                    solara.Text(error.value, style="color: #ff5252;")
            with rv.CardActions():
                rv.Spacer()
                solara.Button(
                    label="Cancel",
                    text=True,
                    on_click=lambda: show.set(False),
                    disabled=loading.value,
                )
                solara.Button(
                    label="Create",
                    color="primary",
                    on_click=_create,
                    disabled=loading.value,
                )
