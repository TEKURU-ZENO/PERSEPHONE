"""
PERSEPHONE Central Model Parameter Loader
Loads mechanistic and biophysical parameters from research/model_params.json.
Guarantees single source of truth across Python computation and frontends.
"""
import os
import json
from functools import lru_cache

def _find_repo_root():
    curr = os.path.abspath(os.path.dirname(__file__))
    while curr:
        if os.path.exists(os.path.join(curr, 'research', 'model_params.json')):
            return curr
        parent = os.path.dirname(curr)
        if parent == curr:
            break
        curr = parent
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))

REPO_ROOT = _find_repo_root()
PARAMS_JSON_PATH = os.path.join(REPO_ROOT, "research", "model_params.json")

@lru_cache(maxsize=1)
def load_model_params():
    """
    Loads full parameter registry dictionary from research/model_params.json.
    """
    if os.path.exists(PARAMS_JSON_PATH):
        with open(PARAMS_JSON_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    # Built-in fallback if file is moved
    return {
        "alpha1": {"value": 0.08},
        "alpha2": {"value": 0.045},
        "K": {"value": 200.0},
        "ES": {"value": 0.16},
        "ER": {"value": 0.015},
        "ke": {"value": 0.15},
        "beta": {"value": 0.25},
        "gamma": {"value": 0.10},
        "aSR": {"value": 1.0},
        "aRS": {"value": 1.0}
    }

def get_default_model_params():
    """
    Returns flat key-value dictionary of numerical parameter defaults.
    """
    raw = load_model_params()
    return {k: float(v["value"]) for k, v in raw.items()}
