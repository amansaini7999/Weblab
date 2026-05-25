from enum import Enum


class AssignmentMode(str, Enum):
    SESSION_BASED = "session_based"
    USER_BASED = "user_based"
