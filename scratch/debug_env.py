import os
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("GATEKEEPER_API_KEY")
print(f"DEBUG: KEY='{key}'")
print(f"DEBUG: LENGTH={len(key) if key else 0}")
