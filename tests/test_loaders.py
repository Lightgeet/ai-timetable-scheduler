import pytest 

from src.data.loaders import parse_subject_requirements

def test_parse_requirements_without_duration():
    result=parse_subject_requirements("MATh101:4")

    assert len(result)==1
    assert result[0].subject_id=="MATH101"
    assert result[0].weekly_sessions==4
    assert result[0].duration_slots==1


def test_parse_multiple_requirements():
    result = parse_subject_requirements(
        "MATH101:4:1;CHEM101:1:2"
    )

    assert len(result) == 2
    assert result[0].weekly_sessions == 4
    assert result[1].duration_slots == 2


@pytest.mark.parametrize(
    "value",
    [
        "MATH101",
        "MATH101:abc",
        "MATH101:0",
        "MATH101:2:0",
        "MATH101:2:abc",
        "MATH101:2:1:3",
    ],
)

def test_invalid_subject_requirements_are_rejected(value):
    with pytest.raises(ValueError):
        parse_subject_requirements(value)