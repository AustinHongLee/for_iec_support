import json
from copy import deepcopy
from pathlib import Path

from core.config_sanity import check_config_sanity, existing_schedule_values


CONFIG_DIR = Path(__file__).resolve().parents[1] / "configs"


def _config(table, **extra):
    return {"type_id": "99", "name": "test", "table": table, **extra}


def test_l_must_be_non_decreasing():
    issues = check_config_sanity(
        _config([
            {"line_size": 2, "L": 100},
            {"line_size": 3, "L": 90},
        ]),
        allowed_schedules=set(),
    )
    assert any(issue.code == "L_NOT_MONOTONIC" for issue in issues)


def test_numeric_values_must_be_positive():
    issues = check_config_sanity(
        _config([{"line_size": 2, "L": 0}]),
        allowed_schedules=set(),
    )
    assert any(issue.code == "NON_POSITIVE_NUMBER" for issue in issues)


def test_schedule_must_come_from_existing_set():
    issues = check_config_sanity(
        _config([{"line_size": 2, "schedule": "SCH.999", "L": 10}]),
        allowed_schedules={"SCH.40", "SCH.80", "STD.WT"},
    )
    assert any(issue.code == "UNKNOWN_SCHEDULE" for issue in issues)


def test_large_change_is_confirmation_warning():
    original = _config([{"line_size": 2, "L": 100}])
    candidate = deepcopy(original)
    candidate["table"][0]["L"] = 140
    issues = check_config_sanity(
        candidate,
        original=original,
        allowed_schedules=set(),
    )
    issue = next(issue for issue in issues if issue.code == "LARGE_CHANGE")
    assert issue.severity == "warning"


def test_all_existing_numeric_type_configs_are_sanity_clean():
    schedules = existing_schedule_values(CONFIG_DIR)
    assert schedules == {"SCH.40", "SCH.80", "STD.WT"}

    failures = {}
    for path in sorted(CONFIG_DIR.glob("type_[0-9][0-9].json")):
        config = json.loads(path.read_text(encoding="utf-8"))
        issues = check_config_sanity(config, allowed_schedules=schedules)
        if issues:
            failures[path.name] = issues

    assert failures == {}
