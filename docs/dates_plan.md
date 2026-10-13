# Dates with the girls: plan

Status: plan only, nothing built. The design decisions are the user's. The game facts
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
  qe, blackbga, blackbgf, blackbgg, whitebg1, whitebg2, blin69_2, trap, junmon, subin_4,
  pass, hyou14, xmvtes, fallp, m_endo, fship_26.
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
- Every girl's world talk gets **"Ask her on a date."** It is there before and after hiring,
  and doesn't need the Honey Bee job. It fades out and MAPJUMPs into the date field for her tier.
- Afterwards it fades back to her spot (her field, beside her).
- Optional: a Gold Saucer ticket cost, e.g. 300 gil. Say if you want one.

### Tiers (by her affection when you ask)

| Affection | Date | Place | Movie |
|---|---|---|---|
| 0-9 | First date | Gondola, ordinary ride | gold2-gold6 (as the normal ride) |
| 10-19 | Second date | Space capsule (pod interior, space layer; FMV if disc 1 allows) | rocket movie / none |
| 20 | Third date | Gondola, the fireworks date ride | gold7, conversation, gold7_2 |

- The third date can be repeated. Each time it plays again (as the Honey Bee devoted visits do).

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
- **Timing:** text over the movie is frame-timed (non-interactive windows, as the original).
  Questions are asked on the static interior between movies (the original date's dialogue sits
  between gold7 and gold7_2).

### Part 2 (explicit, "right there")
- An undressed copy of the girl's own model (`ModelLoader.with_hrc`, new .rsd/.p as for the
  bare-legged Cloud: clothing colours to her skin colour, shape fixes where needed) and the
  bare Cloud.
- Poses built per skeleton with `ff7.fieldanim` (seated / astride, 0.5 s loops as in the
  Honey Bee positions), placed in the gondola seats.
- It plays over gold7_2 (or the static interior if the camera framing doesn't allow it). Then a
  fade and a closing line, and back to her spot.
- **Order:** Tifa, Aerith, Elena, Scarlet first; then batches of 4.

### Fields (7 of the 16 free names)

| Field copy | Base | Holds |
|---|---|---|
| gondola 1 A / B | bwhlin (+ bwhlin2 movies) | first dates, 10 girls each (Cloud + 10 models) |
| capsule A / B | rcktin7 | second dates, 10 girls each |
| gondola 3 A / B / C | bwhlin | third dates + part 2: ~6 girls each (girl + undressed girl + Cloud + bare Cloud) |

About 10 texts per girl per date, so 60-130 texts per field.

## Milestones

1. **Framework + Tifa:**
   - Date option on her talk; tier routing; a gondola 1 copy with the movies and her seated.
   - Seated pose builder for her skeleton; one first date with questions and affection.
   - Return to her spot.
   - Test in-game: models over the FMV, framing, timing.
2. **Space capsule + third date for Tifa,** the ending choice (no part 2 yet).
3. **All 20 girls' dates** (writing 60 dates), seated poses for all 19 skeletons.
4. **Part 2 for Tifa, Aerith, Elena, Scarlet** (undressed models + poses).
5. **Part 2 for the other 16 girls** in batches of 4.

## Open questions for the user

- Gil cost per date? (default: free)
- Third date location: gondola (fireworks) as proposed, or the capsule?
- If the pod FMV can't play on disc 1: is the static space view behind the pod window enough?
