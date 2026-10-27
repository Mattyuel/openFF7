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
| DZBT | dzbt.a | on her back facing up, thighs raised 45 ((user, since) `MISSION_LEG_RAISE` 28: knees straighter, ~64; then 18: ~39; (user) mission legs turned out `MISSION_TURN_OUT` 45 about each hip-ankle line) and spread 45 ((user) `MISSION_LEG_SPREAD` 60 for mission), knees bent (~101 at 45) so the feet are planted flat, arms along her sides; hips where DZBA has them. Moves (15 frames = 0.5 s, eased): the knees fall open 8 degrees and close (each leg turns about its hip-ankle line) and her whole body bounces 1.2 up off the mattress and back, her hips thrusting 1.0 more (shoulders and knees ride only the bounce: chest and thighs re-aimed); arms angled 20 out from her sides; head tilted 25 forward (chin to chest), rocking 12 further forward as she comes down and back as she goes up (user) | `_on_back` (`LEG_RAISE`, `LEG_SPREAD`, `POSE_ROCK`) |
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
| standl / standlf | ZCTF.tor / ZCTG.tor (ours) | edge: as stand, arms further forward, left foot up on the bed's end; standlf twice as fast | as he is |

### Our own pose for Cloud (built at build time, written to char.lgp)

| Anim | File | Pose | Built by |
|---|---|---|---|
| ZCTA | zcta.a | AVDD (on his belly, propped on his forearms) with the knees straightened until the shins lie level, the feet pointed level behind them, the knees swung in to 0.7 from the midline at the same height (thighs pitched/swung at the hip). Moves (15 frames = 0.5 s, eased; was 90 / 0.8): the hips rise 1.6 and settle; chest and thighs re-aimed each frame so the shoulders and hands stay put (the knees slide ~0.6 with the thighs). Looped with DFANM (`LOOPED_C`). First used in Tifa's devoted scene; the mission position. | `_cloud_thrust` (`THRUST_*`) |
| ZCTB | zctb.a | HBGB's first frame (knelt, sitting back, thighs ~54 behind upright; one knee higher and further forward). Moves (15 frames, 0.5 s, eased, looped): pelvis and thighs swing 40 forward about the line through both knees (hips up ~2 and forward ~3), torso and arms ride along unturned; knees, shins and feet stay put. The dog position. | `_cloud_pound` (`POUND_*`) |
| ZCTC | zctc.a | EIAB (sitting comfortably, one knee up) with each whole leg swung out about the vertical at its hip until the thigh points 30 out from straight ahead (/\ from the front); both frames, held. Was the head position (no scene uses it since the head layout became `stand`). | `_cloud_spread` (`SPREAD_ANGLE`) |
| ZCTD | zctd.a | GREA (on his back, looking right) with the head turned to face straight up and tilted 30 forward (chin to chest, looking at her), the arms raised 30 off the bed; the hips thrust 1.5 up and back every 15 frames (0.5 s), shoulders on the bed (chest and thighs re-aimed each frame). Cowgirl / ontop. | `_cloud_buck` (`BUCK_*`) |
| ZCTF / ZCTG | zctf.a / zctg.a | ZCTE for edge (user): arms 60 forward (twice ZCTE's); (user, since) the left thigh aimed 100 forward of straight down and turned 10 out (to his left), the shin straight down, the foot level (ACFE's): the ankle ~20 above the floor, 15 ahead (against the bed's end). Each stroke: hips forward `EDGE_THRUST` 2.5 (x ZCTE's 1.5), both legs re-aimed by two-bone IK so both feet stay put (asserted), the upper body leaning back up to `EDGE_LEAN_BACK` 12 so the head moves ~3.7 to the hips' 8.5. (User, since) the hands stay put on her behind (arm IK every frame against his thrust, `hold="still"`, wrists drawn `HOLD_STILL_IN` 0.12 towards the shoulders for elbow slack). ZCTG = the same in 8 frames (twice as fast), after Tifa's "Faster!" (`standlf`) | `_cloud_stand(ctx, CLOUD_EDGE..., lift=(hip, out), hold="still")` |
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
| ZDBE | zdbe.a | Our bench sit (feet on the floor) for Elena. | `660_dates._ledge` |
| ZDEF / ZCTP | zdef.a / zctp.a | Elena's part two (user: standing, every place): bare Elena (zela.hrc) on all fours, held (thighs straight down, shins flat behind, torso 15 head-up, arms straight angled forward, head 25 up; hands and knees on his floor; her hips 7 ahead and as far to his right as his straight arm reaches, inside the anim, same XYZI and DIR); bare Cloud ZCTP (user, since) on one knee: from ACFE, the left (back) thigh straight down, its shin flat behind on the floor, the right (front) thigh 110 forward (20 above level) with the shin angled back until the ankle is at its standing height, foot flat; upright (user, since: KNEEL_LEAN 0, closer to her; was leaning 20); her hips 7 ahead of him; (user, since) the right arm straight (shoulder to fingertips in one line), swung only at the shoulder: out 60 back (about the vertical) and 20 up, quickly in over 3 frames to the hand on the top of her behind at the middle of 15 frames, eased back out (played once per spank, slap at the middle). | `660_dates._elena_fours` (SWING_*) |
| ZDEK | zdek.a | Elena's part three: Tifa's koala hug (`_koala` on zela.hrc, with ZCTH) turned 180 inside the anim (`_turn_round`), so both keep his DIR. | `660_dates._koala` |


## Movie minigame (670)

Ruby = midgal_woman (CBFE.HRC, jun_i2 model 6): the Honey Bee dancer's skeleton (same bones and lengths; its
l_chest / r_chest are called non_1 / non_2) and the dancer's DXID / DXHF / DXIA stand / walk / run, so the
dancer poses play on her. Her bare copy ZRHA.HRC (`670._bare_ruby`): upper arms, skirt, thighs, shins and feet
in skin colour, the boots shrunk to feet, the skirt's box round each thigh pulled in, the skirt's back corners
pulled in (user's sketch).

| Anim | Pose |
|---|---|
| ZM<p><s> / ZN<p><s> | Ruby / bare Cloud: position p (A mission DZBT+ZCTU, B cowgirl DZBL+ZCTD, C dog DZBF+ZCTN, D edge DZBG+ZCTF, E head reverse ZRHN+ZCTX, F prone ZRPA+ZCTO, G behind ZRWA+ZCTE, H holding ZRKA+ZCTH, I 69 ZR6A+ZCTY, J head ZRTA+ZCTQ) resampled from 15 frames to 20 / 15 / 11 / 8 (s = 0..3: the thrust speed steps). `670._speeds`. Then per pause position (head reverse, 69, head) ZM<p>9 / ZN<p>9 = frame 0 held (pulled back; the head turn aside was removed, user) and ZM<p>8 / ZN<p>8 = frame 7 held (the deepest: the hold, user), then hers only ZM<p>7 (`670._try_anim`; (user, since) 90 frames = `_movie_group.SQUIRMS`: the try below, then a squirm (legs swayed 14 about her body's axis, twice: hips wriggling), then a desperate one (pull 0.45, a fast tremble, legs 20 and arms 25 alternately: pushing at him); her head stays on him; first, 30 frames, played 6 s into the hold: from the deepest her whole pose eased `TRY_PULL` 0.3 of the way towards frame 0, straining with a small tremble, and back: she tries to pull away and can't; 672: ZMQ7); `670.hold_index`. |

Cameraman (junon_report2, FCGD.HRC from junone2 model 6): FDCB holds the camera low (idle), FFBC films with it at his eye, FDCD films crouching.
| ZCWA | Honey Bee dancer (BADD): cowering on the ground (626): from DXID, thighs 115 forward-up, shins turned back down until the ankles reach the floor, pelvis on the floor, leaning in 25, head ducked 25, (user, since) upper arms forward and a little down, forearms up and in, hands before her face; 8-frame tremble (upper body turning +-3). | `626_hb_rescue._cower` |
| ZTSA / ZTSB / ZTSC / ZTSD | The four customers (626: sailor, soldier, punk, manager; each its own skeleton on Cloud's layout), user's slap: from AAFE frame 0, elbow bent 25, the right arm raised 30 out to his side (about his forward axis) while swinging 50 outwards (about the vertical through the shoulder) over 8 frames, then 110 inwards in 3 (the hit, frame 11: SOUND 0x76), held 3, back to his side in 6 (21 frames). (User, since) the whole upper body (all but the hip joints and legs) bent `THUG_BEND` 20 forward throughout. ZTBA-D = frame 0 alone: his idle (bent over, arm down). | `626_hb_rescue._slap` |
| ZRTA | Ruby: DZBK with the head turned HEAD_BACK (20) further back, chin up (user), the minigame's "head". `670._head_back` |
| (model) | Bare Cloud (zcla.hrc) has a second part on the hip bone (user): ZCLP / ZCMP.p, a plain skin-coloured box `MEMBER_LEN` 2.31 long (user: 2.2, then 3.3, then 30% shorter), `MEMBER_W` 0.975 square, forward from the crotch; it follows the pelvis in every anim. `620._bare_cloud_member` |
| (model) | Field models are rigid parts, one per bone (.hrc -> .rsd -> .p): no skinning or vertex weights, so a body can't be one mesh that bends at the joints; parts overlap at the joints instead (rounded knee / shoulder tips, capped ends) to hide the seams. |
| ZCTS | (no longer built) bare Cloud: ZCTE (`620._cloud_stand(knee=70)`) with the knees bent 70, pelvis low. Was the Honey Bee "head" (`standlow`), which now uses ZCTQ (user). The `knee` parameter remains. |
| ZCTR | bare Cloud: ZCTP with the head turned 40 to his right (gondola only, user). `660._elena_fours` |
| ZCFA | Cameraman: FDCB's first frame only, his default anim in Wall Market (user: still there). `670._wall_market` |
| ZCTQ | bare Cloud: ZCTE (`620._cloud_stand`) with the left thigh turned `HEAD_STEP` (20) forward and the knee bent until the foot is on the floor (gap < 1.0, asserted), pelvic thrust x `HEAD_THRUST` (2) (user). The minigame's "head" and (user, since) the Honey Bee "head" (`standlow`); built by 620. (User, since) legs turned `HEAD_LEGS_OUT` 45 out at the hips, fingertips `HOLD_SIDE` 3.2 out (outside her head). Knees bent (two-bone IK each frame, ankles fixed) until the pelvis is at `HEAD_LOW` 3/4 of its height (was 2/3), torso leaning `HEAD_LEAN` 20 (was 25), thrusting from there; both hands on the sides of her head (`hold`: fingertips `HOLD_SIDE` 1.5 either side of the middle of the dancer's DZBK head and `HOLD_NEAR` 0.7 towards him, elbows `HEAD_ELBOWS_OUT` 2 out, `HEAD_HOLD_GAP` 38/3.41 ahead and `HEAD_RIGHT` 6/3.41 to his right, fingers down tipped `HOLD_IN` in; arm IK every frame, asserted within 0.1). (User, since) only the pelvis thrusts: each frame the chest and everything above it turn back about the pelvis's top so the neck keeps frame 0's forward position, the head turned back level (head and hands move < 0.5 per stroke, asserted; `still_upper=HEAD_STILL_UPPER`), and both feet are held at ACFE's flat standing orientation (turned out with the legs). |
| ZCTN | bare Cloud: ZCTB (dog) with the chest and both shoulder bones re-aimed every frame to their frame-0 ends, head and arms keeping frame 0's turn: the hips thrust, the upper body stays (within ~1 unit) (user). `670._cloud_dog` |
| ZCTO | bare Cloud: ACFE tipped face down (feet in line with the shins), pelvis + upper body turned CP_TORSO (30) up from the bed with the legs flat, head CP_HEAD (15) down, upper arms straight down, forearms forward to the bed, hands flat pointing ahead; each 15 frames the hips rise CP_LIFT (1.8) with the knees bending (thighs re-aimed to their knees) and the upper body held (chest/shoulders re-aimed, ~0.5 drift), and back (user). The minigame's "prone", PRONE_UP 12 above her (user, since: raised a bit; was 8). `670._cloud_prone` |
| ZMK0 / ZML0 / ZMM0 / ZMN0 | Ruby (and each co-star retargeted, prefix + K0..N0): the group shoot's waiting poses: lying straight on her back, arms by her sides, head tilted back 50 (K / M), the head kneel's frame 0 (L / N); the head turning left/right now and then (`IDLE_A` / `IDLE_B` timings, ~250 frames). `670._still_poses` |
| ZCTU | bare Cloud: ZCTA with (user) the shins and feet still and flat: the thighs (and pelvis) swing `MISSION_PIVOT` 22 (user, since: more thrust; was 14) about the line through both knees, the knees `MISSION_KNEES` 1.4 either side of his midline (user: legs apart; `knee_gap=`, was 0.7), so the pelvis thrusts forward and down along that arc, the upper body re-aimed back at its shoulders (620 `_cloud_thrust(pivot=)`). The minigame's mission. |
| ZRHN | Ruby: DZBH with (user) the hanging head rocking `HEADREV_NOD` 15 each way about her side axis with each stroke (620 `_on_back(head_nod=)`). The minigame's head reverse. |
| ZRWA / ZRKA | Ruby (CBFE, from DXID): (user, since) "behind" with her hands on the bed (`670._behind_bed`: leaning `BEHIND_LEAN` 40, knees bent `BEHIND_KNEE` 30, each wrist `BEHIND_REACH` 0.92 of the arm's length from the shoulder down on the mattress (54 above the floor), hands flat fingers forward; per frame her pelvis follows Cloud's ZCTE pelvis along z, the upper body pivots at the pelvis until the shoulders are back where they were, arms and legs re-aimed by two-bone IK so hands and feet stay put (asserted); was 660's `_wall`) / Tifa's koala hug (`660._koala`, on ZCTH, DIR + 128): the minigame's "behind" / "holding" (user). |
| ZRIA / ZCTV | (user) special "insert" (672): her face down, shins flat, thighs upright, torso sloped to the shoulders on the bed, arms back, head up (ZRIA static; ZMP0-3 = it with her pelvis (hip bone) rocking `INSERT_ROCK` 6 degrees each way in time with his stroke, the waist dipping ~0.5 and back towards him as he goes in, everything else keeping its turn: `_girl_insert_rock`, user); Cloud squatting over her, hands on his knees, lowering along his member's line; ZCTV built per stroke length as ZNP0-3 (120/90/60/15 frames). |
| ZRFA / ZCTW | (user) special "finisher" (672): Cloud thrusting on his back (ZCTD; ZCTW = its frame 0, unused); she astride facing his feet, leaning back 45 on straight arms, hips riding his by turning about her shoulders; (user, since) her legs up: thighs raised `THIGH_UP` 45 from 45 down (level), `THIGH_OUT` 30 out (a V), knees bent so the shins go down to the bed, feet flat on it and planted (two-bone IK each frame, asserted). |
| ZMS / ZNS / ZGS, ZMT / ZNT / ZGT, ZMU / ZNU / ZGU (+0-3 speeds, S/T 9 / 8 stops, ZMS7 / ZMT7 tries, ZMV0 / ZMV1) | (user) 673 Blast-off, girl (Ruby's skeleton, retargeted as <prefix>S0.. per girl) / bare Cloud / bare Cid (ZCIA). S Rocketman: Cloud seated on a bench (thighs level, shins hanging, leaning back 12, pelvis lifting `RM_BOUNCE`, hands IK'd to her hips); she on his lap facing his way, her pelvis + chest re-aimed by two-bone IK so her neck runs level and bobs towards Cid, her head's crown to him tipped `RM_FACE_UP` up, arms IK'd to his thighs; Cid standing turned round, upper body leant back (at the waist), his member tip on her mouth path, right hand IK'd to her crown. T Twin Jets: her = ZRTA, Cloud = ZCTQ, Cid's member root where Cloud's is, leaning 35 forward, both hands on her head; V0 / V1 her turn: ZRTA's frame 0 turned 180 about her root (either way), 30 frames. U Exhaust: ZNUK (Cloud's koala stand ZCTH with knees bent, `low` 0.8) / ZMUK (her koala on it, 660 `_koala(his_anim=)`), Cid behind her turned round, tip at her seat's entry following her bounce, hands on her hips. Cid's legs IK'd to planted feet, raised onto his toes when needed (`TIPTOE_MAX`). `_blast_poses`. |
| ZN<letter>L | (user) Cloud's lesson (670 `_lesson_anim`): his stroke's frame 0 held, the right arm straight, a short wind-up `LESSON_OUT` 0.55 of the way out to his side over `LESSON_RAISE` 4 frames, swung (speeding up) to `LESSON_DOWN` 45 down and `LESSON_IN` 30 in across him (to her face) over `LESSON_SWING` 5, no hold: 670 `lesson_slot` plays it once (slap sound at the swing's start) then the pulled-back hold frame; directions from his body (up = pelvis to neck, right = between the shoulders). ZNJL head, ZNEL head reverse, ZNIL 69, ZNOL group end, ZNSL Blast-off Rocketman. |
| ZCTX / ZCTY | (user) ZCTE (head reverse) / ZCTD (69) with the resisted push (`620._stroke(resist=True)`): the forward push speeds up to `RESIST_AT` 0.8 of its depth by its halfway point, then suddenly slows, creeping to full depth over `RESIST_CREEP` 0.3 of the push, held at full depth for the rest of it (a very slight pause: frames 6-7 of 15), and eases back out over the stroke's second half (user). ZCTQ (head, also the Honey Bee head) has it too. (User, since) ZCTX's arms: straight (shoulder to fingertips in one line) out in front at 90 degrees to his torso (pelvis to neck: angled down as far as he leans back), turned in at the shoulders until the fingertips are `HEADREV_REACH` 0.5 of the way from the shoulder's side to his middle, re-aimed every frame so they stay steady while he thrusts (hands move < 0.6): holding her back (620 `_cloud_stand(reach=)`). |
| ZCTE / ZCTI | (user, since) `still_upper`: only the hips thrust (head reverse, behind, the dates' part twos). |
| ZNW0-3 / ZNV0-3 / zcz5 | (user) beach party (679, `_beach_poses`): bare Cloud lounging on a lounger (660 `_lounge` with the upper body `CLOUD_BACK` 42 back: zcz5), his root rising and falling with ZNB<k>'s (the cowgirl's beat, same frame counts), hands on her hips by two-bone IK (targets out of reach are pulled in to `REACH` 0.96 of the arm). W: she (ZMB) rides facing his feet, V: facing him (DIR + 128); her spot `sunbed_offset` (her root `W_RIDE` 10 above his). |
| <prefix>Z5 | (user) beach party: lounging (660 `_lounge`, `LOUNGE_BACK` 42) built per girl on her own skeleton, its root moved by -`sunbed_offset` (`lounge_at`) so it plays at a rider's spot: the waiting / watching pose on the loungers. |
| ZMY0-3 (+ per girl) | (user) beach party "waves": the edge girl (ZMD) with her hands on her knees (two-bone IK, `KNEE_HANDS` 0.25 up the thigh) instead of on a bed; Cloud's edge ZND behind her, in the shallows. |
| ZMX0-3 / ZNX0-3 | (built by `_beach_poses` but not used: from this camera Cloud's back hid her) a lounger mission: ZMA's upper body turned `RECLINE` 48 up; ZNA's turned `KNEE_UP` 58 back, head down 35, hands on her thighs. |
| <prefix>W5 / <prefix>X5 | (user) chamber (679_chamber, `_chamber_poses`), per girl on her own skeleton: standing with the wrists together `OVERHEAD` 2.2 above her head (two-bone IK) / kneeling up (`_kneel`: thighs straight down, shins flat behind, feet soles up, shins 0.45 above the floor) with the wrists together `BEHIND` 2.2 behind her pelvis. The girls' homes. |
| ZMW0-3 / ZNK0-3 | (user) chamber "chained": she kneels up, wrists held at one point over her head every frame (IK: bound), her thighs pushed `PUSH` 4 forward about the knees at his deepest; Cloud kneeling up behind her, knees `CLOUD_SPREAD` 42 apart and thighs tilted forward (solved so his tip meets her entry at the deepest frame: Ruby kneels ~2 units lower than him), his thighs swung `THRUST` 14 about the knees (`_swing`: shins fixed, the upper body moved, not turned), hands on her hips. 20/15/11/8 frames, deepest at the middle. |
| ZMX0-3 / ZNN0-3 | (user) chamber "offering": ZMK0 (lying on her back) with both legs straight up in a V (`LEGS_V` 22 out), hips lifted so her entry is level with his tip, sliding `SLIDE` 0.35 up the bed at his deepest; Cloud kneeling up (`CLOUD_TILT` 18) at her hips facing her, hands on her shins. (Not K / L: ZMK0 / ZML0 are the group's still poses.) |
| ZMZ0-3 | (user) chamber "mating press": ZMA (mission) with each leg folded `FOLD` 45 further towards her chest and `FOLD_OUT` 32 out to her side, about the hip; Cloud's mission ZNA. |
| ZNM0-3 | (user) chamber "throne": ZNB's frame 0, one frame (Cloud lying still); she in ZMB with her root `THRONE_UP` 7 above his mouth. |
| ZIUA.HRC / ZI.. | (user) the island nurse (679_nurse): ithos model 8 BTEC.HRC undressed with the standard female body (`_female_body.apply`, tag N, her face's skin, nipples ZKNL/R) = ZIUA.HRC; her **suite**: every anim Tifa has (ZV<suffix>) that Ruby has as ZM<suffix>, retargeted onto her as ZI<suffix> (117; 670 `_retarget`). Her skeleton is the dancer's bone names with Ruby's lengths. |
| ZOA-ZOE 0-3 / ZJA-ZJE 0-3 | (user) the nurse's own positions (`_nurse_poses`, user: "unique, not Tifa's"), built on Ruby (ZO..) and retargeted onto her (ZJ..); Cloud the patient on his back throughout. A checkup: she kneels between his spread legs facing his head, bent down (pitch solved: mouth at his base, `FACE_UP` 0.7), backside high, head bobbing `BOB` 9, hands on the bed (IK). B arched: ZMB facing him, upper body leant `ARCH` 35 back, hands on his thighs (IK). C spoon (with ZNZ): the edge pair (ZMD / ZND) turned onto their sides about her root, him `SPOON_BEHIND` 14 behind. D stacked: ZMA raised `STACK_UP` 2.6 riding his root, feet IK'd wider (`STACK_WIDE` 1.6) on his ZNB. E saddle: ZMB leaning `SADDLE_LEAN` 25 forward, hands to his shins. `PLACE` = her XYZI from Cloud's. |
| ZNY0-3 / ZNY9 / ZNZ0-3 | (user) bare Cloud, the patient: ZNB with his legs `SPREAD` 22 apart (each leg turned about the bed's normal at the hip) / ZNY9 one frame lying still between visits (his ACFE stand laid flat on his back along ZNB's body line, `_lying`) / the spoon's ZND on its side. |
| XZ<letter>0 / X?<letter>0 | (user) the school dance (682, `_dance_poses`): built on Ruby (XZ..) and retargeted per girl (XT Tifa, XA Aerith, XY Yuffie, XE Elena, XS Scarlet); a beat = 15 frames. A bow (1 frame), B wake (8 beats once: head snaps up, arms to a T and down), C march (2-beat loop, high knees, arms swinging), D squat sway (4: deep squat, hands on knees, shoulders swaying), E shrug (2: shoulder shrugs, hip roll, fists up), F punch (2: punches at the sky, bouncing), G head-bang (1: bent at the waist), H side step (4: arms overhead), I arm wave (4: a ripple arm to arm), J kick (4: front kicks, arms out), K spin (4 once: a full turn), L jump (2), M back-bend (8 once), N run (1: on the spot), O yankee squat (4: elbows on knees, staring), P point (1 frame: the finish). Poses by `_Body.frame` (lean / head / arm and ankle IK targets). |
| QW<part><tier> / QT.. / QU.. / QB.. | (user) Sector 7 Workout (683, `_workout_poses`): one squat rep (down and up) per anim, `PERIODS` 60 54 49 44 39 35 32 29 frames for tiers 0-7 (10% faster each); part A clothed, B undressed. Hers on Ruby (QW..) retargeted to the spandex Tifa (QT..) and her tied-hair bare copy (QU..): A arms forward, leaning further each tier; B bent over further (hands on knees from tier 2). Cloud's (QB.., AAAA / ZCLA) built frame by frame against hers: her drop scaled to his height, hands on her hips (`_dance_poses` "at" targets), `gap` behind her shrinking by tier, his hips pushing in at the bottom in B; from part A's later tiers and through B his hips also thrust back and forth during the rep (`push`, twice a rep in B from tier 3) and her body rocks back into it. (User, since) styles (`STYLES`, letters `LETTERS`): QWA/QWB the above, QWC sumo (feet wide, hands behind her head; Cloud's stance wider), QWD Cloud's left leg cocked up and out (`COCK_LEG`), QWE her folded over (`TOE_LEAN`) with her hands hanging to her toes; the holds are no new anims: CANM!2 on the playing anim's bottom frame (her call: a few frames on from it, held). |
| YB / YC / YD.. | (user, round 2) Besties (687, `_besties_poses` on the rig `_besties_rig`): Cloud YB / Tifa YC / Aerith YD + position E edge, R ride, L lick, F share in front (Cloud G = Aerith in front), B share behind, S stack (U = P 1) + speed 0-3 (20/15/11/8 frames); holds YCF8/YDF8 deep, YCF7/YDF7 tapping out (30 frames), YCF9/YDF9 pulled back, YBF8/YBG8. Built on the bare models directly in one scene space across the bed's left edge; contacts solved per frame by `fit`; girls' hips rocked hard (EDGE_TIFA rock 18, RIDE rock 20, ...), heads lagging, hair hanging (or spread along the bed lying). QPT1 / QPA1 / QPC1 sitting on the bed's edge in the dresses / Cloud (660 `_ledge`, root moved back `SEAT_IN + SEAT_OUT`). |
| QHA-D / QHU / QR / QS | (user) Hostile Takeover (686, `_hostile_poses`): QHA0-3 / QHB0-3 Cloud bowing into Scarlet (hands on her hips / on the table), QHC / QHD the same into Elena, QHA8 / QHC8 held; built by `cloud` (face solved onto her entry, pelvis turned `PELVIS_TILT`). QHU0-3/8/7 on Ruby: (user, since) kneeling, leaning back (sitting back on her heels, arched about her waist by the angle 686 solves per girl, hands on the floor behind her; built with `_besties_rig`; was on her back, propped up), head bobbing / tapping out -> QR.. Elena, QS.. Scarlet. At entry scale 768. |
| QYF / QJF | (user) Tickets, please! since: Jessie under Tifa (`_tickets_poses.jessie_under`): 620 `_on_back` held still, the head alone bobbing `NOD` (0-3 speeds, 8 held, 7 shaking, 9 still). Cloud's QZA / QZB now with his pelvis turned so the member is level (`_level`). |
| QYE / QJE / QZ / QN | (user) Tickets, please! (685, `_tickets_poses`): QYE0-3/8/7/9 = Ruby's head reverse (ZME..) with both legs straight up (`legs_up`: each leg turned rigidly to point up, `LEGS_SPREAD` apart, knee straightened); QJE.. the same on Jessie's XJEA (root re-centred under her hips); QZA-D0-3 Cloud solved against Tifa's ZVC (A, B foot on the seat) and Jessie's QJE (C hands on her shoulders, D behind his head), QZC8 his hold; QNT9 Tifa's dog frame 0 (waiting); QNTS / QNJS sitting on the bench (660 `_ledge`). |
| QXC0-E0 / QEC0 / QED0 / QVE0 | (user) Going up (684, `_going_up_poses`): QXC0 the crawl on Ruby (her dog frame 0, `CRAWL_FRAMES` 30: thighs / arms swing `CRAWL_LEG` / `CRAWL_ARM` about the side axis in opposite pairs, the lower body yaws `CRAWL_SWAY` about the waist) -> Elena QEC0; QXD0 waiting on all fours (`SHAKE` hip shake, `LOOK` head to her right) -> QED0; QXE0 kneeling (Ruby's head ZMJ9) turning to the camera and tilting her head right (`CAM_LOOK`, `TILT`) -> Tifa QVE0 (XWUA). |
| QKC0-3 / QKJ0-3 | (user) Going up's Cloud variants (684, `_going_up_poses.build_cloud`): ZNC0-3 with his legs swapped (each leg's world rotations from the other, mirrored in x: his left knee up, the camera's side) and ZNJ0-3 with his hands behind his head (arm IK to `NAPE` off his neck joint each frame). The head hold uses the movie's ZNJ8 / ZVJ8 (held deep) and ZVJ7 (her squirm = tapping out). |
| QFC0-3 / QKS0-3 / QLJ0-3 / QKU0-3 | (user) Going up's third style (684): Elena's dog strokes bent 10 up at the waist, head 25 back, hands kept (`_going_up_poses.bend`); Cloud squatting behind her, leaning 40 in, hands reaching for her head; Tifa's head strokes leaning 15 further forward, head 25 up; Cloud in a 3.8-wide sumo squat. Cloud's solved per frame (`_tickets_poses.cloud`). |
| QRU.. / QSU.. (686 under) | (user, since) the girl under Cloud in Hostile Takeover: left knee down (thigh 60 forward, sitting back), right foot planted ahead (IK), torso leaning back (bisected so her mouth meets his tip), left hand on the floor behind, right arm reaching up. |
| XGS0-3 / XGT0-3 / XGS9 / XGT9 / XGR9 / XGP9 / XHR9 / XHP9 | (user) Going There (690), bare Cloud over Tifa's insert ZVP<s> (672), one per insert speed (120 / 90 / 60 / 15 frames: frame 0 out, the middle in): XGS side-on (DIR 0x00, facing the camera; she faces 0xC0), standing over her hips, left foot planted behind her, right foot on top of her head (sole `HEAD_FOOT_UP` 1.0 above it), hips stroking `STROKE` 2.2 along his member, hands on his hips, head down; XGT reversed (DIR 0x40, facing her feet), pitched `PLANK_BOW` 112 into a plank, hands planted on the bed, legs straight out behind (toes near the bed past her head), hips flopping `FLOP` 2.4 by turning about his shoulders. Both fitted to her entry (672 ENTRY) at ZVP0's deepest frame. The 9s are one-frame stills (pauses): XGR9 / XHR9 = ZNR0 / ZVR0 frame 0, XGP9 / XHP9 = ZNP0 / ZVP0. |
| YHHE / YHIB / YHIF / YHJA / YHKK / YHHR / YHPU / YHF0-8 | (user) The Honey Bee shift (689): YH.. the dancer's DXHE / DXIB / DXIF / DXJA retargeted onto Tifa's dress AXJA (670 `_retarget`); YHKK her front kick (knee up, leg snapped out high, held, back; 30 frames, hit at 11); YHHR the hip rock (`_gestures._hiprock`) on AXJA; YHPU Cloud's three punches, the last an uppercut (AAAA, 36 frames, hits 8 / 20 / 32); YHF<k> customer k knocked flat on his back, stiff (`_fall` on his own skeleton: pitched back about the root over 14 frames, root dropped to lie, a bounce). |
| YXT0 / QXT9 / QXC9 / QXV9 / QXW0 | (user) The Basics (688): YXT0 Cloud kneeling behind Tifa on all fours, his face at her entry (fitted on her QXT9 = ZVC0's first frame held), hands on her hips, head wandering (48 frames); QXC9 / QXV9 the dog strokes' first frames (the pause poses); QXW0 the head wiggle (`_wiggle` on ZNJ0). |
| QOA0-3 / QOB0-3 / QOS0-3 / QOT0-3 | (user) Tickets, please! Tifa (685, `_tickets_poses.wander` on her QNC strokes / QNT9): A = the strokes x3 (one rep) with her head wandering (turn 7 / nod 4, one loop a rep), B = the same with her back arched 12 up at the waist, head turned 38 to her left, right arm reaching back to her hip, left hand re-planted; QOS/QOT = the still frame, as long as each tier's rep (60/45/33/24). |
| YCK0-3 / YDK0-3 | (user) Besties ride's kissing alternate (687 `_besties_poses._kiss`): Tifa / Aerith astride Cloud as YCR / YDR, bent forward until their faces meet, heads tilted 16 opposite ways, hands on each other's shoulders. |
| ZGHR | (user) Tifa's hip rock (`_gestures._hiprock`, any Tifa skeleton): hands on her hips (elbows out), hips swaying side to side twice in 60 frames, upper body countering, feet planted; the workout intro's line 2. |
| QKW0 / QZW0 / QHW0-1 / YBW0-1 | (user) Cloud's pull-out wiggle after a head hold (`_wiggle.build`: from frame 0 of his head stroke there, 684 ZNJ0, 685 Jessie's QZC0, 686 each P's stroke, 687 the share's speed-0 strokes): hips eased back `PULL` 1.4 over `IN_OUT` 10 frames, `CYCLES` 3 sways (root `SWAY` 1.1 to the side, pelvis rolled `ROLL` 13, waist countering `COUNTER` 1.45 x so his head stays within ~0.3 of the stroke's), eased back in; feet planted by two-bone IK. 62 frames, played once (ANIME1 in slot `SLOT` 7, REQEW'd by the director) after each hold's result while she holds her pulled-back pose (684 ZVJ9, 685 QJF9, 687 the holds' 9 pose). |
