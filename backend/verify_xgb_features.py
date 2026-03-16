import asyncio
import aiohttp
import json
import sys
import os

# Ensure we can import from the current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from intelligence_service import get_stock_intelligence

async def test_intelligence():
    print("Testing Intelligence Service with XGBoost FEATURES integration...")
    try:
        async with aiohttp.ClientSession() as session:
            # RELIANCE.NS should have an XGBoost model trained
            data = await get_stock_intelligence("RELIANCE", session)
            
            if "error" in data:
                print(f"Error returned: {data['error']}")
                return

            ai = data.get('ai', {})
            xgb = ai.get('xgboost', {})
            
            print("\n--- XGBoost Result ---")
            print(f"Signal: {xgb.get('signal')}")
            print(f"Move: {xgb.get('move')}%")
            
            features = xgb.get('features', {})
            if features:
                print(f"\n✅ SUCCESS: Features found! ({len(features)} indicators)")
                # Print sample
                print("Samples:", {k: v for k, v in list(features.items())[:5]})
            else:
                print("\n❌ FAILED: Features are still empty or missing.")

    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    asyncio.run(test_intelligence())
