# The Director's parody films: record for integration

(user: "keep a record of what we've done so we can integrate all of this later")

This is what exists today, how it hangs together, and what joining it to the gym plan
(`docs/gym_plan.md` sections 4.1 / 4.2) will touch. Every film is built and passes the offline
checks: placements on offline renders, poses measured, meter spots projected. **None of it has
been confirmed in-game yet.**

## 1. What the player sees

The Director (670's cameraman, in the Sector 7 station `mds7st3`) has a film menu. Every film is
offered from the start.

| # | Menu entry | Patch / data | Set (field) | Cast | Shape |
|---|---|---|---|---|---|
| 0 | The Basics (start here). | `688_tutorial` / `_tutorial` | `blackbg9` = copy of the inn `mds7_w3` (670's movie room) | Cloud, Tifa | the Director's tutorial: head, all fours (+ the taste, the 'there' joke), 69; hold demo; 10 s finisher |
| 1 | Sector 7 Workout. | `683_workout` / `_workout` | `blackbg3` = copy of the gym `mkt_mens` | Cloud, Tifa | squats, clothed part A then bare part B; holds on her cue |
| 2 | Going up. | `684_going_up` / `_going_up` | `blackbg4` = copy of the glass elevator `eleout` | Cloud, Tifa, Elena | Elena behind / Tifa's head, "Switch!" calls, Tifa's tap-out hold; the car moves at the end |
| 3 | Tickets, please! | `685_tickets` / `_tickets` | `blackbg6` = copy of the train `tin_2` | Cloud, Tifa, Jessie | Tifa on all fours over Jessie; Jessie's tap-out hold |
| 4 | Hostile Takeover. | `686_hostile` / `_hostile` | `blackbg5` (front, `blin66_6`) + `blackbg8` (overhead, `blin66_5`), alternating | Cloud, Scarlet, Elena | boardroom table; two camera angles, state carried across by bank 2 142-156 |
| 5 | Besties. | `687_besties` / `_besties` | `blackbgh` = copy of Gast's house `snmayor` | Cloud, Tifa, Aerith | the Director's soap-opera script; 5 segments with offers / gags between; scored climax |

The older movie shoots (670 solo co-stars, 672 special, 673 Blast-off, 674 stage show, 678/679 group
sets, 682 school dance) are still reached from the same Director through the co-star flow. They use
670's press-rate meter, not the prompt game below.

## 2. The shared prompt game (683-688)

Every film runs the same loop, copied into each patch rather than shared. 684's code is the template;
685 and 686 are copies of it.

- **A rep** = one prompt: `[SWITCH]` (Square) / `[CANCEL]` / `[OK]` at random, in window 1. The
  rep lasts `PERIODS[TIER]` frames, which is 3 strokes of the 20 / 15 / 11 / 8-frame speeds. The
  right button in time is a hit. Anything else, or nothing, is a miss.
- **Input:** one tiny polling entity per button (`k_sw`, `k_ca`, `k_ok`, plus `k_mn` = [MENU]).
  - An up -> down change sets PR = button number (OK = 3) and a HELD bit while the button is down.
  - One entity can't poll several buttons: the engine runs 8 ops a frame per entity.
- **Tiers:** `HITS_UP` hits in a row = the next speed; a miss drops back to tier 0.
- **Pay:** PAY += tier + 1 per hit (a HOLD hit pays double). The end pays PAY x `PAY_HIT` gil (10-15).
- **Holds:**
  - HOLD prompts: keep the button down to the rep's end.
  - Head holds (684-687): held deep until she taps out. Let go within `LETGO` = bonus; early = miss;
    late = she gets mad (ANGER). At `MAD_LIMIT` she walks out and loses an affection point.
  - After every head hold, Cloud pulls out and wiggles (`_wiggle`).
- **Switch calls** (684-686): `[MENU]` in time when she calls "Switch!" = a bonus. Either way the
  partner P flips (fast fade).
- **Variety:**
  - Chatter every `CHAT_EVERY` reps; a line on every miss.
  - Cloud's pose style flips every `STYLE_EVERY` reps.
  - Tier lines play the first time each tier is reached.
  - The intro gestures come from `_gestures`.
- **Danger meter** (`_danger`):
  - The cursor sits on a bar at the top of the view. A miss pushes it `MISS_OUT` 2 out; a hit pulls
    it `HIT_IN` 1 in.
  - Either red end = the Director's "CUT!": the film ends, paid for what was earned.
  - Finisher after the last rep: mash [OK] to push the cursor into the right red (it slips back every
    `DECAY` 12 frames). Success = fanfare + `FINISH_BONUS` 20 PAY units.
  - The finisher lasts 5 s (150 frames), or 10 s in The Basics.
- **The Director** stands beside the action (`_director`: a spot clear of every actor on screen), still
  in the intro, filming from the scene on. The Basics uses 670's cameraman spots instead.

### Lengths and pay

| Film | Prompts | Gil per tier point |
|---|---|---|
| Basics | 3 x 12 | 10 |
| Workout | 16 + 20 | 10 |
| Going up / Tickets / Hostile | 32 | 15 |
| Besties | 5 x 10 + finale prompts | 12 |

## 3. Shared modules (reuse these)

| Module | Gives |
|---|---|
| `_danger.py` | Meter sprites per set (tag letters in use: A E F H I J U by 670-679; K L M N O P Q by the films), placement for one view or several (`view=`), `start` / `hit` / `miss` / `cut` / `finale` ops |
| `_wiggle.py` | Cloud's pull-out hip wiggle from any head stroke |
| `_director.py` | The Director's model, a clear spot, his entity (still / filming) |
| `_gestures.py` | One-shot intro gestures per actor, seated copies, our own built ones (ZGHR hip rock) |
| `_besties_rig.py` | The pose rig: body / pelvis / waist / neck turns, bone aims, two-bone IK, `fit`, kneel, stand_feet, face / entry points, hair. Used by 687, 686's `under`, `_wiggle`, 688's taste, 685's wander, the hip rock |
| `_tickets_poses.py` | Field <-> model conversions (`_field`, `_inv_off`), joints, entry / mouth points per frame, `still`, `spread`, `wander` |
| `_dance_poses.py` | `_Body` (drop / shift / lean on a skeleton), used for solving Cloud against a partner |

## 4. State each film uses

- **Temp vars:** each film keeps its own block, from (5,100) to about (5,148) and (6,110-135). They only
  matter inside that film's set.
- **Meter:** 683 (5,137-139); 684-686 (5,146-148); 687 (5,141-143); 688 (5,109-111).
- **Saved:** only 686's camera switch, bank 2 142-156 (`RESUME` + its state; METER at 156).
  670 clears RESUME before jumping in.
- **Affection:** a walk-out costs a point (670 `lose_affection`). Tifa, Elena and Scarlet have one;
  Jessie has none.
- **Square:** every film set is skipped by 680's affection list and by the debug menu, because Square
  is a prompt there.
- **Way back:** every film ends with MAPJUMP `mv.WALL` at `ctx.movie_back`, beside the Director in
  `mds7st3`.

## 5. Integration with the gym plan (open decisions)

The plan (`docs/gym_plan.md` 4.1 / 4.2) wants these steps:

- The Director is met at the Honey Bee Inn, then works from the station.
- Shoots are "Tifa + Cloud, paid per shoot" until you buy the production company.
- Videos then sell through the Materia Store.

What that touches here:

- **Gating the menu.** Today every film is available at once. The chain could unlock them one by one:
  - The Basics first;
  - then Workout once the gym is bought;
  - films with Elena / Jessie / Scarlet / Aerith once they're met or hired.
  - Needs a "films unlocked" byte; banks 1-4 have free bytes per `save-usage`.
- **Pay -> profits.**
  - Today each film pays on the spot (GOLDU).
  - After the company purchase, a film could make a video instead: a record of the film, its PAY score
    and whether the finisher landed.
  - The Materia Store deal would then sell those videos over time, using the play clock as Honey Bee
    Collect does.
- **The meter's score** (hits, finisher) is the natural "video quality" the plan asks for.
- **Code sharing.** The prompt loop is copied in 683-688 (and differs slightly in each).
  - Integration is the time to pull it into one module (`_prompt_game`?) with hooks for each film's
    beats, holds and switch calls.
  - Its pieces today are the rep, hit, miss, hold (early / good / late), switch, chat, style and the
    finisher.
- **The cast's affection.** Walk-outs already cost affection. A good film could earn some (not done).
- **The Honey Bee Inn's night shift** (next) is planned to reuse the same prompt polling, `_danger`'s
  meter and the dates' choice logic.

## 6. Status / untested

- Every film is **built and offline-checked only**.
- Things to confirm in-game:
  - the meter is visible in each set (and in both boardroom views);
  - the cursor's steps read clearly;
  - the finisher mash rate is fair (the slip is one step every 12 frames);
  - the camera follows each position in The Basics;
  - the Director never blocks the action;
  - the wiggle's timing;
  - the walk-outs.
- Test list: `TESTING.md` (film entries).
