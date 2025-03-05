import pytest
import pandas as pd
from data_processing.risk_assessment import calculate_risk_scores

@pytest.fixture
def sample_data():
    return pd.DataFrame({
        'GDP_growth': [4.5, -2.3],
        'Inflation': [8.1, 3.4],
        'Debt_to_GDP': [65, 120],
        'Current_account': [-3.2, 1.5],
        'Political_stability': [60, 30]
    })

def test_risk_score_range(sample_data):
    scores = calculate_risk_scores(sample_data)
    assert all(scores['risk_score'].between(0, 100))