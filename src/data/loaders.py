
import pandas as pd

from src.models.entities import (
    Subject,
    SubjectRequirement,
    Teacher,
    StudentGroup,
    Room,
    TimeStructure,
    SchedulingProblem,
)


def parse_list(value):
    """Convert a semicolon-separated CSV cell into a list."""
    if pd.isna(value) or not str(value).strip():
        return []

    return [
        item.strip()
        for item in str(value).split(";")
        if item.strip()
    ]


def parse_periods(value):
    """Convert P1;P2 into [1, 2]."""
    periods = []

    for item in parse_list(value):
        if not item.startswith("P") or not item[1:].isdigit():
            raise ValueError(f"Invalid period format: {item}")

        periods.append(int(item[1:]))

    return periods


def parse_subject_requirements(value):
    requirements = []

    for item in parse_list(value):
        parts = [part.strip() for part in item.split(":")]

        if len(parts) not in (2, 3):
            raise ValueError(
                f"Invalid subject requirement {item!r}."
            )

        subject_id = parts[0].upper()
        weekly_sessions = int(parts[1])
        duration_slots = int(parts[2]) if len(parts) == 3 else 1

        if weekly_sessions < 1 or duration_slots < 1:
            raise ValueError(
                "Weekly sessions and duration slots must be positive."
            )

        requirements.append(
            SubjectRequirement(
                subject_id=subject_id,
                weekly_sessions=weekly_sessions,
                duration_slots=duration_slots,
            )
        )

    return requirements


def load_timetable_csv(file):
    """Convert a single CSV into a SchedulingProblem."""

    df = pd.read_csv(file, dtype=str).fillna("")

    required_columns = {
        "record_type",
        "id",
        "name",
    }

    missing = required_columns - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    df["record_type"] = (
        df["record_type"].str.strip().str.lower()
    )
    df["id"] = df["id"].str.strip()
    df["name"] = df["name"].str.strip()

    subjects = []
    teachers = []
    groups = []
    rooms = []
    time_structure = None

    for row_number, row in enumerate(
        df.to_dict(orient="records"), start=2
    ):
        kind = row["record_type"]
        record_id = row["id"]
        name = row["name"]

        try:
            if kind == "subject":
                subjects.append(
                    Subject(
                        id=record_id,
                        name=name,
                        subject_type=(
                            (row.get("subject_type") or "theory").strip().lower()
                        ),
                    )
                )

            elif kind == "teacher":
                teachers.append(
                    Teacher(
                        id=record_id,
                        name=name,
                        subjects_can_teach=parse_list(
                            row.get("subjects_can_teach", "")
                        ),
                        unavailable_slots=parse_list(
                            row.get("unavailable_slots", "")
                        ),
                        maximum_weekly_load=int(
                            row.get("maximum_weekly_load") or 20
                        ),
                    )
                )

            elif kind=="class":
                requirements=parse_subject_requirements(
                    row.get("subject_ids","")
                )

                groups.append(
                    StudentGroup(
                        id=record_id,
                        name=name,
                        strength=int(row.get("strength") or 0),
                        subject_requirements=requirements,
                        lunch_break_periods=parse_periods(
                            row.get("lunch_break_slot", "")
                        ),
                    )
                )

            elif kind == "room":
                rooms.append(
                    Room(
                        id=record_id,
                        name=name,
                        capacity=int(row.get("capacity") or 0),
                        room_type=(
                            (row.get("room_type") or "classroom").strip().lower()
                        ),
                    )
                )

            elif kind == "settings":
                if time_structure is not None:
                    raise ValueError(
                        "Only one settings record is allowed"
                    )

                time_structure = TimeStructure(
                    working_days=parse_list(
                        row.get("working_days", "")
                    ),
                    periods_per_day=int(
                        row.get("periods_per_day") or 0
                    ),
                    break_periods=parse_periods(
                        row.get("break_periods", "")
                    ),
                    period_duration_minutes=int(
                        row.get("period_duration_minutes") or 50
                    ),
                )

            else:
                raise ValueError(
                    f"Unknown record type: {kind!r}"
                )

        except (ValueError, TypeError) as exc:
            raise ValueError(
                f"CSV row {row_number}: {exc}"
            ) from exc

    if time_structure is None:
        raise ValueError("CSV must contain a settings record.")

    return SchedulingProblem(
        subjects=subjects,
        teachers=teachers,
        student_groups=groups,
        rooms=rooms,
        time_structure=time_structure,
    )
