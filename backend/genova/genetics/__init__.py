"""Deterministic genetic calculation engine. Pure functions: no I/O, no AI, no randomness."""
from .core import ENGINE_VERSION, GeneticsInputError
from .mendelian import mendelian_analysis, MODES
from .blood_type import blood_type_analysis
from .carrier_risk import carrier_analysis
from .sex_ratio import sex_ratio_analysis
from .polygenic import height_analysis, pigmentation_analysis

__all__ = [
    "ENGINE_VERSION", "GeneticsInputError", "MODES", "mendelian_analysis", "blood_type_analysis",
    "carrier_analysis", "sex_ratio_analysis", "height_analysis", "pigmentation_analysis",
]
