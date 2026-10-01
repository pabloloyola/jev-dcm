import math

from jev_dcm.axioms.iia import summarize_iia
from jev_dcm.menus import all_menus


def test_exact_mnl_has_zero_iia_span():
    utilities = {"A": 1.1, "B": 0.4, "C": -0.2, "D": 0.7}
    distributions = {}
    for menu in all_menus(tuple(utilities)):
        weights = {x: math.exp(utilities[x]) for x in menu}
        z = sum(weights.values())
        distributions[menu] = {x: weights[x] / z for x in menu}
    m = summarize_iia(distributions)
    assert m["iia_log_odds_span_mean"] < 1e-12
    assert m["iia_log_odds_span_max"] < 1e-12
