"""Unit tests for the ALL vs ODD/EVEN overlap rule (double-booking protection).

Covers the risk "double booking" from the test strategy: an ALL slot runs every
week, so it overlaps both the ODD and the EVEN slot of the same day and pair,
while ODD and EVEN alone may share one.

These tests exercise the pure static helper only, so they need no database.
"""
import uuid

import pytest

from app.schemas.assignment import MicroserviceAssignment
from app.services.assignment_service import AssignmentService

TEACHER = uuid.UUID("11111111-1111-1111-1111-111111111111")
OTHER_TEACHER = uuid.UUID("22222222-2222-2222-2222-222222222222")
GROUP = uuid.UUID("33333333-3333-3333-3333-333333333333")
OTHER_GROUP = uuid.UUID("44444444-4444-4444-4444-444444444444")
ROOM = uuid.UUID("55555555-5555-5555-5555-555555555555")
OTHER_ROOM = uuid.UUID("66666666-6666-6666-6666-666666666666")
COURSE = uuid.UUID("77777777-7777-7777-7777-777777777777")


def _item(timeslot_id, *, teacher=TEACHER, group=GROUP, subgroup=0, room=ROOM):
    return MicroserviceAssignment(
        timeslot_id=timeslot_id,
        group_id=group,
        subgroup_no=subgroup,
        course_id=COURSE,
        teacher_id=teacher,
        room_id=room,
        course_type="lec",
    )


# timeslot_id -> (day, lesson, frequency)
SLOTS = {
    1: (1, 1, "ALL"),
    2: (1, 1, "ODD"),
    3: (1, 1, "EVEN"),
    4: (1, 2, "ALL"),   # same day, next pair
    5: (2, 1, "ALL"),   # next day, same pair
    6: (1, 1, "ALL"),   # duplicate of slot 1
    7: (1, 1, "ODD"),   # duplicate of slot 2
}


@pytest.mark.parametrize("second_slot", [2, 3], ids=["all-vs-odd", "all-vs-even"])
def test_all_overlaps_odd_and_even_in_the_same_pair(second_slot):
    clashes = AssignmentService._find_clashes(
        [_item(1), _item(second_slot)], SLOTS
    )

    assert clashes, "an ALL slot must clash with the ODD/EVEN slot of the same pair"


def test_odd_and_even_may_share_one_pair():
    clashes = AssignmentService._find_clashes([_item(2), _item(3)], SLOTS)

    assert clashes == []


@pytest.mark.parametrize(
    "slots", [(1, 6), (2, 7)], ids=["two-all", "two-odd"]
)
def test_same_frequency_twice_in_one_pair_clashes(slots):
    first, second = slots

    clashes = AssignmentService._find_clashes([_item(first), _item(second)], SLOTS)

    assert clashes


@pytest.mark.parametrize("other", [4, 5], ids=["next-pair", "next-day"])
def test_adjacent_pairs_and_other_days_do_not_overlap(other):
    clashes = AssignmentService._find_clashes([_item(1), _item(other)], SLOTS)

    assert clashes == []


def test_clash_is_reported_per_resource_kind():
    # one pair, one room/teacher/group each -> every resource key collides
    clashes = AssignmentService._find_clashes([_item(1), _item(2)], SLOTS)
    kinds = {c.split()[0] for c in clashes}

    assert kinds == {"teacher", "group", "room"}


def test_subgroups_of_one_group_may_share_a_pair():
    clashes = AssignmentService._find_clashes(
        [
            _item(1, subgroup=1, teacher=TEACHER, room=ROOM),
            _item(2, subgroup=2, teacher=OTHER_TEACHER, room=OTHER_ROOM),
        ],
        SLOTS,
    )

    assert clashes == []


def test_same_subgroup_twice_in_one_pair_clashes():
    clashes = AssignmentService._find_clashes(
        [
            _item(1, subgroup=1, teacher=TEACHER, room=ROOM),
            _item(2, subgroup=1, teacher=OTHER_TEACHER, room=OTHER_ROOM),
        ],
        SLOTS,
    )

    assert [c for c in clashes if c.startswith("group")]


def test_remote_lessons_without_a_room_do_not_clash_on_the_room():
    clashes = AssignmentService._find_clashes(
        [
            _item(1, teacher=TEACHER, group=GROUP, room=None),
            _item(2, teacher=OTHER_TEACHER, group=OTHER_GROUP, room=None),
        ],
        SLOTS,
    )

    assert clashes == []
