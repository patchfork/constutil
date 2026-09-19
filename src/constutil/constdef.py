"""Typed definitions for named constants."""

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar

ValueT = TypeVar("ValueT", int, str)


class ConstantMember(Protocol):
    """The structural interface required by a constant group."""

    @property
    def value(self) -> int | str: ...

    @property
    def name(self) -> str: ...


@dataclass(frozen=True)
class ConstDef(Generic[ValueT]):
    """A scalar value and its display name; subclass to add metadata."""

    value: ValueT
    name: str


IntConstDef = ConstDef[int]
StrConstDef = ConstDef[str]
