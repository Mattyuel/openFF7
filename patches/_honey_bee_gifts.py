"""Honey Bee gifts: 12 new key items (ids 51-62, unused in the original game:
their names/descriptions are blank in kernel2 sections 15/7, and the exe's
Key Items list walks all 64 bits, 0x714FC1) sold by the Gift Merchant
(625_gift_shops.py) and given to hired girls in the Honey Bee lounges
(620_honey_bee.py). A key item is a single bit (bank 1 byte 64 + id // 8,
bit id % 8), so you hold at most one of each: buy, give, buy again.

Each gift has a hidden type (0 beautiful, 1 practical, 2 sweet; the
description hints at it). Each girl Likes (+2 affection), is Indifferent to
(+1) or Hates (+0) each type (PREFS: one letter per type 0, 1, 2).
Affection 0-9 = her basic visit scene, 10-19 the closer one, 20 the last.
"""

FIRST_KEY_ITEM = 51
TYPES = ("beautiful", "practical", "sweet")
GAIN = {"L": 2, "I": 1, "H": 0}
CLOSE, DEVOTED, MAX = 10, 20, 20

# (shop field, (x, y)): placed with the background drawn (spots on reachable floor)
SHOPS = {
    "wall": ("mrkt2", (-226, 746)),       # Wall Market: left side of the main street, above the item shop
    "costa": ("del2", (478, 1550)),       # Costa del Sol: the square between the bar and the inn
    "cosmo": ("cosmin7", (-822, 10)),     # Cosmo Canyon: the item store, left hut
    "wutai": ("uutai1", (-608, 1466)),    # Wutai: the path by the save point
}

# key item order (id 51 first): (name, description, type, gil, shop)
GIFTS = [
    ("Silk Scarf", "A gift. Fine silk, beautifully dyed", 0, 5000, "wall"),
    ("Sewing Kit", "A gift. Mends any tear, any time", 1, 4000, "wall"),
    ("Chocolate Box", "A gift. Rich chocolates, tied in a bow", 2, 4000, "wall"),
    ("Shell Necklace", "A gift. Pearly shells on a gold chain", 0, 12000, "costa"),
    ("Sun Parasol", "A gift. Shade wherever she goes", 1, 10000, "costa"),
    ("Coconut Liqueur", "A gift. Sweet, creamy and strong", 2, 10000, "costa"),
    ("Feather Charm", "A gift. Bright feathers and beads", 0, 18000, "cosmo"),
    ("Woven Blanket", "A gift. Thick, warm and hand-woven", 1, 15000, "cosmo"),
    ("Cactus Honey", "A gift. Golden honey from the canyon", 2, 15000, "cosmo"),
    ("Jade Hairpin", "A gift. Carved jade, elegant and rare", 0, 30000, "wutai"),
    ("Tea Set", "A gift. Fine Wutai porcelain for tea", 1, 25000, "wutai"),
    ("Plum Mochi", "A gift. Soft, sugared plum sweets", 2, 25000, "wutai"),
]

# girl -> likes per type (beautiful, practical, sweet)
PREFS = {
    "Bambi": "HLI",      # a blanket to sleep under
    "Gloria": "LHI",     # pretty things, not chores
    "Dot": "IHL",        # sweets; tools confuse her
    "Peggy": "ILH",      # things that fix what she breaks; sticky fingers are a hazard
    "Candy": "HIL",      # treats to share with the gossip
    "Rhonda": "HLI",     # useful, not frilly
    "Lulu": "LHI",       # a diva wants sparkle
    "Raven": "LIH",      # dark and beautiful; sugar is too cheerful
    "Elena": "ILL",      # practical (Turk) with a sweet tooth
    "Marisol": "IHL",    # party drinks
    "Ruby": "LHI",       # bling
    "Holly": "ILH",      # warm and useful; sweets are childish
    "Sakura": "LII",     # grace
    "Mags": "HLI",       # tools
    "Celeste": "LHL",    # pretty things and treats; no chores
    "Aurora": "LIH",     # beautiful things like the stars
    "Tifa": "ILI",       # practical: she runs a bar
    "Aerith": "LIL",     # pretty things and sweets
    "Scarlet": "LHH",    # only the finest
    "Velvet": "LHI",     # a star's jewellery
}

# shared lines (the room text table is nearly full: one set for all girls)
GIVE_PROMPT = "Give her a gift?"
NOT_HELD = "You don't have that gift."
REACT = {
    "L": "She lights up and holds it close.\n“For me? You really get me…”\n(Affection +2: {VAR}/20)",
    "I": "She smiles politely.\n“Aw, thanks. That's sweet of you.”\n(Affection +1: {VAR}/20)",
    "H": "Her smile freezes.\n“…Oh. Wow. You shouldn't have.\n No, really.”\n(Affection unchanged: {VAR}/20)",
}
DEVOTED_LINE = "“You don't need gifts anymore,\n silly. I'm all yours.”\n(Affection 20/20)"
