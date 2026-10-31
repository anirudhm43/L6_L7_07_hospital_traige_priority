
import pytest

from hospital_triage_priority import (
    process_triage_wards,
    monitor_oxygen_manifolds,
)


# --------------------------------------------------
# process_triage_wards() - Input validation
# --------------------------------------------------

def test_invalid_wards_type():
    with pytest.raises(ValueError):
        process_triage_wards("invalid", 10)


def test_negative_default_acuity():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


def test_invalid_wards_and_negative_score():
    with pytest.raises(ValueError):
        process_triage_wards("invalid", -1)


# --------------------------------------------------
# Ward acceptance and patient iteration
# --------------------------------------------------

def test_empty_wards():
    result = process_triage_wards([], 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_non_accepting_ward():
    wards = [{"is_accepting": False}]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_accepting_ward_without_patients():
    wards = [{"is_accepting": True, "patients": []}]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_default_ward_and_patient_values():
    wards = [{"is_accepting": True, "patients": [{}]}]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


# --------------------------------------------------
# Patient vital validation and acuity decisions
# --------------------------------------------------

def test_spo2_zero():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_heart_rate_zero():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 0}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_negative_spo2():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": -1, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_negative_heart_rate():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": -1}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_unconscious_general_patient():
    wards = [{
        "is_accepting": True,
        "tier": "general",
        "patients": [{"unconscious": True}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 100


def test_unconscious_outpatient():
    wards = [{
        "is_accepting": True,
        "tier": "outpatient",
        "patients": [{"unconscious": True}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0
    assert result["status"] == "NO_URGENT_CASES"


def test_low_spo2():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 89, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_high_heart_rate():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 121}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_normal_vitals():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 120}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


# --------------------------------------------------
# ICU standby and ward alert decisions
# --------------------------------------------------

def test_icu_standby_enabled():
    wards = [{
        "is_accepting": True,
        "icu_standby": True,
        "patients": [{"spo2": 98, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 35


def test_icu_standby_disabled():
    wards = [{
        "is_accepting": True,
        "icu_standby": False,
        "patients": [{"spo2": 98, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10


def test_exactly_four_flagged_entries():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0} for _ in range(4)],
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_more_than_four_flagged_entries():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 0} for _ in range(5)],
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"


def test_stable_triage_status():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 98, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "TRIAGE_STABLE"


# --------------------------------------------------
# monitor_oxygen_manifolds()
# --------------------------------------------------

def test_empty_sensor_streams():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


def test_normal_pressure():
    assert monitor_oxygen_manifolds([[5.0, 5.5, 6.0]]) == "PRESSURE_NORMAL"


def test_single_low_pressure_reading():
    assert monitor_oxygen_manifolds([[3.5, 5.0]]) == "PRESSURE_NORMAL"


def test_two_consecutive_low_readings():
    assert monitor_oxygen_manifolds([[3.5, 3.0]]) == "PRESSURE_FAILURE"


def test_low_readings_separated_by_normal_reading():
    streams = [[3.5, 5.0, 3.0, 5.0]]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_NORMAL"


def test_failure_in_second_manifold():
    streams = [
        [5.0, 5.5],
        [3.5, 3.0],
    ]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_FAILURE"


def test_empty_manifold():
    assert monitor_oxygen_manifolds([[]]) == "PRESSURE_NORMAL"


