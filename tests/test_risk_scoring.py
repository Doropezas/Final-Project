# tests/test_risk_scoring.py
import pytest
from src.data_processing.risk_scoring import calculate_risk_score

def test_risk_score_calculation():
    test_data = {"gdp_growth": 3.5, "inflation": 8.2}
    score = calculate_risk_score(test_data)
    assert 0 <= score <= 100