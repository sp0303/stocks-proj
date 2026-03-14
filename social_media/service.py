import http.server
import socketserver
import json
import asyncio
import urllib.parse
from scraper import run_scrape
import os

from dotenv import load_dotenv
import os

load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))
PORT = int(os.getenv("SOCIAL_SERVICE_PORT", 8001))
DATA_DIR = os.path.expanduser("~/.social_sentiment_data")
SCREENSHOT_DIR = os.path.join(DATA_DIR, "screenshots")
RESULTS_DIR = os.path.join(DATA_DIR, "results")

# Ensure directories exist
for d in [SCREENSHOT_DIR, RESULTS_DIR]:
    if not os.path.exists(d):
        os.makedirs(d)

def save_result(symbol, data):
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)
    path = os.path.join(RESULTS_DIR, f"{symbol}.json")
    with open(path, "w") as f:
        json.dump(data, f, indent=4)

class ThreadingHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

class SocialHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urllib.parse.urlparse(self.path)
        
        # Route: Serve screenshots
        if parsed_path.path.startswith("/screenshots/"):
            filename = os.path.basename(parsed_path.path)
            filepath = os.path.join(SCREENSHOT_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-type", "image/png")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Route: Serve symbol JSON results
        if parsed_path.path.startswith("/results/"):
            filename = os.path.basename(parsed_path.path)
            filepath = os.path.join(RESULTS_DIR, filename)
            if os.path.exists(filepath):
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                with open(filepath, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(404)
                self.end_headers()
            return

        # Route: Analyze sentiment
        if parsed_path.path == "/analyze":
            query = urllib.parse.parse_qs(parsed_path.query)
            symbol = query.get("symbol", [None])[0]
            
            if not symbol:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Missing symbol parameter")
                return

            try:
                # Run the async scraper
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(run_scrape(symbol))
                loop.close()
                
                # Save to individual symbol.json
                if result and "error" not in result:
                    save_result(symbol, result)
                
                response_data = json.dumps(result).encode()
                
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", len(response_data))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(response_data)
            except Exception as e:
                error_data = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header("Content-type", "application/json")
                self.send_header("Content-Length", len(error_data))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(error_data)
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
        
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with ThreadingHTTPServer(("", PORT), SocialHandler) as httpd:
        print(f"Social Sentiment Service running on port {PORT}")
        httpd.serve_forever()
