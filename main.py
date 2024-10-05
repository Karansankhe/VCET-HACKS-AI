import streamlit as st
from bs4 import BeautifulSoup
import requests
import re
from textblob import TextBlob
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer

# Function to search for stock news URLs
def search_for_stock_news_urls(ticker):
    search_url = f"https://www.google.com/search?q=yahoo+finance+{ticker}&tbm=nws"
    r = requests.get(search_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    atags = soup.find_all('a')
    hrefs = [link['href'] for link in atags]
    return hrefs

# Function to strip unwanted URLs
def strip_unwanted_urls(urls, exclude_list):
    val = []
    for url in urls:
        if 'https://' in url and not any(exclude_word in url for exclude_word in exclude_list):
            res = re.findall(r'(https?://\S+)', url)[0].split('&')[0]
            val.append(res)
    return list(set(val))

# Function to scrape and process articles
def scrape_and_process(urls):
    articles = []
    for url in urls:
        no = "Thank you for your patience. Our engineers are working quickly to resolve the issue."
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        paragraphs = soup.find_all('p')
        text = [paragraph.text for paragraph in paragraphs]
        words = ' '.join(text).split(' ')[:350]
        article = ' '.join(words)
        if article != no:
            articles.append(article)
    return articles

# Function to generate summary using Sumy
def generate_summary(article):
    parser = PlaintextParser.from_string(article, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, 1)  # Summarizing to 1 sentence
    return ' '.join(str(sentence) for sentence in summary)

# Function to analyze sentiment using TextBlob
def analyze_sentiment(text):
    blob = TextBlob(text)
    sentiment_score = {
        "label": "POSITIVE" if blob.sentiment.polarity > 0 else "NEGATIVE",
        "score": blob.sentiment.polarity
    }
    return [sentiment_score]

# Function to create output array for displaying results
def create_output_array(summaries, scores, urls, monitored_tickers):
    output = []
    for ticker in monitored_tickers:
        for counter in range(len(summaries)):
            output_this = [
                ticker,
                summaries[counter],
                scores[counter]['label'],
                scores[counter]['score'],
                urls[counter]
            ]
            output.append(output_this)
    return output

# Main function for Streamlit application
def main():
    st.title("Stock News Summary and Sentiment Analysis")
    
    ticker = st.text_input("Enter Stock Ticker:")
    
    if st.button("Get News"):
        if ticker:
            exclude_list = ['maps', 'policies', 'preferences', 'accounts', 'support']
            cleaned_urls = strip_unwanted_urls(search_for_stock_news_urls(ticker), exclude_list)
            articles = scrape_and_process(cleaned_urls)

            summaries = []
            sentiment_scores = []
            monitored_tickers = [ticker]
            
            for article in articles:
                summary = generate_summary(article)
                sentiment_score = analyze_sentiment(summary)
                summaries.append(summary)
                sentiment_scores.append(sentiment_score[0])  # Get the first sentiment score

            final_output = create_output_array(summaries, sentiment_scores, cleaned_urls, monitored_tickers)

            for i in range(len(final_output)):
                st.write(f"**Ticker:** {final_output[i][0]}")
                st.write(f"**Summary:** {final_output[i][1]}")
                st.write(f"**Sentiment:** {final_output[i][2]} ({final_output[i][3]})")
                st.write(f"[Read More]({final_output[i][4]})")
                st.write("---")  # Divider

        else:
            st.warning("Please enter a valid stock ticker.")

if __name__ == '__main__':
    main()
