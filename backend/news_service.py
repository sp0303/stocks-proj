import aiohttp
import asyncio
import feedparser
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

analyzer = SentimentIntensityAnalyzer()

# Google News RSS template
RSS_URL = "https://news.google.com/rss/search?q={query}+stock&hl=en-IN&gl=IN&ceid=IN:en"


async def fetch_news(session, company):

    url = RSS_URL.format(query=company)

    async with session.get(url) as response:

        text = await response.text()

        feed = feedparser.parse(text)

        news_items = []

        for entry in feed.entries[:5]:

            sentiment = analyzer.polarity_scores(entry.title)

            news_items.append({
                "title": entry.title,
                "link": entry.link,
                "score": sentiment["compound"]
            })

        return {
            "company": company,
            "articles": news_items
        }


async def fetch_all_news(companies):

    async with aiohttp.ClientSession() as session:

        tasks = [fetch_news(session, c) for c in companies]

        results = await asyncio.gather(*tasks)

        return results

def calculate_news_score(news):

    total = 0
    count = 0

    for item in news:

        for article in item["articles"]:

            total += article["score"]
            count += 1

    if count == 0:
        return 0

    return total / count