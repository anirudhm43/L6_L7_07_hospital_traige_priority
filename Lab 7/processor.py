
import math


def parse_vitals_summary(vitals_csv):
    """Parse patient vitals safely and generate a summary."""

    if not isinstance(vitals_csv, str):
        return None

    parts = vitals_csv.split(',')

    if len(parts) != 3:
        return None

    try:
        hr = float(parts[0].strip())
        spo2 = float(parts[1].strip())
        temp = float(parts[2].strip())
    except (ValueError, TypeError):
        return None

    # Reject NaN and infinity
    if not all(math.isfinite(x) for x in (hr, spo2, temp)):
        return None

    # Validate vital sign ranges
    if hr <= 0 or not 0 < spo2 <= 100 or temp <= 0:
        return None

    critical = hr > 120 or spo2 < 90 or temp > 39.0

    return (
        f"Vitals: HR={hr}, SpO2={spo2}% - "
        f"{'CRITICAL' if critical else 'STABLE'}"
    )


def compute_patient_bmi(bmi_string):
    """Calculate BMI safely after validating the input."""

    if not isinstance(bmi_string, str):
        return None

    parts = bmi_string.split('/')

    if len(parts) != 2:
        return None

    try:
        weight = float(parts[0].strip())
        height = float(parts[1].strip())
    except (ValueError, TypeError):
        return None

    # Reject NaN and infinity
    if not math.isfinite(weight) or not math.isfinite(height):
        return None

    # Weight and height must be positive
    if weight <= 0 or height <= 0:
        return None

    try:
        bmi = weight / (height ** 2)
        if not math.isfinite(bmi):
            return None
        return round(bmi, 2)
    except (ValueError, ZeroDivisionError, OverflowError):
        return None


def assign_ward_bed(allocation_code):
    """Safely validate ward and bed allocation."""

    if not isinstance(allocation_code, str):
        return None

    parts = allocation_code.strip().split('-')

    if len(parts) != 2:
        return None

    ward, bed_str = parts

    ward = ward.strip().upper()
    bed_str = bed_str.strip()

    ward_names = {
        "ER": "Emergency Room",
        "ICU": "Intensive Care Unit",
        "GEN": "General Ward",
        "PED": "Pediatrics"
    }

    # Validate ward code
    if ward not in ward_names:
        return None

    # Validate bed number
    if not bed_str.isdigit():
        return None

    bed_num = int(bed_str)

    if bed_num <= 0:
        return None

    return f"{ward_names[ward]} Bed #{bed_num}"


def main():
    print("==== Running parse_vitals_summary ====")
    v_input = input("Enter vitals (HR,SpO2,Temp): ")
    print("Summary:", parse_vitals_summary(v_input))

    print("\n==== Running compute_patient_bmi ====")
    b_input = input("Enter weight/height (e.g. 70/1.75): ")
    print("BMI:", compute_patient_bmi(b_input))

    print("\n==== Running assign_ward_bed ====")
    w_input = input("Enter allocation (e.g. ICU-05): ")
    print("Assignment:", assign_ward_bed(w_input))


if __name__ == "__main__":
    main()
