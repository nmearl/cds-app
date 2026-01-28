"""
Common types shared across database versions.
These types are used by both legacy (database/) and new (database_new/) implementations.
"""

from typing import Dict, List, Optional, Union, Any, Protocol, TypedDict


# ============================================================================
# Student and Roster Entry Types
# ============================================================================

class StudentInfo(TypedDict):
    """Type for basic student information (common across all versions)"""
    username: str
    email: str
    name: Optional[str]  # Added through set_student_names method


class RosterEntry(TypedDict):
    """Base type for a student entry in roster (common structure)"""
    student_id: int
    story_name: str
    story_state: Dict[str, Any]  # Structure varies by version
    last_modified: str
    student: StudentInfo
    app_state: Optional[Dict[str, Any]]


# ============================================================================
# Multiple Choice Scoring Types
# ============================================================================

class MCScore(TypedDict, total=False):
    """Type for multiple-choice question score (common format)"""
    score: Optional[int]
    tries: int
    choice: Optional[int]


# ============================================================================
# Stage Progress Types
# ============================================================================

class StageProgress(TypedDict):
    """Type for per-stage progress data"""
    name: str
    index: Optional[int]
    progress: Optional[float]


# ============================================================================
# State Interface Protocol
# ============================================================================

class StateInterface(Protocol):
    """
    Common interface for both State implementations (State and NewState).
    
    This protocol ensures that components can work with either database version
    by accessing the same properties and methods, even though the underlying
    data structures differ.
    """
    story_state: Any
    stages: Dict[str, Any]
    responses: Dict[str, Any]
    mc_scoring: Dict[str, Dict[str, MCScore]]
    max_stage_index: int
    has_best_fit_galaxy: bool
    stage_map: Dict[int, str]
    stage_names: List[str]
    
    def get_possible_score(self) -> int: ...
    def stage_name_to_index(self, name: str) -> Optional[int]: ...
    def stage_fraction_completed(self, stage) -> Union[float, None]: ...
    def total_fraction_completed(self) -> Dict[str, Union[float, int]]: ...
    
    @property
    def possible_score(self) -> int: ...
    @property
    def story_score(self) -> int: ...
    @property
    def how_far(self) -> Dict[str, Union[str, float]]: ...
    @property
    def progress_dict(self) -> Dict[str, StageProgress]: ...
    @property
    def current_marker(self) -> Union[str, float]: ...
    @property
    def max_marker(self) -> Union[str, float, int]: ...
    @property
    def percent_completion(self) -> float: ...
    @property
    def stage_index(self) -> int: ...
