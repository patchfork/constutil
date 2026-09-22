"""Typed definitions for named constants."""

from dataclasses import dataclass
from typing import Generic, Protocol, TypeVar, dataclass_transform

ValueT = TypeVar("ValueT", int, str)


class ConstantMember(Protocol):
    """The structural interface required by a constant group."""

    @property
    def value(self) -> int | str: ...

    @property
    def name(self) -> str: ...


@dataclass_transform(frozen_default=True)
@dataclass(frozen=True)
class ConstDef(Generic[ValueT]):
    """A frozen value and display name; subclasses are automatically frozen dataclasses."""

    value: ValueT
    name: str

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        dataclass(cls, frozen=True)


@dataclass_transform()
@dataclass
class MutableConstDef(Generic[ValueT]):
    """A writable value and display name; subclasses are automatically mutable dataclasses."""

    value: ValueT
    name: str

    def __init_subclass__(cls, **kwargs: object) -> None:
        super().__init_subclass__(**kwargs)
        dataclass(cls)


IntConstDef = ConstDef[int]
StrConstDef = ConstDef[str]
