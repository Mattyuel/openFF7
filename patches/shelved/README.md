# Shelved patches

Not applied by the build (it only runs `patches/[0-9]*.py`). Move one back up a
directory to re-enable it.

- `500_tame.py` - Tame milestone 1 (materia 38, command 0x1C, kernel2 text,
  orb on the Sector 6 playground, exe changes). Shelved by the user's choice;
  research in docs/research_battle.md, docs/research_menu.md.
- `950_leader_entities.py` - any character can lead in fields (PC entities for
  everyone, party-copy sync, 16-model cap, VISI guards). Shelved: Cloud stays
  leader for now (locked at new game). Known gaps: ladder/jump scripts act on
  Cloud's entity; 7th Heaven door froze Tifa as leader.
