import asyncio
import json
import os
import sys
import requests

import os
from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
SOCIAL_SERVICE_PORT = int(os.getenv("SOCIAL_SERVICE_PORT", 8001))
SOCIAL_SERVICE_URL = f"http://localhost:{SOCIAL_SERVICE_PORT}/analyze"

async def get_social_sentiment(symbol: str):
    """
    Calls the standalone social media service to perform the scraping.
    """
    try:
        # Remove restrictive timeout for slow human-like scraping
        response = requests.get(f"{SOCIAL_SERVICE_URL}?symbol={symbol}", timeout=None)
        if response.status_code == 200:
            data = response.json()
            # Update screenshot path to include the full URL of the social service
            if "screenshot" in data:
                filename = os.path.basename(data["screenshot"])
                data["screenshot"] = f"/social-screenshots/{filename}"
            return data
        else:
            return {"error": f"Social Service returned error {response.status_code}", "details": response.text}
            
    except Exception as e:
        return {"error": f"Failed to connect to Social Service: {str(e)}"}

async def get_social_sentiment_batch(symbols):
    """
    Batch processing for social sentiment.
    """
    results = []
    for s in symbols:
        results.append(await get_social_sentiment(s))
    return results

if __name__ == "__main__":
    # Test run
    if len(sys.argv) > 1:
        print(asyncio.run(get_social_sentiment(sys.argv[1])))
    else:
        print(asyncio.run(get_social_sentiment_batch(["RELIANCE", "TCS"])))