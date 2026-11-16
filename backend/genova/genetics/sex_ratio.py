"""Biological sex at birth: population statistic only. Family birth-order patterns are NOT used."""
from fractions import Fraction

from .core import make_result, outcome

MALE_PER_100_FEMALE = 105  # natural sex ratio at birth, Our World in Data / UN WPP


def sex_ratio_analysis() -> dict:
    total = MALE_PER_100_FEMALE + 100
    outcomes = [outcome("male", Fraction(MALE_PER_100_FEMALE, total)), outcome("female", Fraction(100, total))]
    return make_result(
        "sex_ratio", "population_statistic", "sex_ratio_at_birth", {}, outcomes,
        ["natural_sex_ratio"], ["sex_ratio_population", "family_pattern_not_predictive"],
        ["owid-sex-ratio", "medlineplus-chromosomes"],
        {"mechanism": "sperm_x_or_y"})
