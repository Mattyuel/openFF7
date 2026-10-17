Hand-edited char.lgp files go here (`990_char_overrides.py` copies each into char.lgp last, over the
built one). Put only the files you changed, named exactly as in char.lgp, lower case (e.g. `zcmb.p`).
Remove a file to go back to the generated one.

Editing the built char.lgp in a model tool:
1. `python3 tools/ff7tool.py build`
2. Copy `build/openFF7/data/field/char.lgp` somewhere (e.g. `my_char.lgp`; the next build overwrites the
   build folder) and edit it in your tool.
3. `python3 tools/ff7tool.py char-overrides my_char.lgp` saves every file you changed here
   (`--dry-run` lists them first).
4. Build again: your edits are in it, and they stay in every later build.

A file here wins over the patches: if a patch later changes that file (e.g. a pose or shape constant), the
change won't show until you delete your copy here.

Cloud's member is part of his pelvis, `zcmb.p` (Cid's: `zcjb.p`), and each girl's nipples are part of
her torso (Tifa: `zxtb.p`), by `985_merge_parts.py`; edit those, not zcmp.p / zj*l.p.
