import os
import sys
import glob
import re


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split(r'(\d+)', text) ]

#files = os.listdir(".")
#for file in files:
#    print(file)

#files = glob.glob("./Section*/*.py")
#files = sorted(glob.glob("./Section*/*.py"), key=natural_keys)
files = sorted(glob.glob("./Section*/*.py"))
#files = glob.glob("./Section*/**/*.py", recursive = True)
for file in files:
    print(file)
sys.exit()

input(">")

f = open("s02_urwid.py",mode="r")

lines = f.readlines()

script = ""
for line in lines:
   print(line.rstrip())
   script += line

input(">")
print(script)
exec(script)
input(">")

