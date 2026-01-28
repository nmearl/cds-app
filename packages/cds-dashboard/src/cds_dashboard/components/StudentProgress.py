import solara
from ..class_report import Roster
from solara.reactive import Reactive
from typing import Optional, List, cast

from .TableFromRows import TableFromRows
from .ProgressRow import ProgressRow

@solara.component
def StudentProgressRow(progress,
                    on_selected_id = None,
                    selected_id: Optional[int] = None, # type: ignore
                    step_order: Optional[List[int]] = None,
                    ):
    """
    progress should be a dictionary with the following keys:
    student_id, student_name, total_points, percent_complete, step_progress

    """
    
    
    student_id = cast(int, progress['student_id'])
    
    selected_id: Reactive[int | None] = solara.use_reactive(selected_id)  # type: ignore
    selected = solara.use_reactive(
        (student_id is not None) and
        str(selected_id.value) == str(int(student_id)) 
        )
    

    student_data = {
        'ID': progress['student_id'],
        'Name': progress['student_name'],
        'Total Points': progress['total_points'],
        'Progress': f"{progress['percent_complete']}%"
    }
    
    def on_row_click(event):
            selected.set(event)

            if on_selected_id is None:
                selected_id.set(int(student_id) if event else None)
            else:
                on_selected_id(int(student_id) if event else None)

    
    if step_order is None:
        step_order = sorted(progress['step_progress'].keys())

    ProgressRow(column_data=student_data, 
                selected = selected.value, #str(selected_id.value) == str(student_id),
                on_selected=on_row_click,
                stepOrder=step_order,
                stepProgress=progress['step_progress'],
                height='100%', gap="5px")


@solara.component
def StudentProgressTable(roster: Optional[Reactive[Roster] | Roster] = None, 
                         student_id = None, 
                         on_student_id = None, 
                         headers = None, 
                         stage_labels = [],
                         height = '100%',
                         ):
    """
    progress_data should be a dictionary keyed by student_id.
    Each entry should have the following keys:
    student_id, student_name, total_score, out_of_possible, percent_complete, progress_dict
    progress_dict should map stage names to {name, index, progress}.
    
    """
    
    roster = solara.use_reactive(roster)
    if roster.value is None:
        solara.Error(label="No roster available. Please contact the CosmicDS team for help.", outlined=True, text = True)
        return
    
    data = roster.value.student_progress
    
    if data is None or (isinstance(data, dict) and len(data) == 0):
        solara.Error(label="No data available. Please contact the CosmicDS team for help.", outlined=True, text = True)
        return
    
    def on_student_id_wrapper(value):
        setfunc = on_student_id or student_id.set
        
        if value is None:
            setfunc(None)
        else:
            setfunc(int(value))

    

    if headers is None:
        headers = ['', 'Student<br>ID', 'Student<br>Name', 'Points/<br>available', 'Progress<br>(%)'] + stage_labels
    student_ids = roster.value.student_ids if roster.value else list(data.keys())
    stage_order = list(range(0, len(stage_labels)))
    
    with TableFromRows(headers=headers, table_height=height):
        for student_id_value in student_ids:
            student_entry = data.get(student_id_value, {})
            progress_dict = student_entry.get('progress_dict', {})
            step_progress = {}
            for stage in progress_dict.values():
                stage_index = stage.get('index')
                if stage_index is None:
                    continue
                step_progress[int(stage_index)] = stage.get('progress')
            for stage_index in stage_order:
                step_progress.setdefault(stage_index, 0)

            total_score = student_entry.get('total_score')
            out_of_possible = student_entry.get('out_of_possible')
            total_points = f"{total_score}/{out_of_possible}" if total_score is not None else "0/0"

            student_name = student_entry.get('student_name')
            if not student_name:
                student_name = f"Student {student_id_value}"

            student_progress = {
                'student_id': student_id_value,
                'student_name': student_name,
                'total_points': total_points,
                'percent_complete': student_entry.get('percent_complete', 0),
                'step_progress': step_progress,
            }
            StudentProgressRow(progress = student_progress,
                                selected_id = student_id,
                                on_selected_id = on_student_id_wrapper,
                                step_order = stage_order,
                                )
