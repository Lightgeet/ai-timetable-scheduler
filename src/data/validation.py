from src.models.entities import SchedulingProblem


def validate_timetable_input(
    problem: SchedulingProblem,
) -> list[str]:
    """Return a list of input-data errors."""

    errors = []

    collections = {
        "Subject": problem.subjects,
        "Teacher": problem.teachers,
        "Class": problem.student_groups,
        "Room": problem.rooms,
    }

    for entity_name, entities in collections.items():
        ids = [entity.id for entity in entities]

        if len(ids) != len(set(ids)):
            errors.append(
                f"Duplicate IDs found in {entity_name} records."
            )

    subject_ids = {
        subject.id for subject in problem.subjects
    }


    for teacher in problem.teachers:
        for subject_id in teacher.subjects_can_teach:
            if subject_id not in subject_ids:
                errors.append(
                    f"Teacher {teacher.id} references "
                    f"unknown subject {subject_id}."
                )

    for group in problem.student_groups:
        if group.strength <= 0:
            errors.append(
                f"Class {group.id} must have positive strength."
            )

        for requirement in group.subject_requirements:
            if requirement.subject_id not in subject_ids:
                errors.append(
                    f"Class {group.id} references unknown "
                    f"subject {requirement.subject_id}."
                )

            if requirement.weekly_sessions <= 0:
                errors.append(
                    f"Class {group.id}: weekly sessions "
                    f"must be positive."
                )

    for room in problem.rooms:
        if room.capacity <= 0:
            errors.append(
                f"Room {room.id} must have positive capacity."
            )

    settings = problem.time_structure

    if not settings.working_days:
        errors.append("At least one working day is required.")

    if settings.periods_per_day <= 0:
        errors.append("Periods per day must be positive.")

    return errors