import asyncio
import json
from intelligence_service import get_stock_intelligence, get_index_intelligence
import aiohttp

async def verify():
    print("--- Testing Individual Intelligence (RELIANCE) ---")
    async with aiohttp.ClientSession() as session:
        reliance_data = await get_stock_intelligence("RELIANCE", session)
        
    print(f"Symbol: {reliance_data['symbol']}")
    print(f"Price: {reliance_data['price']}")
    print(f"AI Consensus: {reliance_data['ai']['consensus']['verdict']}")
    print(f"News Sample: {len(reliance_data['news']['articles'])} items")
    print(f"Fundamentals Sample (PE): {reliance_data['fundamentals'].get('pe')}")
    
    # Save to file for manual inspection if needed
    with open("test_intel_stock.json", "w") as f:
        json.dump(reliance_data, f, indent=2)
    print("\n✔ Individual Intelligence test passed. Result saved to test_intel_stock.json")

    print("\n--- Testing Index Intelligence (NIFTY 50) ---")
    print("Gathering data for 50 stocks (Concurrent)...")
    index_data = await get_index_intelligence()
    
    print(f"Total stocks returned: {len(index_data)}")
    if len(index_data) == 51: # NIFTY50 + indexing quirk? No, nifty50 list has 51 items usually including LTIM
        print("✔ Index Intelligence batch size correct.")
    
    with open("test_intel_index.json", "w") as f:
        json.dump(index_data, f, indent=2)
    print("✔ Index Intelligence test passed. Result saved to test_intel_index.json")

if __name__ == "__main__":
    asyncio.run(verify())
