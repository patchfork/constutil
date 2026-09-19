"""Ordered groups of typed constant definitions."""

from collections.abc import Iterable
from typing import Any, Generic, TypeVar, cast, get_args, get_origin

from .constdef import ConstantMember, IntConstDef, StrConstDef

MemberT = TypeVar("MemberT", bound=ConstantMember)


class ConstGroup(Generic[MemberT]):
    """Discover public members declared directly on a specialized group class.

    Derive from ``ConstGroup[YourDefinition]`` or a specialized alias. Extending
    populated groups and additional generic inheritance layers are unsupported.
    """

    _default_constant: MemberT | None = None

    @classmethod
    def get_default(cls) -> MemberT | None:
        return cls._default_constant

    @classmethod
    def _get_constant_type(cls) -> Any:
        for base in cls.__mro__:
            for original in base.__dict__.get("__orig_bases__", ()):
                if get_origin(original) is ConstGroup:
                    return get_args(original)[0]
        raise TypeError("Declare a group as ConstGroup[YourDefinition].")

    @classmethod
    def get_all_map(cls) -> dict[str, MemberT]:
        """Return a fresh mapping in class declaration order."""
        expected = cls._get_constant_type()
        member_type = get_origin(expected) or expected
        inner_args = get_args(expected)
        members = {}
        for key, member in cls.__dict__.items():
            if key.startswith("_") or not isinstance(member, member_type):
                continue
            if inner_args and not isinstance(member.value, inner_args[0]):
                continue
            members[key] = cast(MemberT, member)
        return members

    @classmethod
    def get_all(cls) -> tuple[MemberT, ...]:
        return tuple(cls.get_all_map().values())

    @classmethod
    def get_all_values(cls) -> tuple[int | str, ...]:
        return tuple(member.value for member in cls.get_all())

    @classmethod
    def get_all_names(cls) -> tuple[str, ...]:
        return tuple(member.name for member in cls.get_all())

    @classmethod
    def get_all_constant_names(cls) -> tuple[str, ...]:
        return tuple(cls.get_all_map())

    @classmethod
    def get_as_pairs(cls) -> tuple[tuple[int | str, str], ...]:
        return tuple((member.value, member.name) for member in cls.get_all())

    @classmethod
    def get_constant(cls, value: object = None, name: str | None = None) -> MemberT | None:
        """Look up a value, or a display name when value is None.

        A positional argument is always a value. A non-None value takes
        precedence over name. Missing matches return None.
        """
        if value is not None:
            return cls.get_by_value(value)
        if name is not None:
            return cls.get_by_name(name)
        raise ValueError("Need one of value or name to filter by")

    @classmethod
    def get_by_value(cls, value: object) -> MemberT | None:
        return next((member for member in cls.get_all() if member.value == value), None)

    @classmethod
    def get_by_name(cls, name: str) -> MemberT | None:
        return next((member for member in cls.get_all() if member.name == name), None)

    @classmethod
    def get_by_constant_name(cls, constant_name: str) -> MemberT | None:
        return cls.get_all_map().get(constant_name)

    @classmethod
    def get_name(cls, value: object) -> str | None:
        member = cls.get_by_value(value)
        return member.name if member is not None else None

    @classmethod
    def get_value(cls, name: str) -> int | str | None:
        member = cls.get_by_name(name)
        return member.value if member is not None else None

    @classmethod
    def is_valid(cls, constant: object) -> bool:
        return constant in cls.get_all()

    @classmethod
    def is_valid_value(cls, value: object) -> bool:
        return cls.get_by_value(value) is not None

    @classmethod
    def is_value(cls, constant: MemberT, value: object) -> bool:
        return constant.value == value

    @classmethod
    def get_filtered(cls, filtered_list: Iterable[MemberT]) -> list[MemberT]:
        """Copy the supplied members; this does not validate group membership."""
        return list(filtered_list)

    @classmethod
    def get_filtered_as_pairs(cls, filtered_list: Iterable[MemberT]) -> list[tuple[str, str]]:
        """Return the supplied members as string-value/display-name pairs."""
        return [(str(member.value), member.name) for member in filtered_list]

    @classmethod
    def has_required(cls, values: Iterable[int | str]) -> bool:
        """Check exact set equality, ignoring order and duplicates."""
        return set(values) == set(cls.get_all_values())


IntConstGroup = ConstGroup[IntConstDef]
StrConstGroup = ConstGroup[StrConstDef]
