"""Loot-filter enums and lookups, as defined in the game code (LE.dll, lootFilterVersion 9).

Values come from the IL2CPP metadata (Cpp2IL); the XML stores enums by name, flag
enums as space-separated names ("UNIQUE SET").
"""
from __future__ import annotations

import re

# EquipmentType: the base type id (MasterItemsList baseTypeID) is the enum value.
EQUIPMENT_TYPES = {
    0: "HELMET", 1: "BODY_ARMOR", 2: "BELT", 3: "BOOTS", 4: "GLOVES",
    5: "ONE_HANDED_AXE", 6: "ONE_HANDED_DAGGER", 7: "ONE_HANDED_MACES", 8: "ONE_HANDED_SCEPTRE",
    9: "ONE_HANDED_SWORD", 10: "WAND", 11: "ONE_HANDED_FIST", 12: "TWO_HANDED_AXE", 13: "TWO_HANDED_MACE",
    14: "TWO_HANDED_SPEAR", 15: "TWO_HANDED_STAFF", 16: "TWO_HANDED_SWORD", 17: "QUIVER", 18: "SHIELD",
    19: "CATALYST", 20: "AMULET", 21: "RING", 22: "RELIC", 23: "BOW", 24: "CROSSBOW",
    25: "IDOL_1x1_ETERRA", 26: "IDOL_1x1_LAGON", 27: "IDOL_2x1", 28: "IDOL_1x2", 29: "IDOL_3x1",
    30: "IDOL_1x3", 31: "IDOL_4x1", 32: "IDOL_1x4", 33: "IDOL_2x2", 34: "BLESSING", 35: "GREATER_LENS",
    36: "ARCTUS_LENS", 37: "MESEMBRIA_LENS", 38: "EOS_LENS", 39: "DYSIS_LENS", 40: "UNUSED", 41: "IDOL_ALTAR",
}
TYPE_IDS = {name: tid for tid, name in EQUIPMENT_TYPES.items()}

WEAPON_TYPES = ("ONE_HANDED_AXE", "ONE_HANDED_DAGGER", "ONE_HANDED_MACES", "ONE_HANDED_SCEPTRE", "ONE_HANDED_SWORD",
                "WAND", "TWO_HANDED_AXE", "TWO_HANDED_MACE", "TWO_HANDED_SPEAR", "TWO_HANDED_STAFF",
                "TWO_HANDED_SWORD", "BOW")
OFFHAND_TYPES = ("SHIELD", "QUIVER", "CATALYST")
ARMOUR_TYPES = ("HELMET", "BODY_ARMOR", "BELT", "BOOTS", "GLOVES")
JEWELRY_TYPES = ("AMULET", "RING", "RELIC")
# Idols: the all-class ones (1x1, 2x1, 1x2) and the class-specific ones (one base per class).
COMMON_IDOL_TYPES = ("IDOL_1x1_ETERRA", "IDOL_1x1_LAGON", "IDOL_2x1", "IDOL_1x2")
CLASS_IDOL_TYPES = ("IDOL_3x1", "IDOL_1x3", "IDOL_4x1", "IDOL_1x4", "IDOL_2x2")
# ItemList.IsWeaverIdol: the Weaver version of each all-class idol (larger pool: + Weaver Idol affixes).
WEAVER_IDOL_SUBTYPES = {"IDOL_1x1_ETERRA": 2, "IDOL_1x1_LAGON": 1, "IDOL_2x1": 1, "IDOL_1x2": 1}
# ItemData.IsOmenIdolAffix: Omen idols also roll the affixes of these (larger) idol types.
OMEN_EXTRA_TYPES = ("IDOL_4x1", "IDOL_1x4", "IDOL_2x2")

# Flag enums, in declaration order (the order the game's XmlSerializer writes them).
RARITIES = ("NORMAL", "MAGIC", "RARE", "UNIQUE", "SET", "LEGENDARY", "EXALTED")      # RarityCondition.Rarity
CLASSES = ("Primalist", "Mage", "Sentinel", "Acolyte", "Rogue")                     # ItemList.ClassRequirement
CLASS_BITS = {c: 1 << i for i, c in enumerate(CLASSES)}
# Filter icons (LootFilterSettingsPanelUI.icons in PermaLoad.bundle): 0 none, then the class icons.
CLASS_FILTER_ICONS = {"Acolyte": 1, "Mage": 2, "Primalist": 3, "Rogue": 4, "Sentinel": 5}
# Affixes use AffixList.ClassSpecificity instead: the same classes one bit up, plus NonSpecific
# (may roll on items that aren't class-specific). 0 = no restriction.
AFFIX_NONSPECIFIC = 1
AFFIX_CLASS_BITS = {c: bit << 1 for c, bit in CLASS_BITS.items()}
# A class's own skills: the game's "Level of <skill>" affix gives each of them one, and the
# Descriptors table gives the skill itself a key of its own - which is where the Wanted affixes
# tab's skill chips get their name in every language (lefilter/i18n.py UI_GAME_TERMS). Affixes
# name a skill in their own text too ("Physical Penetration with Puncture"), which is what the
# chips group them by; SKILL_ALIASES carries the ones an affix words differently.
SKILLS: dict[str, tuple[tuple[str, str], ...]] = {
    "Primalist": (
        ("Avalanche", "88,209,1,2"),
        ("Earthquake", "88,339,1,2"),
        ("Entangling Roots", "88,71,1,2"),
        ("Eterra's Blessing", "88,194,1,2"),
        ("Fury Leap", "88,17,1,2"),
        ("Gathering Storm", "88,757,1,2"),
        ("Maelstrom", "88,318,1,2"),
        ("Serpent Strike", "88,61,1,2"),
        ("Spriggan Form", "88,223,1,2"),
        ("Summon Bear", "88,56,1,2"),
        ("Summon Frenzy Totem", "88,282,1,2"),
        ("Summon Raptor", "88,321,1,2"),
        ("Summon Sabertooth", "88,167,1,2"),
        ("Summon Scorpion", "88,235,1,2"),
        ("Summon Spriggan", "88,75,1,2"),
        ("Summon Storm Crows", "88,510,1,2"),
        ("Summon Storm Totem", "88,195,1,2"),
        ("Summon Thorn Totem", "88,58,1,2"),
        ("Summon Tide Elemental", "88,923,1,0,2"),
        ("Summon Wolf", "88,8,1,2"),
        ("Swarmblade Form", "88,553,1,2"),
        ("Swipe", "88,19,1,2"),
        ("Tempest Strike", "88,270,1,2"),
        ("Tornado", "88,22,1,2"),
        ("Upheaval", "88,550,1,2"),
        ("Warcry", "88,505,1,2"),
        ("Werebear Form", "88,215,1,2"),
    ),
    "Mage": (
        ("Arcane Ascendance", "88,350,1,2"),
        ("Black Hole", "88,15,1,2"),
        ("Disintegrate", "88,314,1,2"),
        ("Elemental Nova", "88,12,1,2"),
        ("Enchant Weapon", "88,201,1,2"),
        ("Fireball", "88,1,1,2"),
        ("Firebrand", "88,428,1,2"),
        ("Flame Reave", "88,156,1,2"),
        ("Flame Rush", "88,696,1,2"),
        ("Flame Ward", "88,336,1,2"),
        ("Focus", "88,175,1,2"),
        ("Frost Claw", "88,708,1,2"),
        ("Frost Wall", "88,703,1,2"),
        ("Glacier", "88,47,1,2"),
        ("Glyph of Dominion", "88,694,1,2"),
        ("Ice Barrage", "88,246,1,2"),
        ("Lightning Blast", "88,39,1,2"),
        ("Mana Strike", "88,29,1,2"),
        ("Meteor", "88,7,1,2"),
        ("Runebolt", "88,691,1,2"),
        ("Runic Invocation", "88,689,1,2"),
        ("Shatter Strike", "88,199,1,2"),
        ("Snap Freeze", "88,166,1,2"),
        ("Static", "88,294,1,2"),
        ("Static Orb", "88,65,1,2"),
        ("Surge", "88,504,1,2"),
        ("Teleport", "88,179,1,2"),
        ("Volcanic Orb", "88,78,1,2"),
    ),
    "Sentinel": (
        ("Abyssal Echoes", "88,118,1,2"),
        ("Anomaly", "88,74,1,2"),
        ("Devouring Orb", "88,88,1,2"),
        ("Erasing Strike", "88,114,1,2"),
        ("Forge Strike", "88,218,1,2"),
        ("Hammer Throw", "88,106,1,2"),
        ("Healing Hands", "88,200,1,2"),
        ("Holy Aura", "88,187,1,2"),
        ("Javelin", "88,536,1,2"),
        ("Judgement", "88,197,1,2"),
        ("Lunge", "88,154,1,2"),
        ("Manifest Armor", "88,219,1,2"),
        ("Multistrike", "88,533,1,2"),
        ("Radiant Lance", "88,924,1,0,2"),
        ("Rebuke", "88,173,1,2"),
        ("Ring Of Shields", "88,172,1,2"),
        ("Rive", "88,91,1,2"),
        ("Shield Bash", "88,403,1,2"),
        ("Shield Rush", "88,101,1,2"),
        ("Shield Throw", "88,267,1,2"),
        ("Smelter's Wrath", "88,354,1,2"),
        ("Smite", "88,216,1,2"),
        ("Symbols of Hope", "88,186,1,2"),
        ("Vengeance", "88,107,1,2"),
        ("Void Cleave", "88,402,1,2"),
        ("Volatile Reversal", "88,100,1,2"),
        ("Warpath", "88,97,1,2"),
    ),
    "Acolyte": (
        ("Assemble Abomination", "88,372,1,2"),
        ("Aura Of Decay", "88,256,1,2"),
        ("Bone Curse", "88,369,1,2"),
        ("Chaos Bolts", "88,715,1,2"),
        ("Chthonic Fissure", "88,722,1,2"),
        ("Death Seal", "88,394,1,2"),
        ("Drain Life", "88,373,1,2"),
        ("Dread Shade", "88,411,1,2"),
        ("Flay", "88,815,1,2"),
        ("Ghostflame", "88,718,1,2"),
        ("Harvest", "88,185,1,2"),
        ("Hungering Souls", "88,153,1,2"),
        ("Infernal Shade", "88,370,1,2"),
        ("Marrow Shards", "88,143,1,2"),
        ("Profane Veil", "88,721,1,2"),
        ("Reaper Form", "88,232,1,2"),
        ("Rip Blood", "88,137,1,2"),
        ("Sacrifice", "88,140,1,2"),
        ("Soul Feast", "88,261,1,2"),
        ("Spirit Plague", "88,371,1,2"),
        ("Summon Bone Golem", "88,157,1,2"),
        ("Summon Skeletal Mage", "88,291,1,2"),
        ("Summon Skeleton", "88,120,1,2"),
        ("Summon Volatile Zombie", "88,408,1,2"),
        ("Summon Wraith", "88,146,1,2"),
        ("Transplant", "88,253,1,2"),
        ("Wandering Spirits", "88,152,1,2"),
    ),
    "Rogue": (
        ("Acid Flask", "88,50,1,2"),
        ("Aerial Assault", "88,731,1,2"),
        ("Ballista", "88,379,1,2"),
        ("Bladestorm", "88,879,1,0,2"),
        ("Cinder Strike", "88,481,1,2"),
        ("Dancing Strikes", "88,450,1,2"),
        ("Dark Quiver", "88,405,1,2"),
        ("Decoy", "88,445,1,2"),
        ("Detonating Arrow", "88,341,1,2"),
        ("Dive Bomb", "88,733,1,2"),
        ("Dreamslash", "88,922,1,0,2"),
        ("Explosive Trap", "88,734,1,2"),
        ("Falconry", "88,727,1,2"),
        ("Flurry", "88,224,1,2"),
        ("Hail of Arrows", "88,479,1,2"),
        ("Heartseeker", "88,807,1,2"),
        ("Lethal Mirage", "88,468,1,2"),
        ("Multishot", "88,377,1,2"),
        ("Net", "88,735,1,2"),
        ("Puncture", "88,440,1,2"),
        ("Shadow Cascade", "88,214,1,2"),
        ("Shadow Rend", "88,881,1,0,2"),
        ("Shift", "88,340,1,2"),
        ("Shurikens", "88,263,1,2"),
        ("Smoke Bomb", "88,473,1,2"),
        ("Synchronized Strike", "88,478,1,2"),
        ("Umbral Blades", "88,562,1,2"),
    ),
}

# The spellings an affix gives a skill the game words differently ("Level of Frostwall" for the
# game's Frost Wall): matched as whole words, like every other skill name.
SKILL_ALIASES: dict[str, tuple[str, ...]] = {
    "Frost Wall": ("Frostwall",),
    "Summon Storm Crows": ("Summon Storm Crow", "Storm Crows"),
    "Synchronized Strike": ("Synchronised Strike",),
}
FACTIONS = ("CircleOfFortune", "MerchantsGuild", "ForgottenKnights", "TheWeaver")   # FactionID
# The faction condition's dropdown only offers the two trade factions (FactionCondition.GetFactionDropdownOptions).
FILTER_FACTIONS = ("CircleOfFortune", "MerchantsGuild")
FACTION_LABELS = {"CircleOfFortune": "Circle of Fortune", "MerchantsGuild": "Merchant's Guild",
                  "ForgottenKnights": "Forgotten Knights", "TheWeaver": "The Weaver"}
CORRUPTION = ("Any", "OnlyCorrupted", "OnlyUncorrupted")
COMPARSION = ("ANY", "EQUAL", "LESS", "LESS_OR_EQUAL", "MORE", "MORE_OR_EQUAL")    # sic, the game's spelling
BEAM_SIZES = ("NONE", "LARGEST", "VERYLARGE", "LARGE", "MEDIUM", "SMALL", "VERYSMALL", "SMALLEST")
SEALED_TYPES = ("Any", "NotSealed", "Sealed", "SealedPrefix", "SealedSuffix")       # AffixCountCondition
LEVEL_CONDITION_TYPES = ("BELOW_LEVEL", "ABOVE_LEVEL", "MAX_LVL_BELOW_CHARACTER_LEVEL", "HIGHEST_USABLE_LEVEL")

NON_EQUIPMENT_FLAGS = (
    "CommonShards", "CommonRunes", "CommonGlyphs", "RareShards", "RareRunes", "RareGlyphs",
    *(f"WovenEchoesRank{i}" for i in range(1, 11)), "WovenEchoesUnpurchasable", "GoldResonance",
    "ObsidianResonance", "ArenaKeys", "DungeonKeys", "DungeonCharms", "LizardTails", "HarbingerEye",
    "PrimordialMaterials", "TemporalKeystone", "MerchantToken", "ArenaKeysOfMemory", "CrystallizedHeart",
    "AllKeys", "AllWovenEchoes", "AllResonances", "AllShards", "AllRunes", "AllGlyphs", "AllCommon", "AllRare",
    "AllCrafting", "All",
)
GLYPH_FLAGS = ("GlyphOfHope", "GlyphOfStability", "GlyphOfOrder", "GlyphOfDespair", "GlyphOfEnvy", "AllGlyphs")
RUNE_FLAGS = ("RuneOfShattering", "RuneOfRefinement", "RuneOfRemoval", "RuneOfDiscovery", "RuneOfShaping",
              "RuneOfAscendance", "RuneOfCreation", "RuneOfWeaving", "RuneOfHavoc", "RuneOfRedemption",
              "RuneOfEvolution", "RuneOfCorruption", "AllRunes")

# Conditions on non-equipment items: condition type -> (flags element, known flag names).
FLAG_CONDITIONS = {
    "KeysCondition": ("NonEquippableItemFilterFlags", NON_EQUIPMENT_FLAGS),
    "CraftingMaterialsCondition": ("NonEquippableItemFilterFlags", NON_EQUIPMENT_FLAGS),
    "ResonancesCondition": ("NonEquippableItemFilterFlags", NON_EQUIPMENT_FLAGS),
    "WovenEchoesCondition": ("NonEquippableItemFilterFlags", NON_EQUIPMENT_FLAGS),
    "GlyphCondition": ("GlyphFilterFlags", GLYPH_FLAGS),
    "RuneCondition": ("RuneFilterFlags", RUNE_FLAGS),
}

# Affix specialAffixType values (MasterAffixesList).
AFFIX_SPECIAL = {0: "", 1: "experimental", 2: "personal", 3: "set", 4: "enchanted idol", 5: "weaver idol",
                 6: "corrupted", 7: "variant"}

# EpochColor.ColorID entries used as the default label colour of each rarity.
RARITY_COLOR_IDS = {"NORMAL": 0, "MAGIC": 1, "RARE": 2, "UNIQUE": 3, "SET": 4, "LEGENDARY": 5, "EXALTED": 11}


def flags_to_xml(names: list[str], order: tuple[str, ...], none: str = "None", everything: str | None = None) -> str:
    """Selected flag names -> the XML text the game writes (declaration order, space-separated)."""
    chosen = [n for n in order if n in set(names)]
    if not chosen:
        return none
    if everything and len(chosen) == len([n for n in order if n != everything]):
        return everything
    return " ".join(chosen)


def class_names(bits: int) -> list[str]:
    return [c for c in CLASSES if bits & CLASS_BITS[c]]


# --- filter file version ---------------------------------------------------------------------------------
# What the game's upgrade of an older filter works on (ItemFilterManager.UpdateFilter renames old tags,
# ItemFilter.Sanitize turns levelDependent into a level condition and BeamId into the beam fields).
OLD_FILTER_LAYOUT = re.compile(r"TWO_HANDED_POLEARM|<type>HIGHLIGHT</type>|<(?:levelDependent|minLvl|maxLvl)>"
                               r"|<levelDependent_deprecated>true<|<BeamId>")


def check_filter_version(version: int | None, text: str, current: int, where: str = "") -> None:
    """Refuses a filter this tool can't read as lootFilterVersion `current`. The game writes 0 into the filters it
    creates (it upgrades them when it next loads one, which would clear their map icons and beam overrides), so
    0 in the current layout counts as current - saving writes `current`, so the game leaves it as it is."""
    if version == current or (version == 0 and not OLD_FILTER_LAYOUT.search(text)):
        return
    raise ValueError(f"{where}lootFilterVersion {version}, expected {current} - open and save it in the current game version first")
