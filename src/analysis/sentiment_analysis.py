from vaderSentiment import SentimentIntensityAnalyzer
from transformers import pipeline

class SentimentAnalyzer:
    def __init__(self):
        self.vader = SentimentIntensityAnalyzer()
        self.hf_pipeline = pipeline("sentiment-analysis", model="finiteautomata/bertweet-base-sentiment-analysis")

    def analyze(self, text: str, method="vader"):
        if method == "vader":
            return self.vader.polarity_scores(text)
        else:
            return self.hf_pipeline(text)