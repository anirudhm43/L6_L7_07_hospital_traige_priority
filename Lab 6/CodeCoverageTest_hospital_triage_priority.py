
import pytest

from hospital_triage_priority import (
    process_triage_wards,
    monitor_oxygen_manifolds,
)


def test_invalid_wards_input():
    with pytest.raises(ValueError):
        process_triage_wards("invalid", 10)


def test_negative_default_acuity():
    with pytest.raises(ValueError):
        process_triage_wards([], -1)


def test_empty_wards():
    result = process_triage_wards([], 10)
    assert result == {
        "acuity_score": 0,
        "status": "NO_URGENT_CASES",
    }


def test_non_accepting_ward():
    wards = [{"is_accepting": False}]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "NO_URGENT_CASES"


def test_normal_patient():
    wards = [{
        "is_accepting": True,
        "tier": "general",
        "patients": [
            {"spo2": 98, "hr": 75, "unconscious": False}
        ],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 10
    assert result["status"] == "TRIAGE_STABLE"


def test_low_oxygen_patient():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 85, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_high_heart_rate_patient():
    wards = [{
        "is_accepting": True,
        "patients": [{"spo2": 95, "hr": 130}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 60


def test_unconscious_patient():
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
        "icu_standby": False,
        "patients": [{"unconscious": True}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0
    assert result["status"] == "NO_URGENT_CASES"


def test_invalid_patient_vitals():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": 0, "hr": 75},
            {"spo2": 95, "hr": 0},
        ],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 0


def test_ward_alert():
    wards = [{
        "is_accepting": True,
        "patients": [
            {"spo2": 0} for _ in range(5)
        ],
    }]
    result = process_triage_wards(wards, 10)
    assert result["status"] == "WARD_ALERT"


def test_icu_standby():
    wards = [{
        "is_accepting": True,
        "icu_standby": True,
        "patients": [{"spo2": 98, "hr": 75}],
    }]
    result = process_triage_wards(wards, 10)
    assert result["acuity_score"] == 35


def test_no_oxygen_sensor_data():
    assert monitor_oxygen_manifolds([]) == "NO_DATA"


def test_oxygen_pressure_failure():
    streams = [[5.0, 3.5, 3.0]]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_FAILURE"


def test_oxygen_pressure_normal():
    streams = [[5.0, 3.5, 4.5, 5.0]]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_NORMAL"


def test_oxygen_single_low_reading():
    streams = [[3.5, 5.0]]
    assert monitor_oxygen_manifolds(streams) == "PRESSURE_NORMAL"
