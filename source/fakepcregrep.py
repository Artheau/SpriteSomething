import os
import regex

REGEX=r"^([-\w]*)([.]|$)([\d]|exe|$)([.]|$)([\d]+|$)([-[:alpha:].]+|$)"

with open(os.path.join("build","SpriteSomething","filename.txt")) as f:
	s = f.read()
y = regex.findall(REGEX, s, regex.MULTILINE)

with open(os.path.join("build","SpriteSomething","filename.txt"),"w+") as f:
	for fname in y:
		fname = "".join(map(str,fname))
		if not fname.strip() == "":
			f.write(fname + "\n")
