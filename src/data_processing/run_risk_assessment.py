# src/analysis/run_risk_assessment.py
from risk_assessment import RiskAssessor
from pathlib import Path

DATA_PATH = Path(__file__).parent.parent.parent / "data"

def main():
    risk_scores = RiskAssessor().calculate_scores()
    risk_scores.to_parquet(DATA_PATH / "processed/risk_scores.parquet")
    print("Latest Risk Scores:\n", risk_scores.head())

if __name__ == "__main__":
    main()