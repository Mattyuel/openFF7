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
56 on Cloud in onna_6, 308 in the lounges (onna_52 / onna_1: 10 extra girls
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
| DZBT | dzbt.a | on her back facing up, thighs raised 45 and spread 45, knees bent (~101) so the feet are planted flat, arms along her sides; hips where DZBA has them. Moves (15 frames = 0.5 s, eased): the knees fall open 8 degrees and close (each leg turns about its hip-ankle line) and her whole body bounces 1.2 up off the mattress and back, her hips thrusting 1.0 more (shoulders and knees ride only the bounce: chest and thighs re-aimed); arms angled 20 out from her sides; head tilted 25 forward (chin to chest), rocking 12 further forward as she comes down and back as she goes up (user) | `_on_back` (`LEG_RAISE`, `LEG_SPREAD`, `POSE_ROCK`) |
| DZBF | dzbf.a | on all fours: facing down, hips / knees / shoulders at 90, knees and wrists on the floor, feet flat, head lifted 30. Moves (15 frames = 0.5 s, eased, starting rocked back): rocks forward 8 degrees on the knees to the rest pose and back again; knees, shins and hands stay planted (the arms re-bend each frame, Newton solve on the skeleton) | `_fours` (`FOURS_HEAD_LIFT`, `POSE_ROCK`) |
| DZBR | dzbr.a | kneeling astride, bouncing (15 frames = 0.5 s; was 60 / ~2 s): hips flexed 70 and spread 30, knees 160 so the shins lie flat (feet flat behind), torso 25 forward, arms 25 forward; the knees open 24 towards straight and back, eased, with the shins planted (the hips rise ~1.8 and settle). Used in the bed layout `ride` (Cloud on his back under her) and the beat `ride` (plays it 3 times) | `_ride` (`RIDE_*`) |
| DZBL | dzbl.a | cowgirl's own DZBR (user): as she comes up the arms rotate 20 down and the head tilts 15 down (chin to chest), back as she comes down. Ontop keeps DZBR | `_ride` (`COWGIRL_*`) |
| DZBK | dzbk.a | kneeling upright on the floor (DZBR's legs without the spread: knees down, shins flat behind), the whole body above the knees tilted 10 forward and rocking 10 further forward and back (15 frames = 0.5 s, eased; the turn is about the knee line, knees asserted on the floor). Her head stays upright throughout (the standing pose's head; user). The head layout (`kneelfloor`): she kneels facing standing Cloud (user) | `_ride` (`KNEEL_*`) |
| DZBH | dzbh.a | head reverse (user): DZBT's pose and motion (bounce, hip thrust, knees opening and closing) with the arms swung 160 out from her sides along the bed (up past her head), the hips held 2.0 up all the time (shoulders on the bed: her body slopes back to them) plus the bounce, and the head hanging straight down every frame (face upright; user). Placed with her neck at the bed's left edge (`HEADREV_GIRL`), so the head hangs off it, Cloud standing (ZCTE) at the edge spot | `_on_back(ctx, HEADREV_*)` |
| DZBG | dzbg.a | standing bent over (user): knees bent 15 (thighs 7.5 forward, shins 7.5 back), torso bent 90 forward at the hips so it lies level, arms straight out past her head, level; ankles where BAJB has them. Rocks (15 frames = 0.5 s, eased) 5 degrees forward about the ankles and back, feet planted. Then (user): head tipped 25 back (chin up) and turned 15 to her right, arms 15 below level; the hands stay where frame 0 puts them while she rocks (two-bone IK, elbows bending out and up). DZBI = 8 frames (twice as fast) with the torso 20 more upright and the arms 30 below level, after Tifa's "Faster!" (`bendf`). The edge layout (`bendfloor`): her feet just left of the bed's left end, facing screen-right, torso and arms out over the bed, Cloud standing (ZCTE) behind her | `_bend` (`EDGE_*`) |

History: DZBT was first DZBA rolled 60 degrees about her length (the hip
bone's z angle + 60), replaced by the knees-up pose.

## Cloud (AAAA.HRC)

The devoted room's part two uses a second Cloud (zcla.hrc, same skeleton: bare
legs, slim knees; 620 `_bare_cloud`) carrying the same animation list, so every
Cloud animation below works on it too.

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
| thrust | ZCTA.tor (ours) | on his belly as AVDD, legs straight back, slow hips (below) | belly |
| pound | ZCTB.tor (ours) | knelt as HBGB, quick deep hip thrust (below) | as he is |
| spread | ZCTC.tor (ours) | sitting as EIAB, legs swung 30 out (below) | as he is |
| buck | ZCTD.tor (ours) | on his back as GREA, quick upward thrusts, head up, arms raised (below) | back |
| stand | ZCTE.tor (ours) | standing, knees bent, leaning forward, thrusting (below) | as he is |
| standl / standlf | ZCTF.tor / ZCTG.tor (ours) | edge: as stand, arms further forward, left leg raised; standlf twice as fast | as he is |

### Our own pose for Cloud (built at build time, written to char.lgp)

| Anim | File | Pose | Built by |
|---|---|---|---|
| ZCTA | zcta.a | AVDD (on his belly, propped on his forearms) with the knees straightened until the shins lie level, the feet pointed level behind them, the knees swung in to 0.7 from the midline at the same height (thighs pitched/swung at the hip). Moves (15 frames = 0.5 s, eased; was 90 / 0.8): the hips rise 1.6 and settle; chest and thighs re-aimed each frame so the shoulders and hands stay put (the knees slide ~0.6 with the thighs). Looped with DFANM (`LOOPED_C`). First used in Tifa's devoted scene; the mission position. | `_cloud_thrust` (`THRUST_*`) |
| ZCTB | zctb.a | HBGB's first frame (knelt, sitting back, thighs ~54 behind upright; one knee higher and further forward). Moves (15 frames, 0.5 s, eased, looped): pelvis and thighs swing 40 forward about the line through both knees (hips up ~2 and forward ~3), torso and arms ride along unturned; knees, shins and feet stay put. The dog position. | `_cloud_pound` (`POUND_*`) |
| ZCTC | zctc.a | EIAB (sitting comfortably, one knee up) with each whole leg swung out about the vertical at its hip until the thigh points 30 out from straight ahead (/\ from the front); both frames, held. Was the head position (no scene uses it since the head layout became `stand`). | `_cloud_spread` (`SPREAD_ANGLE`) |
| ZCTD | zctd.a | GREA (on his back, looking right) with the head turned to face straight up and tilted 30 forward (chin to chest, looking at her), the arms raised 30 off the bed; the hips thrust 1.5 up and back every 15 frames (0.5 s), shoulders on the bed (chest and thighs re-aimed each frame). Cowgirl / ontop. | `_cloud_buck` (`BUCK_*`) |
| ZCTF / ZCTG | zctf.a / zctg.a | ZCTE for edge (user): arms 60 forward (twice ZCTE's), the left thigh raised to 100 forward of vertical with the knee bent only 10 (the raised leg rides with the hips: only the right foot stays planted). ZCTG = the same in 8 frames (twice as fast), after Tifa's "Faster!" (`standlf`) | `_cloud_stand(ctx, CLOUD_EDGE..., lift)` |
| ZCTE | zcte.a | ACFE (standing) with the knees bent 20 (thigh 10 forward, shin 10 back from vertical), the torso tilted 25 forward from the hips, the arms 30 forward (see below); the root lowered so the feet stay on the floor. Moves (15 frames = 0.5 s, eased, looped): the hips thrust 1.5 forward and back (thighs re-aimed to the knees, feet planted), the arms swing 10 in towards the midline on the forward thrust and back out on the return (user). The head position (second version): on the floor left of the bed, facing screen-left; also the edge position, facing the bed (screen-right) behind the bent-over girl. | `_cloud_stand` (`STAND_*`) | Since (user): right arm 70 forward, left 30, each forearm turned 20 in at the elbow (also head reverse's Cloud).

Cloud's skeleton (AAAA.HRC, 21 bones) has the same bone names as the dancer's; his
standing root sits 13.5 up, the floor at y 0 once the stored root height is negated.
| hbgb | HBGB.tak | knelt, thrusting motion (like CPR) | as he is |
| hbgc | HBGC.tak | knelt, looks to the side | as he is |
| hbfe | HBFE.tak | knelt, rubbing his face | as he is |

Fields that use them in the original game (for the exact spelling): GREA/GREB/GREC
gninn, AVDD/AVEA rckt32, ENJE/ENJF sinin2_1, HBGB/HBGC/HBFE rcktin6, EIAB nivgate2,
FTIB coloin2.

## Dates (660): sitting poses

| Anim | File | Pose | Built by |
|---|---|---|---|
| ZDLC | zdlc.a | Cloud (AAAA) sitting on a ledge: from ACFE, each thigh swung forward to level (about the body's side axis; models face -z, the toes splay out so they don't give "forward"), the knee bent back 90 so the shin hangs straight down, arms 25 forward; hip joints 1.5 above the root's floor (the water tower rim). One frame. | `660_dates._ledge` |
| ZDLT | zdlt.a | Tifa (AAGB) the same, from ABCD. | `660_dates._ledge` |

The gondola and capsule seats use the gondola models' own sitting anims (bwhlin: Cloud GDAB, Tifa GDEE).
| ZCTH | zcth.a | ZCTE for the dates' koala hug (user): leaning back 15 instead of forward, arms 55 forward, forearms turned 75 in round her; same thrust. | `620._cloud_stand(lean=-15)` |
| ZDKT | zdkt.a | Tifa (bare copy ztfa.hrc, AAGB bones) koala-hugging standing Cloud (ZCTH), as the user laid it out: leaning 10 forward onto him (head upright); arms raised 95 forward (85, then 10 more: user); each thigh raised 85 forward, spread 45 outward (about the vertical), knee bent 90 about its own hinge (thigh x up), so the shins hang beside his legs; then the pelvis and legs tipped up 10 more together (user). Since (user): arms turned 10 in, her head nodding 12 forward as she rises, her pelvis 0.6 closer to him (KOALA_BACK 1.4); ZCTH's arms turned 10 out (`arms_out`). One frame per ZCTH frame: her pelvis rides in front of his (bouncing 1.5), and her upper body turns forward by asin(pelvis back / torso height) so her head keeps its place. Her XYZI = his, DIR + 128. | `660_dates._koala` |
| ZCTI | zcti.a | ZCTE (head Cloud, right arm 70 / left 30, forearms in) in 8 frames: twice the speed (Aerith's date, after she demands more). | `620._cloud_stand(nframes=8)` |
| ZCTJ / ZCTK | zctj.a / zctk.a | ZCTE for Aerith's head scene (user: his hands on her head): both arms 45 forward-down, turned 8 in, forearms 15 in; ZCTK 8 frames (x2). | `620._cloud_stand(arms_out=-8)` |
| ZDKA / ZDKB | zdka.a / zdkb.a | Aerith (AUFF, her own model) kneeling before standing Cloud ("head", user): shins and feet flat behind, thighs 75 forward (sitting back on her heels: kneeling upright her head was at his chest), arms 40 forward; above the knees tipped 10 forward and rocking 10 more (head upright); her face 7.5 in front of his pelvis (3, a head width further, then a little closer: user); ZDKC = ZDKA looking up (chin up 35, on Cloud's "Look at me"); ZDKB (fast) looks up too (same XYZI, turned round). ZDKA 15 frames, ZDKB 8 (fast). | `660_dates._kneel` |
| ZDKD | zdkd.a | Aerith kneeling on her heels (as ZDKA) bowed: above the knees 40 forward, head 25 more; one frame, where she is (no offset). Her third date: she looks at Cloud, gets up, walks over, kneels and bows (user). | `660_dates._kneel(bow=)` |
| ZDLA | zdla.a | Aerith sitting on the water tower ledge, as ZDLC/ZDLT (from AVBF). | `660_dates._ledge` |

Note (renders): `ff7.fieldanim.forward` needs the root position with y negated ([x, -y, z] as stored); a render that passes the stored root draws each model at the wrong height relative to another (scratch pair renders were off until fixed).
| ZDBS / ZDLS | zdbs.a / zdls.a | Scarlet (AMCC) sitting: bench (feet on the floor, ankles where she stood) / ledge, as ZDLC. Her skirt bones hang from her hips (not children of the thighs). | `660_dates._ledge(bench=)` |
| ZDSW / ZDSX | zdsw.a / zdsx.a | Scarlet (skirtless zsca.hrc) against a wall in front of standing Cloud (user): torso 45 forward, arms 95 forward (straight out), right thigh 80 up with the knee bent 90, head lifted 30 and turned 45 to her left; one frame per ZCTE (ZDSX: ZCTI, x2) frame, her pelvis 3.5 in front of his and following it by pivoting on her left ankle (planted). Same XYZI and DIR as Cloud. | `660_dates._wall` |
| ZDBC / ZDBE / ZDLE | zdbc.a / zdbe.a / zdle.a | Our bench (feet on the floor) / ledge sits: Cloud (bench, for his seated part twos), Elena (bench, ledge). | `660_dates._ledge` |
| ZCTL / ZCTM | zctl.a / zctm.a | Bare Cloud seated (ZDBC) for Elena (user): ZCTL his right arm raised 70 and swung down onto her, lowest at the middle of 15 frames (played once per spank, slap sound at the middle); ZCTM the same swing with his hips 1.0 up at the middle (seated thrust, 0.5 s). | `660_dates._cloud_seated` |
| ZDEA / ZDEB | zdea.a / zdeb.a | Bare Elena (zela.hrc) with seated Cloud (same XYZI and DIR): ZDEA face down across his lap (her length along his side axis; upper body and legs hanging 25 over the sides; pelvis 1.8 above between his thighs' middles); ZDEB sitting on his lap facing his way (her bench pose), bouncing with ZCTM's hips plus 1.0. | `660_dates._lap` |


## Movie minigame (670)

Ruby = midgal_woman (CBFE.HRC, jun_i2 model 6): the Honey Bee dancer's skeleton (same bones and lengths; its
l_chest / r_chest are called non_1 / non_2) and the dancer's DXID / DXHF / DXIA stand / walk / run, so the
dancer poses play on her. Her bare copy ZRHA.HRC (`670._bare_ruby`): upper arms, skirt, thighs, shins and feet
in skin colour, the boots shrunk to feet, the skirt's box round each thigh pulled in, the skirt's back corners
pulled in (user's sketch).

| Anim | Pose |
|---|---|
| ZM<p><s> / ZN<p><s> | Ruby / bare Cloud: position p (A mission DZBT+ZCTA, B cowgirl DZBL+ZCTD, C dog DZBF+ZCTB, D edge DZBG+ZCTF, E head reverse DZBH+ZCTE, F head DZBK+ZCTE) resampled from 15 frames to 20 / 15 / 11 / 8 (s = 0..3: the thrust speed steps). `670._speeds`. |

Cameraman (junon_report2, FCGD.HRC from junone2 model 6): FDCB holds the camera low (idle), FFBC films with it at his eye, FDCD films crouching.
