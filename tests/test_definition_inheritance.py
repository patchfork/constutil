from dataclasses import FrozenInstanceError, asdict, field, replace

import pytest

from constutil import ConstDef, ConstGroup, MutableConstDef


class StatusDef(ConstDef[int]):
    description: str


class DetailedStatusDef(StatusDef):
    priority: int = 0


class MutableStatusDef(MutableConstDef[int]):
    description: str


class DetailedMutableStatusDef(MutableStatusDef):
    tags: list[str] = field(default_factory=list)


def test_automatic_frozen_subclass_fields_and_inheritance():
    status = DetailedStatusDef(1, "Active", "Enabled", priority=2)
    assert asdict(status) == {"value": 1, "name": "Active", "description": "Enabled", "priority": 2}
    assert status == DetailedStatusDef(1, "Active", "Enabled", 2)
    assert hash(status) == hash(DetailedStatusDef(1, "Active", "Enabled", 2))
    assert status != replace(status, description="Disabled")
    assert "description='Enabled'" in repr(status)
    for attribute in ("value", "name", "description", "priority", "extra"):
        with pytest.raises(FrozenInstanceError):
            setattr(status, attribute, None)
        with pytest.raises(FrozenInstanceError):
            delattr(status, attribute)


def test_mutable_definitions_and_automatic_subclasses():
    base = MutableConstDef[str]("active", "Active")
    base.value = "inactive"
    assert base.value == "inactive"
    status = DetailedMutableStatusDef(1, "Active", "Enabled")
    status.value = 2
    status.description = "Changed"
    status.tags.append("new")
    assert asdict(status) == {
        "value": 2,
        "name": "Active",
        "description": "Changed",
        "tags": ["new"],
    }
    assert DetailedMutableStatusDef(1, "Active", "Enabled").tags == []
    with pytest.raises(TypeError, match="unhashable"):
        hash(status)
    del status.description
    assert not hasattr(status, "description")


def test_mutable_definition_group_lookup_tracks_field_changes():
    class Status(ConstGroup[MutableStatusDef]):
        ACTIVE = MutableStatusDef(1, "Active", "Enabled")

    Status.ACTIVE.value = 2
    assert Status.get_by_value(1) is None
    assert Status.get_by_value(2) is Status.ACTIVE


def test_frozen_metadata_is_shallow():
    class TagsDef(ConstDef[str]):
        tags: list[str] = field(default_factory=list)

    item = TagsDef("one", "One")
    item.tags.append("tag")
    assert item.tags == ["tag"]
    with pytest.raises(FrozenInstanceError):
        item.tags = []
