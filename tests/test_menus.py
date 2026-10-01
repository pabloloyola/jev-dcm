import random

from jev_dcm.menus import all_menus, menu_permutations


def test_five_alternatives_have_26_nontrivial_menus():
    menus = all_menus(tuple("ABCDE"))
    assert len(menus) == 26
    assert ("A", "B") in menus
    assert tuple("ABCDE") in menus


def test_permutations_are_unique_and_canonical_first():
    rng = random.Random(7)
    perms = menu_permutations(tuple("ABCD"), 6, rng)
    assert perms[0] == tuple("ABCD")
    assert len(perms) == 6
    assert len(set(perms)) == 6
