"""(user) Hand-edited char.lgp files: every file in patches/char_overrides/ (e.g. a .p part edited in a
model tool) is written into char.lgp last, over whatever the patches built under that name. Only put the
files you changed there, named as in char.lgp (lower case, e.g. zcmp.p); a name the build doesn't know is
added as a new file."""
import os

DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "char_overrides")


def apply(ctx):
    names = sorted(n for n in os.listdir(DIR) if not n.startswith(".") and n.lower() != "readme.md")
    for n in names:
        assert n == n.lower(), ("char.lgp names are lower case", n)
        with open(os.path.join(DIR, n), "rb") as fh:
            ctx.char_file(n, fh.read())
    if names:
        print("  990: %d hand-edited char.lgp file(s): %s" % (len(names), ", ".join(names)))
