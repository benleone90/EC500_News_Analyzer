from flask import Flask, request
from newsapi import NewsApiClient
import os

application = Flask(__name__)
news_key = os.environ.get("NEWS_KEY")
newsapi = NewsApiClient(api_key=news_key)


@application.route('/news/everything/<text>')
def news(text=None):
    results = newsapi.get_everything(
        q=text, language='en', sort_by='relevancy')
    return results


if __name__ == '__main__':
    application.run(debug=True)
