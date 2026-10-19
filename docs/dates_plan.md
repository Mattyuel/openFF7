# Dates with the girls: plan

Status: Tifa and Aerith built (untested in-game): `patches/660_dates.py`. Third place: the Junon cannon (junone7 -> blackbgg, standing, where Tifa and Scarlet slap; user, replacing the Nibelheim water tower). Conversations are the same in every place (user). The design decisions are the user's. The game facts
come from reading the field scripts and the exe offline; none of it has been tested in-game.

## What the user asked for

- Dates with the 20 Honey Bee girls in their **own models** (the ones they use in the
  world), in the **Gold Saucer gondola** and the **space capsule**. The FMV plays behind
  them, as in the original game.
- A chance to get to know each girl more deeply. The dates ramp up in intimacy but are
  less suggestive than the Honey Bee scenes.
- **Questions** during the conversation. Right answers raise affection.
- **Ending choice:** at maxed affection, with every answer in *that* date right, the
  conversation leads to a choice: "Give into your desires." / "Leave it be."
  "Give into your desires" plays an explicit **part 2 right there** (gondola / capsule),
  which needs undressed versions of the girls' own models.
- **How to start one:** ask from the girl's talk menu in the world, hired or not.

User decisions (asked 2026-10-13):

| Question | Answer |
|---|---|
| How many dates | **Tiers like the Honey Bee**: the date you get depends on affection (0-9, 10-19, 20) |
| Affection | **Shared** with the Honey Bee meter (`_config.HB_AFFECTION`, 0-20; gifts, visits, dates all raise it) |
| Part 2 place | **Right there**, in the gondola / capsule |
| Modelling | **A few girls first** (Tifa, Aerith, Elena, Scarlet), then the rest in batches |
| Cost | **Free** |
| Location | **Chosen each time** ("Where to?" Gondola / Space capsule), whatever the tier |
| Background | **Still views, no FMV**: the gondola field's own Gold Saucer night view; the pod's space view |

## Game facts (verified by reading scripts and the exe)

- **Gondola date field = `bwhlin`** (id 489). `blackbg4` is a debug room, not the date.
  - Route: ghotin_2 sets progress 592, then gldgate, then bigwheel (staff), then bwhlin.
  - Normal ride: gold2 + gold3 (`bwhlin.txt:52,72`), gold4, then MAPJUMP `bwhlin2` (gold5 + gold6).
  - Date ride: `bwhlin.txt:621-631` plays PMVIE 0x30 (gold7), the dialogue on the static gondola
    interior, then PMVIE 0x31 (gold7_2).
  - The partner is chosen by IFPRTYQ on the party, not by the movie id.
  - Field stats: 9 models, 67 texts, music MUSIC 00/01/02 by partner.
- **Characters over the FMV:** movies with a `.cam` file in `data/cd/moviecam.lgp`
  drive the field camera while they play, so field models are drawn over the movie.
  - Cam files exist for gold1-gold7_2 and the rocket movies.
  - The script places models (XYZI), then `PMVIE n`, then REQs helper scripts, then `MOVIE`.
    MOVIE blocks only the calling script.
  - Helpers poll the frame with `MVIEF 06 xx` and act at frame numbers: text windows, moves, anims.
  - The camera framing is fixed by the .cam data, so models must sit where the originals sit.
  - The movie camera only exists while MOVIE runs; before and after, the static interior is shown.
- **Space capsule = `rcktin7`** (Escape Pod). Its interior is a static background with a
  "space" BG layer (BGON/BGOFF); its FMV is played mid-scene (PMVIE 0x2c, then 0x2d out).
  - 9 models, 213 texts (shared rocket bank): use a copy.
  - The rocket movies look like disc-2 movie-list entries. openFF7 plays as disc 1, so the
    pod's FMV may not be playable. The static space layer still works. **To check.**
- **Movie name table:** ff7_en.exe VA 0x7BAE80, 105 dword pointers (PMVIE n -> name; disc 1).
  Opcodes: BGMOVIE 0x27, PMVIE 0xF8, MOVIE 0xF9, MVIEF 0xFA, MVCAM 0xFB.
- **New fields:** `ctx.new_field` needs a maplist name with no file. 16 are free besides the
  wmN / dummy / Honey Bee names:
  qe, blackbga, blackbgf, blackbgg, whitebg1 (used: 670's movie set), whitebg2, blin69_2, trap, junmon, subin_4,
  pass, hyou14, xmvtes, fallp, m_endo, fship_26 (the beach date, 660). None left.
- **Limits:** 16 models and ~255 texts per field. So one field can't hold all 20 girls
  (plus their undressed copies), and dates are spread over several copies.
- **Girls' models:**
  - 19 different skeletons (Rhonda and Celeste share DQAE), all with the standard bone names
    (hip, chest, head, l_/r_ collar, uparm, foarm, hand, hip, femur, tibia, foot).
  - Tifa and Aerith add hair bones; Scarlet adds foot sub-bones.
  - So `ff7.fieldanim` pose builders (as for the Honey Bee dancer and Cloud) work for all of them.
  - All are adult women.

## Design (proposed; to confirm)

### Starting a date
- Every girl's world talk gets **"Ask her on a date."**, before and after hiring, with or without the
  Honey Bee job. It's free.
- Then "Where to?": **Gondola** / **Space capsule**. Fade, MAPJUMP into that location's field
  copy for her group.
- Afterwards, fade back to her spot (her field, beside her).

### Tiers (by her affection when you ask), in either location

| Affection | Date |
|---|---|
| 0-9 | First date |
| 10-19 | Second date |
| 20 | Third date (repeatable; the ending choice) |

- One conversation per girl per tier, used in both places. The opening line and a
  remark or two follow the location (the view of the Saucer / of the planet).

### Backgrounds (user: still views, no FMV)
- **Gondola:** bwhlin's still background is the Gold Saucer at night (no cabin drawn). Cloud
  and the girl sit in front of it on the field's walkmesh.
  - **To check:** how the pair looks against the view with no cabin. If it reads oddly, a
    cabin frame could be drawn as extra background tiles.
- **Space capsule:** rcktin7's pod interior with its space layer on (BGON), and the planet
  in view. No movie, so no disc-1/disc-2 movie question and no camera-fixed framing.

### Conversation and questions
- Each date has about 6-10 lines and **2-3 questions** about her: her past, her tastes, things she
  said in earlier dates and in her Honey Bee lines.
- Answering works like the hiring questions (ASK, 3 answers, one right). Each right answer gives
  +1 affection (capped at 20). A wrong answer gets a reaction line and no gain.
- **Third date at 20:** a temp flag records any wrong answer *in this date*. With none, her last
  lines lead into the ASK "Give into your desires." / "Leave it be."
  - Leave it be: a tender ending line.
  - Give in: part 2.
  - With a wrong answer, the date ends normally (no choice shown).

### Part 2 (explicit, "right there")
- An undressed copy of the girl's own model (`ModelLoader.with_hrc`, new .rsd/.p as for the
  bare-legged Cloud: clothing colours to her skin colour, shape fixes where needed) and the
  bare Cloud.
- Poses built per skeleton with `ff7.fieldanim` (seated / astride, 0.5 s loops as in the
  Honey Bee positions), in the gondola seat / pod.
- Then a fade, a closing line, and back to her spot.
- **Order:** Tifa, Aerith, Elena, Scarlet first; then batches of 4.

### Fields (8 of the 16 free names)
- Girls in 4 groups of 5. Per location, one field copy per group (gondola: bwhlin; capsule: rcktin7).
- Each copy holds:
  - Cloud + bare Cloud + 5 girls + 5 undressed girls = 12 models.
  - 5 girls x 3 tiers x ~10 texts = ~150 texts.
- The undressed copies are added only as their part 2 gets built.

## Milestones

1. **Framework + Tifa:**
   - Date option + "Where to?" on her talk; tier routing.
   - Both field copies (gondola view, pod with the space layer) with her and Cloud placed and seated
     (seated pose builder for her skeleton).
   - Her three dates with questions, affection and the ending choice (no part 2 yet).
   - Return to her spot.
   - Test in-game: how the two views look, positions, text.
2. (merged into 1)
3. **All 20 girls' dates** (writing 60 dates), seated poses for all 19 skeletons.
4. **Part 2 for Tifa, Aerith, Elena, Scarlet** (undressed models + poses).
5. **Part 2 for the other 16 girls** in batches of 4.

## Open questions for the user

- None for now. Answered 2026-10-13: free; location chosen each time; still views instead of FMV.
