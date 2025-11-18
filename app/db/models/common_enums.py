import enum
from sqlalchemy import Enum as SQLEnum


class CourseFrequency(str, enum.Enum):
    """
    Frequency for a course, e.g., weekly or bi-weekly.
    """
    WEEKLY = "WEEKLY"
    ODD = "ODD"
    EVEN = "EVEN"


class TimeslotFrequency(str, enum.Enum):
    """
    Frequency for a timeslot, distinguishing 'all' weeks from 'odd'/'even'.
    """
    ALL = "ALL"
    ODD = "ODD"
    EVEN = "EVEN"


class CourseType(str, enum.Enum):
    """
    Type of class (lecture, practical, lab).
    """
    LEC = "LEC"
    PRAC = "PRAC"
    LAB = "LAB"


CourseFrequencyEnum = SQLEnum(
    CourseFrequency,
    name="course_frequency_enum",
    create_type=True
)

TimeslotFrequencyEnum = SQLEnum(
    TimeslotFrequency,
    name="timeslot_frequency_enum",
    create_type=True
)

CourseTypeSQLEnum = SQLEnum(
    CourseType,
    name="course_type_enum",
    create_type=True
)
