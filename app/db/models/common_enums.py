import enum
from sqlalchemy import Enum as SQLEnum


class CourseFrequency(str, enum.Enum):
    """
    Frequency for a course, e.g., weekly or bi-weekly.
    """
    WEEKLY = "weekly"
    ODD = "odd"
    EVEN = "even"


class TimeslotFrequency(str, enum.Enum):
    """
    Frequency for a timeslot, distinguishing 'all' weeks from 'odd'/'even'.
    """
    ALL = "all"
    ODD = "odd"
    EVEN = "even"


class CourseType(str, enum.Enum):
    """
    Type of class (lecture, practical, lab).
    """
    LEC = "lec"
    PRAC = "prac"
    LAB = "lab"


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
