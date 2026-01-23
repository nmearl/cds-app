import solara

from .FileLoad import TableLoad, SetColumns, CSVFileInfoToTable

import reacton.ipyvuetify as rv

import copy

from functools import partial

from ..logger_setup import logger
from ..class_report import Roster
from typing import Union, Optional  
import pandas as pd

@solara.component
def StudentDataLoadInterface(name_dataframe = None, on_load = None, student_names_set = None):
    
    
    file_info = solara.use_reactive(None)
    table = solara.use_reactive(None)
    table_set = solara.use_reactive(student_names_set)

    name_dataframe = solara.use_reactive(name_dataframe)
    
    def on_clear(value):
        if not value:
            logger.debug('clearing values')
            table.set(None)
            table_set.set(False)
            name_dataframe.set(None)
            file_info.set(None)
            
    def on_name_dataframe_set(df):
        logger.debug("setting table")
        # table_set.set(df is not None)
        name_dataframe.set(df)


    
    file_loaded = solara.use_reactive(False, on_change = on_clear)
    

    with solara.Row():
        with solara.Column():
            TableLoad(file_info, load_complete = file_loaded)
    with solara.Row(gap="10px"):
        with solara.Div():
            SetColumns(table, on_set = on_name_dataframe_set)
        CSVFileInfoToTable(file_info, on_table = table.set)
@solara.component
def FakeStudentDataLoadInterface(name_dataframe = None, on_load = None, student_names_set = None, id_list = []):
    """
    convenience component to generate a new valid set of names for testing
    """
    name_dataframe = solara.use_reactive(name_dataframe)
    
    def gen_fake_data():
        names = [f'Fake name {i}' for i in id_list]
        df = pd.DataFrame({'student_id': id_list, 'name': names})
        name_dataframe.set(df)
    
    solara.Button(label="Generate Fake Student Names", icon_name='mdi-account-multiple-plus', on_click=gen_fake_data, classes=["my-buttons","student-name-button"])
        
    

@solara.component
def StudentLoadDialog(student_names = None, student_names_set = None, dialog_open = False, no_dialog = False, validator = lambda x: (True, []), id_list = []):
    
    
    student_names = solara.use_reactive(student_names)
    
    def on_internal_names_change(value):
        if student_names.value is not None:
            new = pd.concat([student_names.value, value]).drop_duplicates(subset=['student_id'], keep='last').reset_index(drop=True)
            student_names.set(new)
        else:
            student_names.set(value)
            
    internal_student_names = solara.use_reactive(student_names.value, on_change=on_internal_names_change)
    student_names_set = solara.use_reactive(student_names_set)
    
    
    table_valid = solara.use_reactive([False, ''])
    
    dialog_open = solara.use_reactive(dialog_open)
      
    dialog = rv.Dialog(
        v_model = dialog_open.value,
        on_v_model=dialog_open.set,
        v_slots = [{
            'name': 'activator',
            'variable': 'dummy_var',
            'children': 
                solara.Tooltip(tooltip="Use local csv file to convert IDs to names", 
                    children = [solara.Button(label = "ID → Name", icon_name='mdi-google-spreadsheet', on_click = lambda: dialog_open.set(True), classes=["my-buttons","student-name-button"])]
                )
        }]
    )
    comp = dialog if not no_dialog else solara.Div()
    with comp:
        with solara.Card(classes=["dash-card"]):
            StudentDataLoadInterface(internal_student_names, student_names_set = student_names_set)
            
            table_valid.set(validator(internal_student_names.value))
            
            # if table is in valid because of missing ids and student_names_set was never given
            # assume that we are running the component in standalone mode and set student_names_set to true
            # otherwise this needs to be set elsewhere to avoid an infinite loop. this probably
            # can be done better, but this works and is stable so . This not needed if running the full dashboard
            if (table_valid.value[1] != 0) and (student_names_set.value is None):
                logger.error("setting student names set to true in standalone mode")
                student_names_set.set(True)
                # raise Exception("student_names_set must be provided when there are missing student IDs in the table")
                
            if table_valid.value[0] and student_names_set.value:
                logger.debug("table valid and names set")
                solara.Success("Successfully updated student names.", dense=True, outlined=True, classes=["my-success"])
            elif (not table_valid.value[0]) and student_names_set.value:
                logger.debug("table invalid but names set")
                solara.Success("Updated student names.", dense=True, outlined=True, classes=["my-success"])
                solara.Warning("Some student IDs ({}) are missing from the table.".format(table_valid.value[1]), dense=True, outlined=True, icon='mdi-traffic-cone')
            
                
            with solara.CardActions():
                solara.Button(icon_name="mdi-close-circle",label = "Close", on_click = lambda: dialog_open.set(False), text=True, outlined=True, classes=["dash-dialog-button"])
                FakeStudentDataLoadInterface(internal_student_names, student_names_set = student_names_set, id_list = id_list)


def validate_table(table, required_sids):
        logger.debug('validating table')
        if isinstance(table, solara.Reactive):
            table = table.value
            
        if table is None:
            logger.debug("table is none")
            return False, 0
        if 'student_id' not in table.columns:
            logger.debug("no student id column")
            return False, 0
        if 'name' not in table.columns:
            logger.debug("no name column")
            return False, 0
        
        sids = table['student_id'].tolist()
        
        present = all([r in sids for r in required_sids])
        
        missing = [r for r in required_sids if r not in sids]
        if not present:
            logger.debug(f"missing ids {missing}")
        return present, missing

def set_names_on_roster(
    roster: Union[solara.Reactive[Roster], Roster] = None, 
    student_names = None, 
    student_names_set = None, 
    on_update = lambda x: None
    ):
    logger.debug(f"Checking: student_names has a value {student_names.value is not None} {type(student_names.value)}, student_names_set is {student_names_set.value}")
    r = copy.copy(roster.value)
    if (student_names.value is not None) and (not student_names_set.value):
        logger.debug("successfully loaded student names, updating roster")
        student_names_dict = {row['student_id']: row['name'] for _, row in student_names.value.iterrows()}
        r.set_student_names(student_names_dict)
        # r.short_report(refresh = True)
        roster.set(r)
        student_names_set.set(True)
        on_update(student_names.value)
    else:
        logger.debug(f"not updating student names: Reason: student_names has a value {student_names.value is not None} {type(student_names.value)}, student_names_set is {student_names_set.value}")

@solara.component
def StudentNameLoad(roster: Union[solara.Reactive[Roster], Roster], student_names = None, student_names_set = None, on_update = lambda x: None, use_dialog = True):
    logger.debug("student name load component")
    roster = solara.use_reactive(roster)
    def on_change(val):
        logger.debug("student names changed to {}".format(val))
    student_names = solara.use_reactive(student_names, on_change = on_change)
    student_names_set = solara.use_reactive(student_names_set, on_change=lambda x: logger.debug(f"student_names_set changed to {x}"))
  
    validator = partial(validate_table, required_sids = roster.value.student_ids)
    # if the student_names is set, we need to validate it
    if student_names_set.value:
        valid = validator(student_names.value)
        if not valid[0]:
            student_names_set.set(False)
            
    StudentLoadDialog(student_names, student_names_set = student_names_set, no_dialog = not use_dialog, validator = validator, id_list = roster.value.student_ids)

    solara.use_effect(
        lambda: set_names_on_roster(
            roster, student_names, 
            student_names_set,
            on_update=on_update,
            ),
        [student_names.value]
    )