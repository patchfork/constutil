from dataclasses import FrozenInstanceError

import pytest

from constutil import (
    ConstGroup,
    IntConstDef,
    IntConstGroup,
    MutableConstDef,
    MutableConstGroup,
    StrConstDef,
    StrConstGroup,
)


@pytest.mark.parametrize("base", [IntConstGroup, ConstGroup[IntConstDef]])
def test_frozen_group_seals_members_defaults_and_helpers(base):
    class Day(base):
        MONDAY = IntConstDef(1, "Monday")
        _default_constant = MONDAY
        description = "Days"

    for name in (
        "MONDAY",
        "TUESDAY",
        "_default_constant",
        "description",
        "get_all",
        "_constutil_sealed",
        "__bases__",
    ):
        with pytest.raises(TypeError, match="is frozen; cannot assign"):
            setattr(Day, name, None)
        with pytest.raises(TypeError, match="is frozen; cannot delete"):
            delattr(Day, name)
    assert Day.get_all() == (Day.MONDAY,)
    assert Day.get_default() is Day.MONDAY
    assert Day.description == "Days"
    mapping = Day.get_all_map()
    mapping.clear()
    assert Day.get_all_values() == (1,)


def test_string_group_and_public_frozen_base_are_sealed():
    class Season(StrConstGroup):
        SPRING = StrConstDef("spring", "Spring")

    assert Season.get_by_value("spring") is Season.SPRING
    for group in (Season, ConstGroup):
        with pytest.raises(TypeError, match="is frozen"):
            group.extra = None


def test_mutable_group_changes_and_frozen_members():
    class Day(MutableConstGroup[IntConstDef]):
        MONDAY = IntConstDef(1, "Monday")
        _default_constant = MONDAY

    Day.MONDAY = IntConstDef(3, "Changed")
    Day.TUESDAY = IntConstDef(2, "Tuesday")
    Day._default_constant = Day.TUESDAY
    assert Day.get_all_values() == (3, 2)
    assert Day.get_by_value(1) is None
    assert Day.get_default() is Day.TUESDAY
    with pytest.raises(FrozenInstanceError):
        Day.MONDAY.value = 4
    del Day.MONDAY
    del Day._default_constant
    assert Day.get_all() == (Day.TUESDAY,)
    assert Day.get_default() is None
    assert not issubclass(MutableConstGroup, ConstGroup)


@pytest.mark.parametrize("base", [ConstGroup, MutableConstGroup])
def test_member_mutability_is_independent(base):
    class Status(base[MutableConstDef[int]]):
        ACTIVE = MutableConstDef(1, "Active")

    Status.ACTIVE.value = 2
    assert Status.get_by_value(1) is None
    assert Status.get_by_value(2) is Status.ACTIVE


def test_mutable_string_specialization_filters_wrong_value_types():
    class Status(MutableConstGroup[StrConstDef]):
        ACTIVE = StrConstDef("active", "Active")
        WRONG = IntConstDef(1, "Wrong")

    assert Status.get_all() == (Status.ACTIVE,)
    Status.OTHER = StrConstDef("other", "Other")
    assert Status.get_all_values() == ("active", "other")


def test_mutable_group_requires_specialization():
    with pytest.raises(TypeError, match="MutableConstGroup"):
        MutableConstGroup.get_all()
