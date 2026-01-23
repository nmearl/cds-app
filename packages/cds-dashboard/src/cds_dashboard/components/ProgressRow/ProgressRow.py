import solara

@solara.component_vue('ProgressRow.vue')
def ProgressRow(column_data=None, 
                selected = False, 
                on_selected = None,
                stepOrder = None,
                stepProgress = None,
                height = None,
                gap="0px",
                ):
    pass
