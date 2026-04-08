import subprocess
import sys

def get_help():
    try:
        result = subprocess.run(['flet', 'build', 'apk', '--help'], capture_output=True, text=True, check=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error getting help: {e}")

if __name__ == "__main__":
    get_help()
