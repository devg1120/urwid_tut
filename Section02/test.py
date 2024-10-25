
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

