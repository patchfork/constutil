import re
from dataclasses import FrozenInstanceError, dataclass
from pathlib import Path
from typing import Generic, TypeVar

import pytest

from constutil import ConstDef, ConstGroup, IntConstDef, IntConstGroup, StrConstDef, StrConstGroup


class Day(IntConstGroup):
    MONDAY = IntConstDef(1, "Monday")
    TUESDAY = IntConstDef(2, "Tuesday")
    _default_constant = MONDAY
    _hidden = IntConstDef(0, "Hidden")
    description = "Days"
    wrong = StrConstDef("wrong", "Wrong")


class Moon(StrConstGroup):
    TITAN = StrConstDef("titan", "Titan")
    RHEA = StrConstDef("rhea", "Rhea")


def test_definition_frozen_equality_and_hash():
    first = IntConstDef(1, "Monday")
    assert first == Day.MONDAY
    assert hash(first) == hash(Day.MONDAY)
    assert first != IntConstDef(1, "Other")
    with pytest.raises(FrozenInstanceError):
        first.value = 2


def test_enumeration_and_default():
    assert Day.get_all() == (Day.MONDAY, Day.TUESDAY)
    assert Day.get_all_values() == (1, 2)
    assert Day.get_all_names() == ("Monday", "Tuesday")
    assert Day.get_all_constant_names() == ("MONDAY", "TUESDAY")
    assert Day.get_as_pairs() == ((1, "Monday"), (2, "Tuesday"))
    assert Day.get_default() is Day.MONDAY
    assert Moon.get_default() is None
    mapping = Day.get_all_map()
    mapping.clear()
    assert len(Day.get_all()) == 2


@pytest.mark.parametrize(
    "value,expected",
    [(1, True), ("1", False), (True, True), (1.0, True), (0, False), (None, False)],
)
def test_value_comparisons_agree(value, expected):
    assert Day.is_valid_value(value) is expected
    assert Day.is_value(Day.MONDAY, value) is expected
    assert (Day.get_by_value(value) is Day.MONDAY) is expected
    assert (Day.get_name(value) == "Monday") is expected
    if value is not None:
        assert (Day.get_constant(value) is Day.MONDAY) is expected


@pytest.mark.parametrize(
    "value,expected", [("titan", True), ("TITAN", False), (" titan", False), (1, False)]
)
def test_string_comparisons_agree(value, expected):
    assert Moon.is_valid_value(value) is expected
    assert Moon.is_value(Moon.TITAN, value) is expected
    assert (Moon.get_by_value(value) is Moon.TITAN) is expected
    assert (Moon.get_constant(value=value) is Moon.TITAN) is expected
    assert (Moon.get_name(value) == "Titan") is expected


@pytest.mark.parametrize(
    "name,expected",
    [("Monday", True), ("monday", False), ("MONDAY", False), ("Monday ", False), ("", False)],
)
def test_display_name_comparisons_agree(name, expected):
    assert (Day.get_by_name(name) is Day.MONDAY) is expected
    assert (Day.get_constant(name=name) is Day.MONDAY) is expected
    assert (Day.get_value(name) == 1) is expected


def test_combined_lookup_and_attribute_names():
    assert Day.get_constant(1, "Tuesday") is Day.MONDAY
    assert Day.get_constant("Monday") is None
    assert Day.get_constant(None, "Monday") is Day.MONDAY
    assert Day.get_constant(0, "Monday") is None
    with pytest.raises(ValueError, match="Need one of"):
        Day.get_constant()
    assert Day.get_by_constant_name("MONDAY") is Day.MONDAY
    assert Day.get_by_constant_name("Monday") is None
    assert Day.get_by_constant_name("get_all") is None
    assert Day.get_by_constant_name("_hidden") is None


def test_membership_uses_equality():
    assert Day.is_valid(IntConstDef(1, "Monday"))
    assert not Day.is_valid(IntConstDef(1, "Other"))
    assert not Day.is_valid(1)


def test_preserved_helpers():
    foreign = IntConstDef(9, "Foreign")
    members = [Day.TUESDAY, foreign, Day.TUESDAY]
    assert Day.get_filtered(iter(members)) == members
    assert Day.get_filtered(members) is not members
    assert Day.get_filtered_as_pairs(members) == [
        ("2", "Tuesday"),
        ("9", "Foreign"),
        ("2", "Tuesday"),
    ]
    assert Day.has_required([2, 1, 1])
    assert not Day.has_required([1])
    assert not Day.has_required([1, 2, 3])
    assert not Day.has_required(["1", "2"])
    assert Day.is_value(foreign, 9)


def test_metadata_and_structural_members():
    @dataclass(frozen=True, slots=True)
    class MoonDef(ConstDef[str]):
        discovery_year: int

    class Saturn(ConstGroup[MoonDef]):
        TITAN = MoonDef("titan", "Titan", 1655)

    assert Saturn.get_by_value("titan").discovery_year == 1655

    @dataclass
    class MutableDef:
        value: int
        name: str

    class Custom(ConstGroup[MutableDef]):
        FIRST = MutableDef(1, "First")

    assert Custom.get_all() == (Custom.FIRST,)
    Custom.FIRST.value = 2
    assert Custom.get_by_value(1) is None
    assert Custom.get_by_value(2) is Custom.FIRST


def test_duplicates_and_changes():
    class Duplicate(IntConstGroup):
        FIRST = IntConstDef(1, "First")
        ALIAS = FIRST
        SAME_VALUE = IntConstDef(1, "Other")
        SAME_NAME = IntConstDef(2, "First")

    assert len(Duplicate.get_all()) == 4
    assert Duplicate.get_by_value(1) is Duplicate.FIRST
    assert Duplicate.get_by_name("First") is Duplicate.FIRST
    Duplicate.FIRST = IntConstDef(3, "New")
    assert Duplicate.get_all_values() == (3, 1, 1, 2)


def test_empty_and_inheritance_boundary():
    class Empty(StrConstGroup):
        pass

    assert Empty.get_all() == ()
    assert Empty.has_required([])
    assert Empty.get_by_name("none") is None

    class Child(Day):
        WEDNESDAY = IntConstDef(3, "Wednesday")

    assert Child.MONDAY is Day.MONDAY
    assert Child.get_all() == (Child.WEDNESDAY,)
    assert Child.get_by_value(1) is None


def test_unrelated_generic_mixin():
    T = TypeVar("T")

    class Mixin(Generic[T]):
        pass

    class Mixed(Mixin[int], ConstGroup[StrConstDef]):
        FIRST = StrConstDef("first", "First")

    assert Mixed.get_all() == (Mixed.FIRST,)


def test_missing_specialization():
    with pytest.raises(TypeError, match="ConstGroup"):
        ConstGroup.get_all()


def test_readme_examples():
    readme = (Path(__file__).resolve().parents[1] / "README.md").read_text()
    blocks = re.findall(r"```python\n(.*?)```", readme, re.DOTALL)
    assert len(blocks) == 3
    for block in blocks:
        exec(compile(block, "README.md", "exec"), {})
