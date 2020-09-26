import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

with open("./requirements.txt") as req:
    reqs = req.readlines()

for req_n in reqs:
    install(req_n.replace("\n", ""))

