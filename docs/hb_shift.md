# The Honey Bee Inn shift (Tifa works it)

(user: "let's work on a different minigame now; honeybee inn. keep a record of what we've done so we can
integrate all of this later")

This is the design and what's built, kept up to date as the work goes on. The gym plan's night shift
(`docs/gym_plan.md` 4.1, 4.2, "Night: the Honey Bee Inn") is the source. Patch `689_hb_shift.py`, data
`_hb_shift.py`.

## Decisions (user)

- **Tifa works the shift.** The player picks her approach and plays her prompts. Cloud isn't on the floor;
  he's the inn's **security**.
- **A few customers, one at a time.** Three a shift, drawn at random from the cast.
- **The inn's own rooms.** It starts from the Honey Bee manager in the lobby (`onna_4`, his menu: "Tifa's
  shift."). The shift plays in a copy of the inn's room (`onna_52`) under a free field name. It isn't
  gated yet.
- **Customers stay dressed.** Even in the explicit endings only Tifa undresses.
- **A spectrum of customers** (user): some timid, some open, others pushy and sometimes aggressive. Tifa
  adapts. Make it funny and experimental, and use Tifa's personality (warm, steady, dry, a bartender who's
  heard everything, a martial artist who doesn't need saving and still likes it when Cloud shows up).
  - **Open** customers who are respectful and say what they want: she generally goes all the way. The visit
    ends in a short explicit scene. Each open customer has his own position: head, cowgirl or mission, the
    movie's poses.
  - **Timid** customers: harder to satisfy. Tifa has to work out what they're really after, guided by their
    hints. Find it and the visit ends in his scene, which is never the obvious one (and isn't explicit).
  - **Pushy / aggressive** customers: they escalate. Cross a line and Tifa either calls **security**
    (Cloud walks in and beats him up, the scene played out) or **handles it herself** (one kick; Cloud arrives
    after it's over). Handled well from the start, a pushy one can come round.

## The visit (one customer)

1. He walks in from the door to his spot. Tifa greets him; his opening lines show his type.
2. **Three rounds.** Each round is:
   - an ASK of Tifa's approach (three options, written per customer), which moves his mood by the option's
     weight (+2 / +1 / 0 / -1 / -2) and plays his reply;
   - then three prompts while she dances (Honey Bee dancer moves retargeted onto her dress). A hit is +1
     mood and a bit of tip; a miss is -1.
3. **Mood** is the `_danger` meter (0-10, starting at his type's value). The left end is the left red: he
   storms out, or the pushy ones turn on her (the incident). The right end is the right red: he's smitten.
4. **The ending**, by type and mood:
   - open, mood >= 7: all the way (her undressed model, his dressed one in the movie's anims for his position,
     a few lines, six prompts);
   - timid, mood >= 7: his found desire's scene;
   - pushy with an incident flag: the incident. Otherwise, with mood >= 7, he comes round;
   - otherwise he leaves (lines by mood).
5. **Tip:** mood x his rate, more for the endings.

The shift ends with a summary, Tifa's line to Cloud, and the pay. Then it's back to the lobby beside the
manager.

## Status

- Built: see `CLAUDE.md` (689 row). **Untested in-game.** Checked on offline renders: the talk spots, the three
  bed / floor positions, the punch, the kick, the falls.
- Cast as built: open Dio (head), Bruno the arm-wrestler (cowgirl), Pete the sailor (mission); timid Private
  Hobbs (wants praise), Gus the mechanic (wants to talk fuel pumps), Professor Nabe (wants to see her kata);
  pushy Spike the punk (aggressive), Corneo's lackey (misses the Don), Mr. Dunmore of Shinra Accounts (wants
  not to be in charge).
- To integrate later (gym plan):
  - before you own the inn only Tifa works, at a cost to her trust (not modelled yet);
  - once you own it, the hired girls work too, each better with some types;
  - the takings become the inn's profits.
