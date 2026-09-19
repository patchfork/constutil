"""Run from the repository root: uv run examples/days.py [day-number]."""

import argparse

from constutil import IntConstDef, IntConstGroup


class Day(IntConstGroup):
    MONDAY = IntConstDef(1, "Monday")
    TUESDAY = IntConstDef(2, "Tuesday")
    WEDNESDAY = IntConstDef(3, "Wednesday")
    THURSDAY = IntConstDef(4, "Thursday")
    FRIDAY = IntConstDef(5, "Friday")
    SATURDAY = IntConstDef(6, "Saturday")
    SUNDAY = IntConstDef(7, "Sunday")

    _default_constant = MONDAY


def main() -> None:
    parser = argparse.ArgumentParser(description="Look up a day using its integer value.")
    parser.add_argument("day", type=int, nargs="?", default=1)
    args = parser.parse_args()
    day = Day.get_by_value(args.day)
    if day is None:
        parser.error(f"Unknown day {args.day}; choose one of {Day.get_all_values()}")
    print(f"{day.value}: {day.name}")
    print(f"Weekend: {day in (Day.SATURDAY, Day.SUNDAY)}")
    print(f"All days: {Day.get_as_pairs()}")
    print(f"String '1' is valid: {Day.is_valid_value('1')}")
    print(f"Member named MONDAY exists: {Day.get_by_constant_name('MONDAY') is not None}")


if __name__ == "__main__":
    main()
