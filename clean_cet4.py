import json

# Load the original file
with open('cet4.json', 'r') as f:
    data = json.load(f)

print(f"Original word count: {len(data)}")

# ============================================================
# Step 1: Remove placeholder entries (待补充 / incomplete)
# ============================================================
to_remove = []
for key, val in data.items():
    if val.get('meaning') == '(待补充)' or val.get('phonetic') == '' or val.get('pos') == '':
        to_remove.append(key)

for key in to_remove:
    del data[key]
print(f"Removed {len(to_remove)} placeholder entries: {to_remove}")
print(f"After removing placeholders: {len(data)}")

# ============================================================
# Step 2: Fix known content errors
# ============================================================

# Fix "schema" - meaning is wrong (it's "scheme" not "schema")
if 'schema' in data:
    old_meaning = data['schema']['meaning']
    data['schema']['meaning'] = '模式；纲要；图解'
    print(f"Fixed 'schema': '{old_meaning}' -> '模式；纲要；图解'")

# Remove "tideous" - misspelling of "tedious" (which already exists)
if 'tideous' in data:
    del data['tideous']
    print(f"Removed 'tideous' (misspelling of 'tedious')")

# Remove "blacks." - has period, not a proper word
if 'blacks.' in data:
    del data['blacks.']
    print(f"Removed 'blacks.' (invalid key with period)")

# Remove "condem" - misspelling of "condemn" (which already exists)
if 'condem' in data:
    del data['condem']
    print(f"Removed 'condem' (misspelling of 'condemn')")

# Remove "yon" - archaic word, not CET-4
if 'yon' in data:
    del data['yon']
    print(f"Removed 'yon' (archaic word)")

# Remove "skulled" - not a standard CET-4 word
if 'skulled' in data:
    del data['skulled']
    print(f"Removed 'skulled' (not a standard word)")

# Remove "incidents" - plural form, should be "incident" if included
if 'incidents' in data:
    del data['incidents']
    print(f"Removed 'incidents' (plural form, not a base word)")

# Fix "former" - meaning incorrectly includes "模型" (which means "model")
if 'former' in data:
    old = data['former']['meaning']
    data['former']['meaning'] = '以前的；前者的'
    data['former']['pos'] = 'adj./n.'
    print(f"Fixed 'former': '{old}' -> '以前的；前者的'")

# Fix "brilliant" - meaning too narrow (just 明亮的)
if 'brilliant' in data:
    old = data['brilliant']['meaning']
    data['brilliant']['meaning'] = '明亮的；才华横溢的；杰出的'
    print(f"Fixed 'brilliant': '{old}' -> '明亮的；才华横溢的；杰出的'")

# Fix "schema" pos - should be just n., not n./v.
if 'schema' in data:
    old_pos = data['schema']['pos']
    data['schema']['pos'] = 'n.'
    print(f"Fixed 'schema' pos: '{old_pos}' -> 'n.'")

# Fix "olympic" -> key should match proper noun
if 'olympic' in data:
    data['olympic']['word'] = 'Olympic'
    print(f"Fixed 'olympic' word field to 'Olympic'")

# Fix "world-wide" -> standard form is "worldwide"
if 'world-wide' in data:
    data['world-wide']['word'] = 'worldwide'
    print(f"Fixed 'world-wide' word field to 'worldwide'")

print(f"After fixing errors: {len(data)}")

# ============================================================
# Step 3: Remove basic primary/junior high school words
# ============================================================
# These are words typically learned in 小学 (primary) and 初中 (junior high)
# that are too basic for a CET-4 word list

basic_words = {
    # === Extremely basic words (小学 level) ===
    # Common everyday objects / basic concepts
    "area", "type", "gas", "dust", "soil", "coal", "tin", "iron", "steel",
    "metal", "silver", "rope", "inch", "cent", "penny", "block", "hole",
    "sort", "stuff", "item", "edge", "path", "mode", "code", "tip", "gap",
    "period", "scene", "depth", "length", "quantity", "heat", "energy",

    # Food / drink
    "cheese", "pork", "ham", "corn", "wine", "nut", "pea", "cream",
    "melon", "peach", "steak", "berry", "brandy", "champagne", "liquor",

    # Animals
    "cow", "pig", "rat", "mouse", "goose", "goat", "cock", "donkey",
    "dove", "insect", "worm", "hawk", "hawk", "goose",

    # Body parts
    "mouth", "lip", "fist", "bone", "thumb", "belly", "elbow", "wrist",
    "throat", "muscle", "tongue", "chin", "jaw", "palm", "ankle", "waist",

    # Household / everyday
    "roof", "ceiling", "shelf", "drawer", "ladder", "mirror", "sheet",
    "pan", "pot", "lid", "tap", "fork", "spoon", "mat", "basin", "oven",
    "fridge", "garage", "cottage", "attic", "collar", "button", "pad",
    "paste", "needle", "nail", "pipe", "tube", "deck", "bench", "chimney",
    "stair", "bush", "fence", "gate", "cage", "wheel", "disk",

    # Nature / geography
    "cave", "shore", "valley", "forest", "bush", "clay", "marsh",
    "lake", "hill", "pond", "stream", "ocean",

    # Directions
    "south", "north", "east", "west", "southeast", "southwest",
    "northeast", "northwest", "southern", "northern",

    # School / education (too basic)
    "chalk", "pupil", "geography", "physics", "laboratory", "campus",
    "medal", "catalogue", "dialogue",

    # Very basic verbs
    "bite", "throw", "boil", "chew", "lick", "swallow", "melt", "freeze",
    "flow", "sail", "sweep", "bend", "fetch", "drown", "cough", "skip",
    "wipe", "sew", "knit", "chop", "hatch", "spill", "drag", "stir",
    "pat", "toss", "haul", "creep", "crawl", "clap", "bang",

    # Very basic adjectives
    "old", "mad", "blind", "neat", "pure", "thick", "bitter", "tight",
    "fond", "cruel", "fair", "wise", "broad", "narrow", "shallow",
    "rough", "dull", "keen", "idle", "bold", "damp", "raw", "ripe",
    "pale", "hollow", "brave", "noble", "vain", "dim", "pale",
    "slippery", "sticky", "dizzy", "messy", "tidy",

    # Very basic prepositions / pronouns / adverbs
    "among", "above", "below", "within", "throughout", "ahead", "aside",
    "somehow", "anyhow", "anyway", "anywhere", "anyone", "anybody",
    "anything", "otherwise", "likewise", "indeed", "hence", "altogether",
    "upward", "upstairs", "downstairs", "further", "moreover",
    "normally", "basically", "naturally", "fortunately", "presently",
    "midday",

    # Very basic nouns
    "scene", "model", "machine", "medicine", "envelope", "telegram",
    "cigarette", "tobacco", "crop", "harvest", "seed", "wheat", "cotton",
    "coal", "petrol", "fuel", "flame", "frost", "dawn", "dusk", "century",
    "era", "castle", "camp", "prison", "church", "hell", "heaven",
    "devil", "ghost", "lord", "god", "soul", "spirit", "funeral",
    "wedding", "party", "treasure", "jewel", "pearl", "bullet", "arrow",
    "sword", "torch", "flag", "tent", "bell", "lamp", "jar", "jug",
    "kettle", "blanket", "towel", "soap", "comb", "brush", "bucket",
    "basket", "bottle", "cigarette", "whistle", "horn", "drum",
    "piano", "violin", "bicycle", "train", "taxi", "truck",
    "photo", "radio", "movie", "phone", "photo", "video",
    "newspaper", "magazine", "calendar", "clock", "watch", "purse",
    "suitcase", "umbrella", "camera", "computer", "television",
    "internet", "database", "software", "hardware", "mouse",
    "keyboard", "screen", "disk", "microphone", "microscope", "microwave",

    # Family / people (too basic)
    "baby", "infant", "child", "parent", "husband", "wife",
    "soldier", "servant", "maid", "tailor", "merchant", "peasant",
    "pilot", "prisoner", "thief", "pirate", "cop", "bully",

    # Colors / shapes
    "pink", "purple", "brown", "gray",

    # Other basic
    "dozen", "cent", "dollar", "wage", "rent", "debt", "tax",
    "passport", "visa", "ticket", "menu", "recipe", "diploma",

    # Very common places
    "kitchen", "bathroom", "bedroom", "balcony", "yard",

    # Measures / basic science
    "inch", "foot", "yard", "mile", "ounce", "pound", "gallon",
    "gram", "kilogram", "liter", "meter", "kilometer",

    # Very common weather
    "cloud", "rain", "snow", "wind", "storm", "fog", "ice",

    # Very basic time
    "day", "week", "month", "year", "hour", "minute", "second",
    "morning", "afternoon", "evening", "night", "today", "tomorrow",
    "yesterday", "noon", "midnight",

    # Very basic colors
    "red", "blue", "green", "yellow", "black", "white",

    # Very basic numbers / math
    "zero", "one", "two", "three", "four", "five", "six", "seven",
    "eight", "nine", "ten", "hundred", "thousand", "million",
    "billion", "first", "second", "third", "fourth",

    # Very basic family
    "mother", "father", "sister", "brother", "uncle", "aunt",
    "grandfather", "grandmother", "cousin", "nephew", "niece",
    "son", "daughter",

    # Very basic common verbs
    "eat", "drink", "sleep", "walk", "run", "sit", "stand",
    "talk", "speak", "say", "tell", "ask", "answer", "call",
    "cry", "laugh", "smile", "shout", "hear", "listen",
    "see", "look", "watch", "feel", "touch", "taste", "smell",
    "think", "know", "understand", "remember", "forget",
    "learn", "teach", "study", "read", "write", "count",
    "draw", "paint", "sing", "dance", "play", "work",
    "rest", "cook", "clean", "wash", "open", "close",
    "push", "pull", "carry", "bring", "take", "give",
    "send", "receive", "buy", "sell", "pay", "cost",
    "begin", "start", "finish", "end", "continue",
    "arrive", "leave", "return", "enter", "cross",
    "follow", "lead", "meet", "visit", "invite",
    "agree", "decide", "choose", "believe", "hope",
    "wish", "want", "need", "like", "love", "hate",
    "prefer", "let", "make", "help",
    "try", "show", "turn", "move", "pass",
    "put", "set", "cut", "hit", "hold",
    "lift", "drop", "pick", "fill", "empty",
    "build", "break", "burn", "change", "check",
    "cover", "divide", "fail", "fit", "fix",
    "grow", "join", "jump", "kick", "kill",
    "lock", "mark", "mix", "name", "nod",
    "note", "own", "park", "permit", "phone",
    "plan", "please", "practise", "promise", "pronounce",
    "protect", "punish", "raise", "reach", "repair",
    "repeat", "report", "require", "ring", "roll",
    "save", "search", "share", "shoot", "sign",
    "stick", "suffer", "suggest", "supply", "support",
    "surprise", "test", "tie", "touch", "translate",
    "travel", "treat", "trust", "weigh", "wonder",

    # Very common
    "banana", "apple", "orange", "rice", "bread", "egg",
    "milk", "water", "coffee", "tea", "sugar", "salt",
    "butter", "oil", "fish", "meat", "chicken", "beef",
    "cake", "soup", "salad", "sandwich", "cookie", "candy",
    "juice", "beer", "soda",

    # Body parts (basic)
    "head", "hair", "face", "eye", "ear", "nose", "cheek",
    "neck", "shoulder", "arm", "hand", "finger", "chest",
    "back", "stomach", "leg", "knee", "foot", "toe", "skin",

    # Very basic clothes
    "coat", "jacket", "shirt", "dress", "skirt", "pants",
    "shoe", "sock", "hat", "cap", "glove", "scarf", "belt",
    "pocket", "boot", "jeans",

    # Very basic furniture
    "chair", "table", "bed", "desk", "sofa", "cupboard",
    "curtain", "carpet", "pillow",

    # Very basic buildings
    "house", "room", "door", "window", "wall", "floor",
    "garden", "pool", "bridge", "tower",

    # Very basic transport
    "car", "bus", "plane", "boat", "ship", "bike",
    "road", "street", "map", "station", "airport",

    # School (basic)
    "school", "class", "teacher", "student", "book",
    "pen", "pencil", "paper", "bag", "ruler", "eraser",

    # Very basic nature
    "tree", "flower", "grass", "leaf", "river",
    "mountain", "sky", "star", "moon", "sun",

    # MONEY/numbers
    "money", "coin", "cash", "price",

    # Colors
    "orange", "color",
}

# Additional basic words found in CET4.json that I can see from the list
# These are definitely below CET-4 level
additional_basic = {
    # From the last-10-keys and other basic entries
    "go", "so", "as", "off", "old", "sure", "well", "stop",
    "video", "color", "coming", "seen", "fourth", "joke", "site",
    "pole", "golf", "hunt", "nit", "awe", "berry", "disc", "facing",
    "disc", "vein",

    # More basic words from the full list
    "pack", "row", "tap", "ski", "tire", "saw", "cell", "hall",
    "flight", "chain", "slip", "league", "fetch", "edit", "route",
    "fever", "lid", "tube", "zone", "loop", "yawn", "lane", "cop",
    "mat", "bang", "rag", "oven", "rat", "oral", "buddy", "bunch",
    "pad", "tow", "jar", "cue", "dose", "wagon", "web", "axe",
    "gym", "pub", "vet", "van", "yell", "tag", "rib", "rim",
    "rod", "sack", "hut", "peg", "stool", "tray", "dome", "moss",
    "cliff", "crane", "herd", "flock", "hawk", "moth", "owl",
    "trout", "salmon", "crab", "shrimp", "squid", "whale",
    "seal", "dove", "goose", "crow", "sparrow", "pigeon",

    # Plants / fruits
    "oak", "pine", "bamboo", "olive", "mushroom", "onion",
    "carrot", "potato", "tomato", "cabbage", "pea", "bean",
    "grape", "lemon", "cherry",

    # Tools / household
    "hammer", "saw", "drill", "screw", "bolt", "nut", "hook",
    "shelf", "rack", "cord", "wire", "plug", "socket",

    # Money / business (basic)
    "sale", "shop", "store", "market", "mall", "brand",
    "bill", "cheque", "fare", "rent",

    # Very common adjectives
    "quiet", "loud", "fast", "slow", "heavy", "light",
    "hard", "soft", "easy", "difficult", "simple",
    "safe", "dangerous", "fresh", "stale", "full",
    "empty", "big", "small", "tall", "short", "long",
    "high", "low", "rich", "poor", "young", "elderly",
    "happy", "sad", "angry", "glad", "sorry", "afraid",
    "lucky", "hungry", "thirsty", "sick", "healthy",
    "stupid", "clever", "honest", "lazy", "busy",
    "free", "single", "married", "correct", "wrong",
    "interesting", "boring", "beautiful", "ugly",
    "modern", "ancient", "square", "round",

    # Common verbs
    "become", "spend", "stay", "keep", "lose", "win",
    "turn", "appear", "disappear", "happen", "seem",
    "remain", "rise", "fall", "add", "reduce", "double",
    "prepare", "explain", "describe", "compare", "connect",
    "collect", "connect", "consider", "control", "copy",
    "deliver", "demand", "depend", "design", "develop",
    "discover", "discuss", "encourage", "examine",
    "expect", "experience", "explain", "express",
    "imagine", "improve", "include", "introduce",
    "judge", "manage", "notice", "offer", "order",
    "organize", "perform", "practise", "prefer",
    "produce", "provide", "realize", "record",
    "relax", "respect", "result", "review", "rule",
    "seem", "serve", "settle", "smoke", "spread",
    "state", "succeed", "sudden", "suffer",
    "waste", "wonder", "worry",
}

basic_words.update(additional_basic)

# Count before removal
before_count = len(data)

# Build a final set that also checks common basic word patterns
# Remove the basic words
removed_basic = []
for key in list(data.keys()):
    if key.lower() in basic_words:
        removed_basic.append(key)
        del data[key]

print(f"Removed {len(removed_basic)} basic primary/junior high words")
print(f"Words after filtering: {len(data)}")

# ============================================================
# Step 4: Sort and write the cleaned file
# ============================================================
# Sort alphabetically by key
sorted_data = dict(sorted(data.items()))

with open('cet4_cleaned.json', 'w', encoding='utf-8') as f:
    json.dump(sorted_data, f, ensure_ascii=False, indent=2)

print(f"\nFinal word count: {len(sorted_data)}")
print(f"Original: {before_count + len(to_remove)} -> Cleaned: {len(sorted_data)}")
print(f"Total removed: {before_count + len(to_remove) - len(sorted_data)}")
print(f"\nCleaned file saved to: cet4_cleaned.json")
