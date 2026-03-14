import asyncio
import random
import os
import sys
from playwright.async_api import async_playwright
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import subprocess


if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

analyzer = SentimentIntensityAnalyzer()

SCREENSHOT_DIR = os.path.join(os.path.expanduser("~"), ".social_sentiment_data", "screenshots")


async def human_delay(a=1, b=3):
    await asyncio.sleep(random.uniform(a, b))


async def scroll(page):
    """Human-like scrolling"""
    distance = random.randint(700, 1200)

    for _ in range(random.randint(3, 5)):
        await page.mouse.wheel(0, distance)
        await asyncio.sleep(random.uniform(1, 2))


def is_relevant(text, symbol):
    """Filter irrelevant tweets"""
    text = text.lower()
    symbol = symbol.lower()

    if symbol in text:
        return True

    # stock hashtags
    if f"${symbol}" in text:
        return True

    # finance keywords
    finance_words = [
        "stock",
        "market",
        "buy",
        "sell",
        "earnings",
        "profit",
        "target",
        "bullish",
        "bearish",
        "invest",
    ]

    return any(word in text for word in finance_words)

async def run_scrape(symbol):

    if not os.path.exists(SCREENSHOT_DIR):
        os.makedirs(SCREENSHOT_DIR)

    browser = None
    subprocess.run(
    ["taskkill", "/F", "/IM", "msedge.exe"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
    )

    async with async_playwright() as p:

        try:

            local_app_data = os.environ.get("LOCALAPPDATA")

            user_data_dir = os.path.join(
                local_app_data,
                r"Microsoft\Edge\User Data"
            )

            profile_name = "Default"

            edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
            if not os.path.exists(edge_path):
                edge_path = r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"

            browser = await p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                executable_path=edge_path,
                headless=False,
                args=[
                    f"--profile-directory={profile_name}",
                    "--disable-blink-features=AutomationControlled",
                    "--start-maximized",
                    "--no-sandbox"
                ]
            )

            page = await browser.new_page()

            # SEARCH QUERY
            # This query targets high-signal sentiment while stripping out automated spam
            query = f'(${symbol} OR "{symbol} stock" OR "{symbol} share") (bullish OR bearish OR breakout OR support OR resistance OR target OR rally OR dip OR buy OR sell) -is:retweet lang:en'
            url = f"https://x.com/search?q={query}&src=typed_query&f=live"

            await page.goto(url)

            await asyncio.sleep(5)

            tweets = []
            scores = []

            for _ in range(15):

                tweet_cards = await page.query_selector_all('article[data-testid="tweet"]')

                for card in tweet_cards:

                    text_el = await card.query_selector('[data-testid="tweetText"]')

                    if not text_el:
                        continue

                    text = await text_el.inner_text()

                    if len(text) < 30 or text in tweets:
                        continue

                    if not is_stock_related(text):
                        continue

                    sentiment = analyzer.polarity_scores(text)

                    tweets.append(text)
                    scores.append(sentiment["compound"])

                    if len(tweets) >= 20:
                        break

                if len(tweets) >= 20:
                    break

                await page.mouse.wheel(0, random.randint(800,1200))
                await asyncio.sleep(2)

            tweets = tweets[:20]
            scores = scores[:20]

            avg = sum(scores)/len(scores) if scores else 0

            shot = f"{symbol}_social.png"
            path = os.path.join(SCREENSHOT_DIR, shot)

            await page.screenshot(path=path)

            return {
                "symbol": symbol,
                "tweets_analyzed": len(tweets),
                "average_sentiment": round(avg, 3),
                "tweets": tweets,
                "scores": scores,
                "bullish_count": len([s for s in scores if s > 0.05]),
                "bearish_count": len([s for s in scores if s < -0.05]),
                "neutral_count": len([s for s in scores if -0.05 <= s <= 0.05]),
                "screenshot": f"/screenshots/{shot}"
            }

        except Exception as e:
            return {"error": str(e)}

        finally:
            try:
                if browser:
                    await browser.close()
            except:
                pass
        
def is_stock_related(text):

    text = text.lower()

    finance_keywords = [
        "stock",
        "share",
        "target",
        "buy",
        "sell",
        "breakout",
        "support",
        "resistance",
        "earnings",
        "profit",
        "results",
        "long",
        "short",
        "market",
        "invest",
        "bullish",
        "bearish"
    ]

    if any(word in text for word in finance_keywords):
        return True

    return False