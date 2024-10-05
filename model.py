# model.py
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

def generate_summary(article):
    parser = PlaintextParser.from_string(article, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 1)  # Summarizing to 1 sentence
    return ' '.join(str(sentence) for sentence in summary)

def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = {"label": "POSITIVE" if blob.sentiment.polarity > 0 else "NEGATIVE", "score": blob.sentiment.polarity}
    return [sentiment_score]
