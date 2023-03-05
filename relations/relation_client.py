import requests
import json
import sys
from config_loader import load_config

if __name__ == "__main__":
    infile = sys.stdin
    if len(sys.argv) == 2:
        infile = open(sys.argv[1], encoding="utf-8")
    config = load_config()
    port = config["port"]
    data = json.load(infile)
    infile.close()
    res = requests.post(f"http://localhost:{port}/predict", json=data)
    print(json.dumps(res.json(), indent=4))

