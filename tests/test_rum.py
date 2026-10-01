import itertools

from jev_dcm.axioms.rum import rum_distance
from jev_dcm.menus import all_menus


def _from_ranking_mixture(alts, mixture):
    d = {}
    for menu in all_menus(alts):
        p = {x: 0.0 for x in menu}
        for ranking, weight in mixture:
            rank = {x: i for i, x in enumerate(ranking)}
            winner = min(menu, key=rank.__getitem__)
            p[winner] += weight
        d[menu] = p
    return d


def test_exact_random_ranking_model_has_zero_rum_distance():
    alts = tuple("ABCD")
    mixture = [(("A", "B", "C", "D"), 0.4), (("C", "B", "D", "A"), 0.6)]
    result = rum_distance(_from_ranking_mixture(alts, mixture), alts)
    assert result.success
    assert result.mean_l1 < 1e-10


def test_regularity_violation_is_outside_rum_polytope():
    alts = tuple("ABC")
    # Start with every menu. The pair AB gives A=.2, while adding C raises A to .8,
    # which no menu-independent RUM can reproduce exactly.
    d = {
        ("A", "B"): {"A": 0.2, "B": 0.8},
        ("A", "C"): {"A": 0.5, "C": 0.5},
        ("B", "C"): {"B": 0.5, "C": 0.5},
        ("A", "B", "C"): {"A": 0.8, "B": 0.1, "C": 0.1},
    }
    result = rum_distance(d, alts)
    assert result.success
    assert result.mean_l1 > 0.05
