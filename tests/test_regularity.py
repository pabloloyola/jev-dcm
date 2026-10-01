from jev_dcm.axioms.regularity import regularity_violations


def test_constructed_regularity_violation_is_found():
    d = {
        ("A", "B"): {"A": 0.4, "B": 0.6},
        ("A", "B", "C"): {"A": 0.55, "B": 0.25, "C": 0.20},
    }
    violations = regularity_violations(d)
    assert any(v["option"] == "A" and abs(v["delta"] - 0.15) < 1e-12 for v in violations)
