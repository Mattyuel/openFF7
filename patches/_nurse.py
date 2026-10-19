"""(user) Hello nurse (679_nurse): a scene in Mideel's clinic (ithos, copied). Cloud is the patient in the
front bed; over and over the doctor sends one of the nurses ("Nurse <name>, go check on the patient."), she
walks over and stops at the foot of his bed, says her piece, a fade, and the two of them on the bed in one of
her own positions (`_nurse_poses`) for `TURN` frames (20 s, user); then she's back at her spot. Now and then a
break: the nurses discuss the patient with each other or with the doctor. Square asks to check out (leave).
Data only."""

FIELD = "subin_4"             # (the classic group set: no longer entered since the loose shoot, 678)
BASE = "ithos"
TURN = 600                    # (user) 20 seconds a position
FAST_AT = 300                 # the faster pace from halfway
MUSIC = 67                    # BEE (naughty)
CUT_CHANCE = 96               # a break after a round: 96 in 256
ROUND_PRESSES = 12            # the cameraman pays MOVIE_PRESSES = rounds x this (x the group's rate)

# the cast (each her own clothed copy of the island nurse; one undressed copy plays them all)
NURSES = ["Amy", "Bella", "Clara", "Daisy", "Eve", "Faye"]

# positions (`_nurse_poses`): girl / Cloud anim letters, Cloud's spot on the bed
POSITIONS = [
    dict(key="checkup", girl="A", cloud="Y"),
    dict(key="arched", girl="B", cloud="B"),
    dict(key="spoon", girl="C", cloud="Z"),
    dict(key="stacked", girl="D", cloud="B"),
    dict(key="saddle", girl="E", cloud="B"),
]

INTRO = [
    "Doctor\n“Ah, the patient's awake. Mako poisoning,\n severe. He'll need round-the-clock care.”",
    "Doctor\n“My nurses are the best on the island.\n ...Very hands-on.”",
]
SEND = "Doctor\n“Nurse {name}, go check on the patient.”"
GREET = {   # (two each, one at random) at the foot of his bed
    "Amy": ["Nurse Amy\n“Time for your check-up, mister.\n Don't be shy.”",
            "Nurse Amy\n“Ooh, your pulse is racing.\n Let me take a closer look.”"],
    "Bella": ["Nurse Bella\n“Doctor's orders! Lie back and say 'ahh'.”",
              "Nurse Bella\n“Again? You're my favourite patient.”"],
    "Clara": ["Nurse Clara\n“...Hm. Temperature's rising.\n I have a cure for that.”",
              "Nurse Clara\n“Stay still. This is a very thorough\n examination.”"],
    "Daisy": ["Nurse Daisy\n“Hiii! Sponge bath time!\n ...I forgot the sponge. Oops.”",
              "Nurse Daisy\n“Feeling better? Let's make sure!”"],
    "Eve": ["Nurse Eve\n“I hear you've been a bad patient.”",
            "Nurse Eve\n“Bedside manner is my specialty.”"],
    "Faye": ["Nurse Faye\n“Shh. Doctor thinks I'm changing\n your sheets.”",
             "Nurse Faye\n“Open wide... oh, wait. That's my line.”"],
}
TALK = {    # her lines in each position ({name} = hers), two shown in each turn
    "checkup": ["“Mmh... everything looks... healthy.”", "“Hold still, I'm not finished.”"],
    "arched": ["“Ahh! Doctor said... gentle exercise...”", "“Look at me, patient. Eyes up here.”"],
    "spoon": ["“Mm... body heat is... very therapeutic.”", "“Don't tell the doctor... ahh!”"],
    "stacked": ["“I'm your... human blanket. Ahh!”", "“Your heart's... pounding through my back!”"],
    "saddle": ["“Reflexes... ahh... excellent!”", "“Hold on to me... I mean, I'll hold on!”"],
}
AFTER = "(She straightens her cap and slips back to her post.)"

LEAVE_ASK = "Doctor\n“Feeling well enough to check out?”"
LEAVE = ["Check out.", "Stay in bed."]
LEAVE_LINE = "Doctor\n“Come back any time. My nurses\n will miss you. ...A lot.”"

# breaks: who gathers by the doctor (nurse names / "doctor"), and the talk
CUTS = [
    dict(who=["Amy", "Bella"],
         talk="Nurse Amy\n“Have you SEEN the patient in bed two?”{NEW}"
              "Nurse Bella\n“Seen him? I've... examined him.”{NEW}"
              "Nurse Amy\n“Thoroughly?”{NEW}"
              "Nurse Bella\n“Twice.”"),
    dict(who=["doctor", "Clara"],
         talk="Doctor\n“Nurse Clara, his chart says 'vitals:\n excellent' fourteen times.”{NEW}"
              "Nurse Clara\n“He's very... vital, doctor.”{NEW}"
              "Doctor\n“...Carry on.”"),
    dict(who=["Daisy", "Eve", "Faye"],
         talk="Nurse Daisy\n“I call dibs on the next check-up!”{NEW}"
              "Nurse Eve\n“You can't call dibs on a patient.”{NEW}"
              "Nurse Faye\n“...Dibs after Daisy.”{NEW}"
              "Nurse Eve\n“...Fine. Dibs after Faye.”"),
    dict(who=["doctor", "Amy", "Eve"],
         talk="Doctor\n“Ladies, the mako poisoning seems to\n be... improving rapidly.”{NEW}"
              "Nurse Eve\n“It's the treatment, doctor.”{NEW}"
              "Nurse Amy\n“Very intensive treatment.”{NEW}"
              "Doctor\n“...I don't want to know.”"),
    dict(who=["Bella", "Clara"],
         talk="Nurse Bella\n“He moans in his sleep. Something about\n a 'promise' and a 'water tower'.”{NEW}"
              "Nurse Clara\n“Poor thing. ...Want to go cheer him up?”{NEW}"
              "Nurse Bella\n“I thought you'd never ask.”"),
    dict(who=["doctor", "Faye"],
         talk="Nurse Faye\n“Doctor, I think the patient needs\n more bed rest.”{NEW}"
              "Doctor\n“He's been in bed for a week.”{NEW}"
              "Nurse Faye\n“...More bed. Less rest.”"),
    dict(who=["Daisy", "Amy"],
         talk="Nurse Daisy\n“Is it true SOLDIERs have more\n stamina?”{NEW}"
              "Nurse Amy\n“Ex-SOLDIER. And... yes. Very much yes.”{NEW}"
              "Nurse Daisy\n“I'm putting in for a double shift.”"),
    dict(who=["doctor", "Bella", "Daisy", "Faye"],
         talk="Doctor\n“Who used every towel in the clinic?”{NEW}"
              "(Three nurses look at the ceiling.){NEW}"
              "Nurse Daisy\n“...The patient spilled something.”{NEW}"
              "Doctor\n“Several times, apparently.”"),
    dict(who=["Clara", "Eve"],
         talk="Nurse Clara\n“Shift report: patient stable,\n nurses exhausted.”{NEW}"
              "Nurse Eve\n“Recommend: continued treatment.”{NEW}"
              "Nurse Clara\n“Seconded.”"),
    dict(who=["doctor", "Amy", "Bella", "Clara"],
         talk="Doctor\n“A friend of the patient called. A young\n woman. Tifa, I believe.”{NEW}"
              "Nurse Amy\n“...”{NEW}Nurse Bella\n“...”{NEW}"
              "Nurse Clara\n“Tell her he's resting.”"),
]
