import os
import regex

REGEX=r"^([-\w]*)([.]|$)([\d]|exe|$)([.]|$)([\d]+|$)([-[:alpha:].]+|$)"

filename_notes = os.path.join("..","build","filename.txt")

with open(filename_notes) as f:
	s = f.read()
	f.close()

print(s)

y = regex.findall(REGEX, s, regex.MULTILINE)

with open(filename_notes,"w+") as f:
	for fname in y:
		fname = "".join(map(str,fname))
		if not fname.strip() == "":
			f.write(fname + "\n")
	f.close()
os.chmod(filename_notes,0o777)
