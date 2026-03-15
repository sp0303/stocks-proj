from fundamental_service import get_fundamentals
from technical_service import get_technical
import json

def test_normalization():
    symbols = ["RELIANCE", "RELIANCE.NS", "^NSEI"]
    
    for s in symbols:
        print(f"\n--- Testing Symbol: {s} ---")
        
        print("Fetching Fundamentals...")
        funda = get_fundamentals(s)
        print(f"PE: {funda.get('pe')}, Score: {funda.get('score')}")
        
        print("Fetching Technicals...")
        tech = get_technical(s)
        print(f"Price: {tech.get('price')}, Action: {tech.get('action')}")
        
        if funda.get('score') == 0 and s != "^NSEI":
            print(f"❌ Fundamentals failed for {s}")
        elif tech.get('price') is None:
            print(f"❌ Technicals failed for {s}")
        else:
            print(f"✅ Success for {s}")

if __name__ == "__main__":
    test_normalization()
