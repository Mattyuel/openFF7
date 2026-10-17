# python copy_model.py OLD.lgp NEW.lgp OUT.lgp ZTFA ZNEL [more anim ids...]
import sys, re
sys.path.insert(0, "tools")
from ff7.lgp import LGP

old, new = LGP.read(sys.argv[1]), LGP.read(sys.argv[2])
model, anims = sys.argv[4].lower(), [a.lower() for a in sys.argv[5:]]
find = lambda n: next((k for k in old.names() if k.lower() == n.lower()), None)

files = [f"{model}.hrc"]
hrc = old[find(files[0])].decode("latin1").splitlines()
for line in hrc:                      # "<count> RSD1 RSD2 ..." lines
    parts = line.split()
    if parts and parts[0].isdigit() and len(parts) == int(parts[0]) + 1:
        for rsd in parts[1:]:
            files.append(f"{rsd}.rsd")
            text = old[find(f"{rsd}.rsd")].decode("latin1")
            files += [m.split(".")[0] + ".p" for m in re.findall(r"PLY=(\S+)", text)]
            files += [m.split(".")[0] + ".tex" for m in re.findall(r"TEX\[\d+\]=(\S+)", text)]
files += [f"{a}.a" for a in anims]

for n in dict.fromkeys(files):
    src = find(n)
    if src is None:
        print("missing in old archive:", n); continue
    dst = next((k for k in new.names() if k.lower() == n.lower()), n.lower())
    print(("replace " if dst in new else "add     ") + dst)
    new[dst] = old[src]
new.write(sys.argv[3])