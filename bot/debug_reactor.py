import json
import os

REACT_FILE = "reactor_data.json"

def load_reacts():
    if not os.path.exists(REACT_FILE):
        return {}
    with open(REACT_FILE, 'r') as f:
        return json.load(f)

data = load_reacts()
print(f"Loaded data: {data}")

keyword = "علیون"
text = "این یک متن تست است علیون سلام"

print(f"Testing match: '{keyword}' in '{text}'")

for k, v in data.items():
    print(f"Checking '{k}' against '{text}'")
    if k.lower() in text.lower():
        print(f"MATCH FOUND! React with {v}")
    else:
        print("No match.")
