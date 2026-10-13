# Animation catalogue

Field animations we use or have looked at, by model, with what they look like
(meanings mostly from the user, who checked them in game or a viewer). Keep this
up to date when an animation is added, renamed or found to look different.

**How names work.** A field model loader lists animations as `NAME.ext`
(e.g. `DXJC.tor`); the game loads `name.a` from `data/field/char.lgp`, so
the extension is only the original animator's tag. Use the spelling some field
already uses (search the model loaders), or any tag for our own files.
An animation only works on the skeleton it was made for (same bones).
Add animations to a model with `ModelLoader.with_anims(entry, [names])`; play one
with `DFANM` (0xA2: becomes her default animation, which loops while she is idle; 620's
`_loop` also plays it once with ANIME1 so the loop starts at once), `ANIM!1` (0xAF, plays and holds the last frame), `ANIME1` (0xA3, plays once
and returns to the idle) or `CANM!1` (0xB1, a frame range); 620's `_anim` /
`_canm` helpers.

**Limits seen so far** (no hard cap found; each animation costs memory and load
time on entering a field): the original game's maximum is 47 on one model
(junbin5) and 173 in one field (jundoc1a). Ours, played in game without trouble:
55 on Cloud in onna_6, 308 in the lounges (onna_52 / onna_1: 10 extra girls
carrying all 24 dancer animations; trim them if a field ever needs headroom).

## Honey Bee dancer (BADD.HRC, 21 bones)

Bones: 0 hip, 1 chest, 2 head, 3 l_chest, 4 l_collar, 5 l_uparm, 6 l_foarm,
7 l_hand, 8 r_chest, 9 r_collar, 10 r_uparm, 11 r_foarm, 12 r_hand, 13 l_hip,
14 l_femur, 15 l_tibia, 16 l_foot, 17 r_hip, 18 r_femur, 19 r_tibia, 20 r_foot
(hip, l_hip and r_hip hang off the root).

| Anim | Looks like | Used as (620) |
|---|---|---|
| BAJB | stand (idle) | loader slot 0 |
| BCCC | walk | slot 1 |
| BCCD | run | slot 2 |
| AVJE | shocked | beat `shocked` |
| BYAD | point / poke | beat `point`; lounge standing idle |
| DXHE | sitting | lounge sitter; scene `sit1`, the bed-edge sitter (`("bed", "sit")`) |
| DXIB | sitting (another) | lounge sitter; scene `sit2` |
| DXIC | sitting (another) | lounge sitter; scene `sit3` |
| DXIF | check both sides | beat `checksides`; lounge standing idle |
| DXJA, DXJB | dances | (unused) |
| BAJF | squat and twirl hips | beat `twirl`; lounge standing idle |
| BBAA | bend down, poke with the stinger | beat `stinger`; lounge standing idle |
| BAJD | spin, then shake behind | beat `spinshake`; lounge standing idle |
| BAJC | walk (another) | (unused) |
| DXJC | sexy dance | beat `sexy`; lounge standing idle |
| DXJD | present something with an arm | beat `present`; lounge standing idle |
| DZBA | lying on her back (1-frame pose) | lounge lying girl |
| DIEF | bow | beat `bow`; lounge standing idle |
| DXIE | (another shake, like BAJE) | (unused) |
| BAJE | shake behind | beat `shimmy`; lounge standing idle |
| AAGA | silly run | (unused) |
| DXHF | strut | (not added) |
| DXIA | silly run | (not added) |
| DXID | stand (another) | (not added) |

### Our own poses (built at build time, written to char.lgp)

Made in 620 from her standing pose BAJB with `ff7.fieldanim` (forward
kinematics on BADD.HRC; rotation order Y X Z, each bone runs along its own
-z; the root height is stored negated, floor at 0, y down). One frame each.

| Anim | File | Pose | Built by |
|---|---|---|---|
| DZBT | dzbt.a | on her back facing up, thighs raised 45 and spread 45, knees bent (~101) so the feet are planted flat, arms along her sides; hips where DZBA has them. Moves (60 frames, ~2 s, eased): the knees fall open 8 degrees and close (each leg turns about its hip-ankle line: the feet don't move) | `_on_back` (`LEG_RAISE`, `LEG_SPREAD`, `POSE_ROCK`) |
| DZBF | dzbf.a | on all fours: facing down, hips / knees / shoulders at 90, knees and wrists on the floor, feet flat, head lifted 30. Moves (60 frames, eased): rocks back 8 degrees on the knees and forward again; knees, shins and hands stay planted (the arms re-bend each frame, Newton solve on the skeleton) | `_fours` (`FOURS_HEAD_LIFT`, `POSE_ROCK`) |
| DZBR | dzbr.a | kneeling astride, rocking (60 frames, ~2 s): hips flexed 70 and spread 30, knees 160 so the shins lie flat (feet flat behind), torso 25 forward, arms 25 forward; the knees open 8 towards straight and back, eased, with the shins planted (the hips rise ~0.6 and settle). Used in the bed layout `ride` (Cloud on his back under her) and the beat `ride` (plays it 3 times) | `_ride` (`RIDE_*`) |

History: DZBT was first DZBA rolled 60 degrees about her length (the hip
bone's z angle + 60), replaced by the knees-up pose.

## Cloud (AAAA.HRC)

### In the "&" room's own loader (onna_52)

All 25 (index: name): 0 ACFE, 1 AAFF, 2 AAGA, 3 AQAA, 4 EACF, 5 DMBC, 6 EADA,
7 EADB, 8 AJEC, 9 AVJE, 10 AQBF, 11 BTCE, 12 CDAA, 13 CPHF, 14 CDAC, 15 AQAB,
16 BICA, 17 BICB, 18 BICC, 19 EADC, 20 EADD, 21 EADE, 22 CZHE, 23 EADF, 24 APJF.
The ones the scenes use:

| Index | Anim | Looks like | Used as |
|---|---|---|---|
| 0 | ACFE | stand | `stand` |
| 3 | AQAA | kneel / sit down on the bed: frames 0-1D sit, 1D-2C stand up | `sit`, `stand` |
| 9 | AVJE | shocked | `shocked` |
| 15 | AQAB | hands on hips | `hips` |
| 16 | BICA | falls down (avoid: overused) | `fallstay` |
| 20 | EADD | lying | (the room's own dream) |

### Added for the scenes (`CLOUD_EXTRA`, user-chosen)

| Beat | Anim | Looks like |
|---|---|---|
| shrug | AQCB.chi | shrug |
| take | FYGC.chi | take something |
| nudge | FYFC.chi | nudge |
| nod | AJDC.aki | nod |
| shakehead | BUAA.chi | shake head |
| laugh | BTCD.aki | laugh |
| impatient | BDCC.aki | impatient |
| lookaround | AUEE.yos | look around |
| lookup | AQFA.yos | look up |
| turnaway | CAFB.aki | turn away |
| formal | EGGD.yos | stand formally |
| coy | EGIC.yos | coy |
| point | ALGB.yos | point |
| cleanpants | CCJF.tor | brush off trousers |
| stretch | HOCF.tak | stretch |
| warmup | FJCB.yos | warm up |
| leanin | CDDE.tor | lean in |
| cheer | FDIF.hei | cheer |
| drink | FJCE.aki | drink |

Avoid EACF (arms up): overused.

### Bed poses (`CLOUD_BED`, added only where a room's scenes use them)

| Beat | Anim | Looks like | Facing (620) |
|---|---|---|---|
| grea | GREA.hei | lying on his back, looking right | `CLOUD_BACK_DIR` (0xC0) |
| greb | GREB.hei | lying on his back, moving a little | back |
| grec | GREC.hei | lying, then sits up | back |
| ftib | FTIB.chi | lying on his back (made for the Shinra soldier skeleton BWAB, same bone count) | back |
| enje | ENJE.yos | starts laid down, slowly sits up | back |
| avdd | AVDD.yos | lying on his belly (on top of her) | `CLOUD_BED_DIR` (0x40) |
| avea | AVEA.yos | on his belly, looks to the side | belly |
| enjf | ENJF.yos | sitting, stretching his legs | as he is |
| eiab | EIAB.chi | sitting comfortably | as he is |
| hbgb | HBGB.tak | knelt, thrusting motion (like CPR) | as he is |
| hbgc | HBGC.tak | knelt, looks to the side | as he is |
| hbfe | HBFE.tak | knelt, rubbing his face | as he is |

Fields that use them in the original game (for the exact spelling): GREA/GREB/GREC
gninn, AVDD/AVEA rckt32, ENJE/ENJF sinin2_1, HBGB/HBGC/HBFE rcktin6, EIAB nivgate2,
FTIB coloin2.
