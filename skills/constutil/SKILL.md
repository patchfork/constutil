---
name: constutil
description: Define, organize, access, and validate related Python constants with constutil in projects adopting this convention. Use when adding or changing grouped constants, named choices, or constant metadata; not for unrelated configuration or isolated numeric literals.
---

# constutil conventions

In a project adopting this skill, always use `constutil` when grouping related
constant values. Use `ConstDef` for definitions and `ConstGroup` for groups,
including choices that might otherwise be represented by ad hoc dictionaries,
parallel lists, or enum-like classes. Honor an explicit requirement for another
representation or an external API that requires `enum.Enum`; do not migrate
unrelated existing code as a side effect.

## Place and name definitions

- Usually put groups in the application's `constants` package, for example
  `src/myapp/constants/days.py` or a domain's `constants/` package. Follow the
  existing package boundary and include `__init__.py`.
- Use focused snake_case modules (`days.py`, `saturn_moons.py`), singular PascalCase
  group names (`Day`, `SaturnMoon`), and UPPER_SNAKE_CASE members (`MONDAY`, `TITAN`).
- Name metadata records `<Domain>Def`, such as `MoonDef`. Reserve `_`-prefixed
  attributes for helpers and defaults; public matching records become members.
- Import public types from `constutil`. Use `IntConstDef`/`IntConstGroup` or
  `StrConstDef`/`StrConstGroup` for simple choices. For metadata, derive a frozen
  dataclass from `ConstDef[int]` or `ConstDef[str]`, then use `ConstGroup[ThatDef]`.
- Use direct generic derivations only. Do not derive one populated group from
  another or build extra generic base layers. Inherited members are not enumerated.
- Keep scalar values stable: they are the stored or exchanged identifiers. `.name`
  is display text, distinct from both `.value` and the class attribute name.

```python
# src/myapp/constants/days.py
from constutil import IntConstDef, IntConstGroup


class Day(IntConstGroup):
    MONDAY = IntConstDef(1, "Monday")
    TUESDAY = IntConstDef(2, "Tuesday")

    _default_constant = MONDAY
```

## Access, compare, and check existence

For a known constant, use `Day.MONDAY`, `Day.MONDAY.value`, or
`Day.MONDAY.name`. Import `Day` from its constants module, following the project's
absolute import convention. Pass `.value` at storage, JSON, and API boundaries;
use the definition object when metadata is useful. Do not scatter copied literals.

For an external value, look it up once and explicitly handle a missing result:

```python
member = Day.get_by_value(1)
if member is None:
    raise ValueError("Unknown day")
assert member.name == "Monday"
```

Choose the existence check matching the input:

| Input | Existence check or lookup |
| --- | --- |
| Stored value, e.g. `1` | `Day.is_valid_value(value)` or `Day.get_by_value(value) is not None` |
| Display name, e.g. `"Monday"` | `Day.get_by_name(name) is not None` |
| Attribute name, e.g. `"MONDAY"` | `Day.get_by_constant_name(name) is not None` |
| Definition object | `Day.is_valid(member)` (equality, not identity) |
| Member and expected scalar | `Day.is_value(member, value)` (does not validate membership) |

Do not use `hasattr(Day, input)` to validate membership: it also sees methods and
inherited attributes. Do not use truthiness of `.value`; `0` and `""` may be valid.
Do not compare a `ConstDef` directly to a scalar or use `value in Day`.

Comparisons use Python `==` with no coercion or case folding. `"1"` differs from
`1`, and `"Monday"` differs from `"monday"`. Python numeric equality still makes
`True` and `1.0` equal to `1`. If the application requires strict input types,
validate the type at its input boundary. Use `is None` for lookup misses.

`get_constant(value=None, name=None)` remains available: a positional argument is
a value, `name=` searches display text, non-None value wins if both are supplied,
and neither raises `ValueError`. Do not pass a display name positionally.

## Enumerate and avoid helper traps

- Use `get_all()` for member tuples, `get_all_values()` for scalar tuples,
  `get_as_pairs()` for value/display-name tuples, and `get_all_map()` for a fresh
  attribute-name/member dictionary. Order follows declaration order.
- `get_all_names()` returns display names; `get_all_constant_names()` returns
  Python attribute names. `get_name(value)` and `get_value(name)` return `None`
  for a missing match. The latter and bulk scalar APIs return `int | str`; use a
  typed member's `.value` when a narrower scalar type matters.
- `get_filtered(items)` only copies its input. To filter for membership, write
  `[item for item in items if Day.is_valid(item)]`.
- `get_filtered_as_pairs(items)` accepts foreign members and stringifies their
  values. Use `get_as_pairs()` when original scalar types should be preserved.
- `has_required(values)` checks exact set equality, not subset containment. For
  “all requested values exist”, use `all(Day.is_valid_value(v) for v in values)`.
- Prefer unique values and names within an application group. The library permits
  duplicates and returns the first matching declaration. It does not enforce
  singleton identity, runtime constructor types, or group immutability.

Check tests for valid and unknown inputs, case differences, scalar type mismatches,
and zero/empty values when applicable. Do not silently choose a default on invalid
input unless that behavior is part of the application's contract.
