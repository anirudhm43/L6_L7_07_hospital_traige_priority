
from hypothesis import given, strategies as st
from processor import parse_vitals_summary, compute_patient_bmi, assign_ward_bed



@given(st.text() | st.none())
def test_parse_vitals_summary_no_crash(s):
    try:
        parse_vitals_summary(s)
    except Exception as e:
        assert False, f"parse_vitals_summary crashed with input {s!r}: {e}"



@given(st.text() | st.none())
def test_compute_patient_bmi_safe(s):
    try:
        compute_patient_bmi(s)
    except Exception as e:
        assert False, f"compute_patient_bmi crashed with input {s!r}: {e}"



@given(st.text() | st.none())
def test_assign_ward_bed_safe(s):
    try:
        assign_ward_bed(s)
    except Exception as e:
        assert False, f"assign_ward_bed crashed with input {s!r}: {e}"
