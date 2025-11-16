# Catalog
from .catalog.course import Course
from .catalog.group import Group
from .catalog.lesson import Lesson
from .catalog.room import Room

# Joins
from .joins.group_course import GroupCourse
from .joins.student_group import StudentGroup
from .joins.teacher_course import TeacherCourse

# People
from .people.admin import Admin
from .people.registration_request import RegistrationRequest, RegistrationStatus
from .people.student import Student
from .people.teacher import Teacher
from .people.user import User, UserRole

# Scheduling
from .scheduling.assignment import Assignment
from .scheduling.schedule import Schedule
from .scheduling.subgroup_constraints import SubgroupConstraints
from .scheduling.timeslot import Timeslot

# --- New Models ---
from .scheduling.teacher_availability import TeacherAvailability
from .scheduling.teacher_preference import TeacherPreference
from .scheduling.group_availability import GroupUnavailability
from .common_enums import CourseFrequency, TimeslotFrequency

__all__ = [
    # Catalog
    "Course",
    "Group",
    "Lesson",
    "Room",
    # Joins
    "GroupCourse",
    "StudentGroup",
    "TeacherCourse",
    # People
    "Admin",
    "RegistrationRequest",
    "RegistrationStatus",
    "Student",
    "Teacher",
    "User",
    "UserRole",
    # Scheduling
    "Assignment",
    "Schedule",
    "SubgroupConstraints",
    "Timeslot",
    # New
    "TeacherAvailability",
    "TeacherPreference",
    "GroupUnavailability",
    "CourseFrequency",
    "TimeslotFrequency",
]
