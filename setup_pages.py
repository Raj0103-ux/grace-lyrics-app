import urllib.request
import json

TOKEN = "cfat_9yyIx9TqPirxNwrMl4X7VDpJHTNgEDaU7NrbDnitb0946df3"
ACCOUNT_ID = "cdb6fe7f2b93a9c99d0966ae16f28826"
PROJECT_NAME = "gggm-admin"
DB_ID = "06909295-3d34-4fff-9b9b-4724d373659e"

def setup_pages():
    # 1. Create Pages Project
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects"
    body = {
        "name": PROJECT_NAME,
        "production_branch": "main"
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="POST")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("PROJECT_CREATED")
    except Exception as e:
        print(f"PROJECT_INFO|{e}") # Might already exist
    
    # 2. Bind D1 Database to Pages
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/pages/projects/{PROJECT_NAME}"
    # We need to update the placement or production config
    body = {
        "deployment_configs": {
            "production": {
                "d1_databases": {
                    "DB": { "id": DB_ID }
                }
            },
            "preview": {
                "d1_databases": {
                    "DB": { "id": DB_ID }
                }
            }
        }
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(), method="PATCH")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", "application/json")
    
    try:
        with urllib.request.urlopen(req) as resp:
            print("BINDING_SUCCESS")
    except Exception as e:
        print(f"BINDING_ERROR|{e}")

if __name__ == "__main__":
    setup_pages()
