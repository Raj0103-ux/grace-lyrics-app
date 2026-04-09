import urllib.request
import os

TOKEN = "cfat_9yyIx9TqPirxNwrMl4X7VDpJHTNgEDaU7NrbDnitb0946df3"
ACCOUNT_ID = "cdb6fe7f2b93a9c99d0966ae16f28826"
SCRIPT_NAME = "gggm-admin"

def upload_worker():
    url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{SCRIPT_NAME}"
    
    boundary = "---GGGM_BOUNDARY---"
    
    with open("metadata.json", "r") as f:
        metadata = f.read()
    with open("cloudflare_worker.js", "r") as f:
        script = f.read()
    
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="metadata"\r\n'
        f"Content-Type: application/json\r\n\r\n"
        f"{metadata}\r\n"
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="cloudflare_worker.js"; filename="cloudflare_worker.js"\r\n'
        f"Content-Type: application/javascript+module\r\n\r\n"
        f"{script}\r\n"
        f"--{boundary}--\r\n"
    ).encode("utf-8")
    
    req = urllib.request.Request(url, data=body, method="PUT")
    req.add_header("Authorization", f"Bearer {TOKEN}")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    
    try:
        with urllib.request.urlopen(req) as response:
            print("DEPLOY_SUCCESS")
    except Exception as e:
        print(f"ERROR|{e}")

if __name__ == "__main__":
    upload_worker()
