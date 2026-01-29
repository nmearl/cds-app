from typing import List, Any, Dict, Union, cast, Protocol
from .common_types import RosterEntry
from .database.old_types import StudentEntry as OldRosterEntry
from .database_new.types import StudentEntry as NewRosterEntry
from .cds_api_utils.Query import QueryCosmicDSApi
from .logger_setup import logger

# Import State classes
from .database.State import State
from .database_new.NewState import State as NewState
from .database_new.NewState import MonoRepoState as MonoRepoState
import json
def log_to_json(thing):
    with open('temp.json', 'w') as f:
        f.write(json.dumps(thing))


# Each database version has its own adapter that knows how to transform the
# API response into a format appropriate for that version's State class.
# Protocol is kinda like a TS interface (but not at all), telling use the structre
# that needs to be implemented in a class. Not all tooling pays attention to it.
class StateAdapter(Protocol):
    query: QueryCosmicDSApi
   
    def transform_roster(self, api_roster: List[Any]) -> List[OldRosterEntry]: ...
    def get_class_measurements(self, roster: List[OldRosterEntry], exclude_merged: bool) -> Dict[str, List[Any]]: ...
    def get_student_measurements(self, roster: List[OldRosterEntry], student_id: int) -> List[Dict[str, Any]]: ...
    @property
    def version_name(self) -> str: ...
    @property
    def state_class(self) -> type: ...


class LegacyStateAdapter(StateAdapter):
    #The legacy format is correct from the API, but we ensure consistency
    
    def __init__(self, query: QueryCosmicDSApi):
        self.query = query
    
    def transform_roster(self, api_roster: List[Any]) -> List[OldRosterEntry]:
        """
        Transform legacy API format to clean OldRosterEntry format.
        Legacy API is what everthing is based on so minimal transformation needed.
        """
        result = cast(List[OldRosterEntry], api_roster)
        return result
    
    def get_class_measurements(self, roster: List[OldRosterEntry], exclude_merged: bool = False) -> Dict[str, List[Any]]:
        """Get all measurements for the class. Uses API call for legacy format."""

        res = self.query.get_class_data(class_id=self.query.class_id, exclude_merged=exclude_merged)
        if res is None or res == {} or len(res) == 0:
            res = {'student_id': []}
        return res if res is not None else {'student_id': []}
    
    def get_student_measurements(self, roster: List[OldRosterEntry], student_id: int) -> List[Dict[str, Any]]:
        """Get measurements for a specific student. Uses API call for legacy format."""

        result = self.query.get_student_data(student_id)
        return result.get('measurements', []) if result else []
    
    @property
    def version_name(self) -> str:
        return "legacy"
    
    @property
    def state_class(self) -> type:
        return State  # Uses old marker-based progress calculation


class OldSolaraStateAdapter(StateAdapter):
    """
    Adapter for Solara-era database format (215 <= class_id < 335).
    
    Cleaned up, but keep it close to original that worked.
    """
    
    def __init__(self, query: QueryCosmicDSApi):
        self.query = query
    
    def transform_roster(self, api_roster: List[Any]) -> List[OldRosterEntry]:
        result: List[OldRosterEntry] = []
        
        for student in api_roster:
            transformed = self._transform_student_entry(student)
            result.append(transformed)
        
        self._add_stage_data(result)
        
        return result
    
    
    def _transform_student_entry(self, student: NewRosterEntry) -> OldRosterEntry:        
        story_state = student['story_state']
        
        # forcefully reshape from NewRosterEntry to OldRosterEntry
        student['app_state'] = story_state.get('app', {})  # type: ignore[reportAssignmentType]
        student['story_state'] = story_state['story'] # type: ignore[reportAssignmentType]
        student['student_id'] = student['student_id']
        
        # Process free responses (original block)
        free_responses_dict = student['story_state'].get('free_responses', {}).copy()
        
        if 'responses' in free_responses_dict:
            free_responses = free_responses_dict.pop('responses')
            responses = self._group_by_stage(free_responses)
            # Extract just the 'response' text 
            ## TODO: follows original logic, but this looks recursive :|
            responses = {
                stage_key: {q_key: q_value.get('response', '')
                            for q_key, q_value in stage_value.items()}
                for stage_key, stage_value in responses.items()
            }
            student['story_state']['responses'] = responses # type: ignore[reportAssignmentType]
        
        # Remove free_responses after extraction (original: if 'free_responses' in roster[i]['story_state'])
        if 'free_responses' in student['story_state']:
            student['story_state'].pop('free_responses')
        
        # Process multiple choice scoring (original block)
        mc_scoring_dict = student['story_state'].get('mc_scoring', {}).copy()
        
        if 'scores' in mc_scoring_dict:
            mc_scoring = mc_scoring_dict.pop('scores')
            student['story_state']['mc_scoring'] = self._group_by_stage(mc_scoring)
        
        return cast(OldRosterEntry, student)  # Cast back to expected type
    
    def _group_by_stage(self, items: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        # Find all unique stages
        stages = set([value['stage'] for value in items.values() if isinstance(value, dict) and 'stage' in value])
        
        if len(stages) == 0:
            logger.debug('OldSolaraStateAdapter._group_by_stage: No stages found in data')
            return items  # Return as-is if no stage field
        
        # Group by stage, keeping all original fields
        by_stage: Dict[str, Dict[str, Any]] = {}
        for stage in stages:
            by_stage[stage] = {
                key: value
                for key, value in items.items()
                if isinstance(value, dict) and 'stage' in value and value['stage'] == stage
            }
        
        return by_stage
    
    def _add_stage_data(self, roster: List[OldRosterEntry]) -> None:
        for i, entry in enumerate(roster):
            student_id = entry['student_id']
            try:
                stages = self.query.get_stages(student_id)
                entry['story_state']['stages'] = stages  # type: ignore
            except Exception as e:
                logger.error(f"OldSolaraStateAdapter: Failed to fetch stages for student {student_id}: {e}")
                entry['story_state']['stages'] = {}  # type: ignore
    
    def get_class_measurements(self, roster: List[OldRosterEntry], exclude_merged=False) -> Dict[str, List[Any]]:
        """Get all measurements for the class. Uses API call for Solara format."""

        res = self.query.get_class_data(class_id=self.query.class_id, exclude_merged=exclude_merged)
        if res is None or res == {} or len(res) == 0:
            res = {'student_id': []}
        return res if res is not None else {'student_id': []}
    
    def get_student_measurements(self, roster: List[OldRosterEntry], student_id: int) -> List[Dict[str, Any]]:
        """Get measurements for a specific student. Uses API call for Solara format."""

        result = self.query.get_student_data(student_id)
        return result.get('measurements', []) if result else []
    
    @property
    def version_name(self) -> str:
        return "solara"
    
    @property
    def state_class(self) -> type:
        return NewState  # Uses progress field from database


class MonorepoStateAdapter(StateAdapter):
    """
    Adapter for monorepo database format (class_id >= 335).
    
    To be implemented once monorepo format is analyzed.
    Likely similar to Solara but with different API structure.
    Will also use NewState since it has database-provided progress.
    """
    
    def __init__(self, query: QueryCosmicDSApi):
        self.query = query
    
    def transform_roster(self, api_roster: List[Any]) -> List[OldRosterEntry]:
        result = []
        
        for student in api_roster:
            transformed = self._transform_student_entry(student)
            result.append(transformed)
        return result
    
    def fix_progress(self, stage: Dict):
        """
        In the monorepo format, the progress is already 
        calculated by the Stage and stored in the database.
        """
        return stage['progress']
    
    
    def fix_stages(self, stage_states: Dict, max_stage_progress: int):
        stage_map = {
            'introduction' : '0',
            'spectra_&_velocity': '1',
            'distance_introduction': '2',
            'distance_measurements': '3',
            'explore_data' : '4',
            'class_results_and_uncertainty': '5',
            'professional_data': '6',
        }
        for key, value in stage_states.items():
            stage_states[key]['index'] = int(stage_map[key])
            set_to_zero = (max_stage_progress is not None) or (max_stage_progress is not None and int(stage_map[key]) > max_stage_progress)
            stage_states[key]['progress'] = 0 if set_to_zero else self.fix_progress(value)
            stage_states[key]['state'] = value
        return stage_states

        
    
    def get_multiple_choice(self, stage_states: Dict):
        mc_scoring_dict = {}
        for key, value in stage_states.items():
            mctemp = value.pop('multiple_choice_responses')
            if (len(mctemp) > 0):
                mc_scoring_dict[str(value['index'])] = mctemp
        return mc_scoring_dict
        
    def get_free_responses(self, stage_states: Dict):
        free_responses_dict = {}
        for key, value in stage_states.items():
            stage_free_responses = value.pop('free_responses')
            # Extract just the 'response' text from each question
            # Similar to OldSolaraStateAdapter transformation
            responses = {
                q_key: q_value.get('response', '') if isinstance(q_value, dict) else q_value
                for q_key, q_value in stage_free_responses.items()
            }
            free_responses_dict[str(value['index'])] = responses
        return free_responses_dict
        
        
    
    def _transform_student_entry(self, student):
        # already has top level student id
        student_id = student.get('student_id', 'unknown')
        last_modified = student.get('last_modified')  # Capture before transformation
        
        app = student.pop('story_state').pop('app')
        story_state = app.pop('story_state')
        max_stage_progress = story_state.get('max_stage_progress', None)
        # Check if measurements exist and inject last_modified
        measurements = story_state.get('measurements', None)
        if measurements is not None and last_modified is not None:
            # Inject last_modified into each measurement
            for measurement in measurements:
                if isinstance(measurement, dict):
                    measurement['last_modified'] = last_modified
        
        stage_states = self.fix_stages(story_state.pop('stage_states'), max_stage_progress)
        # check if student_id is in the story_state
        if 'student_id' not in story_state:
            story_state['student_id'] = student_id
        student['app_state'] = app
        student['story_state'] = story_state
        student['story_state']['mc_scoring'] = self.get_multiple_choice(stage_states)
        student['story_state']['responses'] = self.get_free_responses(stage_states)
        student['story_state']['stages'] = stage_states
        if ('stage_5_class_data_students' in story_state and len(story_state['stage_5_class_data_students']) > 0):
            student['story_state']['class_data_students'] = story_state['stage_5_class_data_students']
        elif ('stage_4_class_data_students' in story_state and len(story_state['stage_4_class_data_students']) > 0):
            student['story_state']['class_data_students'] = story_state['stage_4_class_data_students']
        else:
            pass
        return student
    
    def get_class_measurements(self, roster: List[OldRosterEntry], exclude_merged=False) -> Dict[str, List[Any]]:
        """Get all measurements for the class. Uses API call for Solara format."""

        res = self.query.get_class_data(class_id=self.query.class_id, exclude_merged=exclude_merged)
        if res is None or res == {} or len(res) == 0:
            res = {'student_id': []}
        return res if res is not None else {'student_id': []}
    
    def get_student_measurements(self, roster: List[OldRosterEntry], student_id: int) -> List[Dict[str, Any]]:
        """Get measurements for a specific student. Uses API call for Solara format."""

        result = self.query.get_student_data(student_id)
        return result.get('measurements', []) if result else []
    
    @property
    def version_name(self) -> str:
        return "monorepo"
    
    @property
    def state_class(self) -> type:
        return MonoRepoState  # Likely uses NewState (database has progress)


class StateAdapterFactory(StateAdapter):
    
    def __init__(self, query: QueryCosmicDSApi, class_id: int):
        self._adapter = None
        self.query = query
        self.class_id = class_id
    
    def get_adapter(self, api_roster, class_id: int) -> StateAdapter:
        if class_id < 215:
            logger.debug(f"Using LegacyStateAdapter for class {class_id}")
            return LegacyStateAdapter(self.query)
        
        if len(api_roster) == 0:
            logger.debug(f"API roster is empty for class {class_id}, defaulting adapter based on class_id")
            if class_id < 335:
                logger.debug(f"Using OldSolaraStateAdapter for class {class_id} (empty roster)")
                return OldSolaraStateAdapter(self.query)
            else:
                logger.debug(f"Using MonorepoStateAdapter for class {class_id} (empty roster)")
                return MonorepoStateAdapter(self.query)
        
        useMono = 'stage_states' in api_roster[0].get('story_state', {}).get('app', {}).get('story_state', {})
        if not useMono:
            logger.debug(f"Using OldSolaraStateAdapter for class {class_id}")
            return OldSolaraStateAdapter(self.query)
        else:
            logger.debug(f"Using MonorepoStateAdapter for class {class_id}")
            return MonorepoStateAdapter(self.query)
        
    def transform_roster(self, api_roster: List[Any]) -> List[OldRosterEntry]:
        self._adapter = self.get_adapter(api_roster, self.class_id)
        return self._adapter.transform_roster(api_roster)
    
    def get_class_measurements(self, roster: List[OldRosterEntry], exclude_merged: bool = False) -> Dict[str, List[Any]]:
        """Delegate to the underlying adapter."""
        if self._adapter is None:
            raise ValueError("Adapter not initialized. Call transform_roster first.")
        return self._adapter.get_class_measurements(roster, exclude_merged=exclude_merged)
    
    def get_student_measurements(self, roster: List[OldRosterEntry], student_id: int) -> List[Dict[str, Any]]:
        """Delegate to the underlying adapter."""
        if self._adapter is None:
            raise ValueError("Adapter not initialized. Call transform_roster first.")
        return self._adapter.get_student_measurements(roster, student_id)
    
    
        
    @property
    def version_name(self) -> str:
        if self._adapter is None:
            raise ValueError("Adapter not initialized. Call transform_roster first.")
        return self._adapter.version_name
    @property
    def state_class(self) -> type:
        if self._adapter is None:
            raise ValueError("Adapter not initialized. Call transform_roster first.")
        return self._adapter.state_class
        
        