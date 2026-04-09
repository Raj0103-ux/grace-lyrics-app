import urllib.request
import json

TOKEN = "cfat_9yyIx9TqPirxNwrMl4X7VDpJHTNgEDaU7NrbDnitb0946df3"
ACCOUNT_ID = "cdb6fe7f2b93a9c99d0966ae16f28826"

def get_subdomain():
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/subdomain"
    req = urllib.request.Request(url, method="GET")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode())
            if res.get("success"):
                print(f"SUBDOMAIN|{res['result'].get('subdomain', 'NOT_SET')}")
            else:
                print(f"FAILED|{res.get('errors')}")
    except Exception as e:
        print(f"ERROR|{e}")

if __name__ == "__main__":
    get_subdomain()
