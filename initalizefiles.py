import os

import json

folders = os.listdir(".")
# Checks if all folders are existent
if 'logs' not in folders:
    os.makedirs('logs')
    print("Ordner Logs wurde erstellt")
if 'data' not in folders:
    os.makedirs('data')
    print("Ordner Data wurde erstellt")
if 'roles' not in os.listdir('data'):
    os.makedirs('data/roles')
    print("Roles wurde in data erstellt")

# Check for needed files
with open("data/output.png", "w+"):
    pass
with open("data/blacklist.json", "w+") as f:
    json.dump({"0": []}, f, indent=4)
with open("data/reactionchannels.json", "w+") as f:
    json.dump(dict(), f, indent=4)
with open("data/roles/mainrole.json", "w+") as f:
    json.dump(dict(), f, indent=4)
with open("data/roles/spacer.json", "w+") as f:
    json.dump(dict(), f, indent=4)
