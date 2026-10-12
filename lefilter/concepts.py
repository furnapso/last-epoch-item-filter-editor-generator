"""The Wanted affixes tab's build concepts: what its chips tick.

The affix picker's own groups say where an affix sits, not what a build wants from it: "Offensive ·
Damage Type" holds physical, fire and cold together, "Ailments · Ailments" every ailment in one list.
These concepts regroup the same affixes the way a build is written down - a damage type, how the hit
lands, one ailment at a time, an attribute, a defence, a class - so a physical bleed build can tick
Physical, Bleed, Slow, Frailty and Health Leech without hunting for them.

A concept takes an affix by a phrase in its name or a picker category taken whole (the "Leech"
category, under the Health Leech chip); a class concept takes the class's own affixes - the ones only
it may have. The name is the one the editor shows, not the affix asset's: a few corrupted affixes
carry a completely different asset name (a leftover from how they were extracted), which would put
them in the wrong chips. Which of them a build may use at all - its class, the item types it wears,
the idol kinds it works with - the editor works out from the tabs' settings, and the chips skip what
the build can't carry.
"""
from __future__ import annotations

from dataclasses import dataclass

from .gamedata import AFFIX_CLASS_BITS, AFFIX_NONSPECIFIC, CLASSES
from .leveling import ATTRIBUTES


@dataclass(frozen=True)
class Concept:
    key: str
    label: str                         # the English text: also the key it's translated under
    group: str                         # CONCEPT_GROUPS' key
    phrases: tuple[str, ...] = ()      # lower-case substrings of the affix's own name
    categories: tuple[str, ...] = ()   # affix-picker categories taken whole
    exclude: tuple[str, ...] = ()      # lower-case substrings that disqualify
    only: str = ""                     # a class: only its own affixes ("" = every class's)


CONCEPT_GROUPS = (
    ("damage", "Damage type"),
    ("focus", "Build focus"),
    ("ailment", "Ailments"),
    ("attributes", "Attributes"),
    ("defence", "Defence & utility"),
    ("class", "Class"),
)


def _damage(key: str, label: str, also: tuple[str, ...] = ()) -> Concept:
    words = (key, *also)
    return Concept(key, label, "damage", tuple(f"{w} {s}" for w in words for s in ("damage", "penetration")))


def _focus(key: str, label: str, *phrases: str, exclude: tuple[str, ...] = ()) -> Concept:
    return Concept(key, label, "focus", phrases or (key,), exclude=exclude)


def _ailment(key: str, label: str, phrase: str = "", exclude: tuple[str, ...] = ()) -> Concept:
    return Concept(key, label, "ailment", (phrase or key,), exclude=exclude)


def _attribute(key: str) -> Concept:
    return Concept(key, key.capitalize(), "attributes", (key,))


def _defence(key: str, label: str, phrases: tuple[str, ...] = (), categories: tuple[str, ...] = (),
             exclude: tuple[str, ...] = ()) -> Concept:
    return Concept(key, label, "defence", phrases, categories, exclude)


CONCEPTS = (
    # a damage type: everything that adds or pierces it, however the build lands it
    _damage("physical", "Physical"),
    _damage("fire", "Fire", also=("elemental",)),
    _damage("cold", "Cold", also=("elemental",)),
    _damage("lightning", "Lightning", also=("elemental",)),
    _damage("void", "Void"),
    _damage("necrotic", "Necrotic"),
    _damage("poison", "Poison"),
    Concept("elemental", "Elemental", "damage", ("elemental damage", "elemental penetration")),
    # how the damage lands (the Leveling tab's focus toggles)
    _focus("melee", "Melee", exclude=("minion",)),
    _focus("spell", "Spell / magic", "spell", "cast speed", exclude=("minion",)),
    _focus("throwing", "Throwing", exclude=("minion",)),
    _focus("bow", "Bow", exclude=("minion",)),
    _focus("minion", "Minion"),
    _focus("crit", "Critical strike", "crit", exclude=("avoidance", "reduced bonus damage")),
    _focus("dot", "Damage over time", "damage over time"),
    # one ailment per chip: the stacks a damage-over-time build actually scales with
    _ailment("bleed", "Bleed"),
    _ailment("ignite", "Ignite"),
    _ailment("chill", "Chill"),
    _ailment("freeze", "Freeze", "freez"),
    _ailment("slow", "Slow"),
    _ailment("frailty", "Frailty", "frailt"),
    _ailment("poison_ailment", "Poison", "poison", exclude=("damage", "penetration")),   # its own chip is the damage one
    _ailment("shock", "Shock"),
    _ailment("blind", "Blind"),
    _ailment("stun", "Stun", exclude=("health",)),   # Health and Stun Avoidance is a health affix (see leveling)
    _ailment("shred_armour", "Armor Shred", "shred"),
    _ailment("electrify", "Electrify"),
    *(_attribute(a) for a in ATTRIBUTES),
    Concept("all_attributes", "All Attributes", "attributes", ("all attributes",)),
    # defence and utility: the picker's own categories, which hold the class and idol ones too
    _defence("health", "Health", ("health",), ("Health",)),
    _defence("health_regen", "Health Regeneration", ("regeneration",), ("Health Recovery",)),
    _defence("leech", "Health Leech", ("leech",), ("Leech",)),
    _defence("resistances", "Resistances", ("resistance",), exclude=("minion",)),
    _defence("armour", "Armour", ("armor",), exclude=("minion", "shred")),
    _defence("endurance", "Endurance", ("endurance",), exclude=("minion",)),
    _defence("dodge", "Dodge", ("dodge",), ("Dodge",)),
    _defence("block", "Block", ("block",), ("Block",)),
    _defence("ward", "Ward", ("ward",), ("Ward",)),
    _defence("mana", "Mana", ("mana",), ("Mana",)),
    _defence("movement", "Movement speed", ("movement speed",), ("Movement",)),
    _defence("cooldown", "Cooldown recovery", ("cooldown",), ("Cooldown",)),
    # a class: its own affixes - the picker's category, its idols', and the ones only it may have
    *(Concept(c.lower(), c, "class", only=c) for c in CLASSES),
)


def _matches(c: Concept, a: dict, name: str) -> bool:
    """One affix, one concept: by its lowered name (or its picker category taken whole), or - for a class
    concept - by being that class's own affix, which its class bits say whatever it's called."""
    if c.only:
        bit = AFFIX_CLASS_BITS[c.only]
        return bool(a["class"] & bit) and not (a["class"] & AFFIX_NONSPECIFIC)
    hit = any(p in name for p in c.phrases) or a["category"] in c.categories
    return hit and not any(x in name for x in c.exclude)


def concept_affixes(affixes: list[dict]) -> dict[str, list[dict]]:
    """Concept key -> the affixes it takes, over every affix (the editor filters these by the build)."""
    lowered = [a["name"].lower() for a in affixes]
    return {c.key: [a for a, name in zip(affixes, lowered) if _matches(c, a, name)] for c in CONCEPTS}
