"""The Wanted affixes tab's build concepts: what its chips tick.

The affix picker's own groups say where an affix sits, not what a build wants from it: "Offensive ·
Damage Type" holds physical, fire and cold together, "Ailments · Ailments" every ailment in one list.
These concepts regroup the same affixes the way a build is written down - a damage type, how the hit
lands, one ailment at a time, an attribute, a defence, a class - so a physical bleed build can tick
Physical, Bleed, Slow, Frailty and Health Leech without hunting for them.

A concept takes an affix by a phrase in its name or a picker category taken whole (the "Leech"
category, under the Health Leech chip); a class concept takes the class's own affixes - the ones only
it may have; a skill concept the affixes naming that skill as a whole word ("Net" is a Rogue skill,
not a Network affix). Skills are the class's own, from the game's "Level of <skill>" affixes, so the
Skills row holds the ones of the class the build plays: tick Puncture there and the Rogue chip keeps
the affixes no skill names but drops the other skills'.

An affix that only works under some condition is a chip of its own kind as well: what it wields
("Increased Damage while wielding a Dagger"), what happens for it to count ("Health Gained on Block",
"Increased Damage per active Shadow"), and the buffs a build keeps up (Frenzy, Haste). The ailment
row also has the ailments the picker lumps into the class lists - Frostbite, Time Rot, Damned, Fear -
so a cold build can tick Frostbite without ticking Mage. The name is the one the editor shows, not the
affix asset's: a few corrupted affixes carry a completely different asset name (a leftover from how
they were extracted), which would put them in the wrong chips. Which of them a build may use at all -
its class, the item types it wears, the idol kinds it works with - the editor works out from the
tabs' settings, and the chips skip what the build can't carry.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from functools import lru_cache

from .gamedata import AFFIX_CLASS_BITS, AFFIX_NONSPECIFIC, CLASSES, SKILL_ALIASES, SKILLS
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
    whole: bool = False                # phrases are whole words, not substrings (a skill's "Net" is no "Network")


CONCEPT_GROUPS = (
    ("damage", "Damage type"),
    ("focus", "Build focus"),
    ("ailment", "Ailments"),
    ("buffs", "Buffs"),
    ("attributes", "Attributes"),
    ("defence", "Defence & utility"),
    ("conditions", "Conditions"),
    ("class", "Class"),
    ("skills", "Skills"),
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


def _buff(key: str, label: str, phrase: str = "", exclude: tuple[str, ...] = ()) -> Concept:
    """A buff a build keeps up: the picker files these under the classes, not under ailments."""
    return Concept(key, label, "buffs", (phrase or key,), exclude=exclude)


def _condition(key: str, label: str, *phrases: str, whole: bool = False) -> Concept:
    """An affix that only counts under a condition: what happens for it to (Health Gained on Block),
    or what has to be true of the build first (Increased Damage per active Shadow)."""
    return Concept(key, label, "conditions", phrases, whole=whole)


@lru_cache(maxsize=None)
def _word(phrase: str) -> re.Pattern[str]:
    """A skill's name as a whole word: "Net" is a Rogue skill, not a Network affix."""
    return re.compile(rf"(?<!\w){re.escape(phrase)}(?!\w)")


def _skill_concepts() -> tuple[Concept, ...]:
    """One chip per class skill, taking the affixes that name it as a whole word (with the spellings
    an affix gives it), and leaving the ones naming a longer skill to it - "Static" skips Static Orb's."""
    def slug(name: str) -> str:
        return re.sub(r"\W+", "_", name.lower()).strip("_")
    out = []
    for cls in CLASSES:
        longer = {name: tuple(o.lower() for o, _ in SKILLS[cls] if o != name and _word(name.lower()).search(o.lower()))
                  for name, _ in SKILLS[cls]}
        out += [Concept(f"skill_{cls.lower()}_{slug(name)}", name, "skills",
                        (name.lower(), *(a.lower() for a in SKILL_ALIASES.get(name, ()))),
                        exclude=longer[name], whole=True)
                for name, _ in SKILLS[cls]]
    return tuple(out)


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
    # what the build has in hand: an affix that only counts with that weapon ("Increased Damage while
    # wielding a Dagger", "Melee Physical Damage if wielding a Sword"). Bow is the chip above - it takes
    # "while wielding a Bow" as well, so a bow build needs only the one tick.
    _focus("dagger", "Dagger", "wielding a dagger", "equipped dagger"),
    _focus("sword", "Sword", "wielding a sword", "equipped sword"),
    _focus("axe", "Axe", "wielding an axe", "wielding a axe"),
    _focus("mace", "Mace", "wielding a mace"),
    _focus("staff", "Staff", "wielding a staff"),
    _focus("shield", "Shield", "with a shield", "using a shield"),
    _focus("dual_wield", "Dual wielding", "dual wielding"),
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
    # the ailments the picker only ever shows inside the class lists: a cold build wants Frostbite
    # without having to tick Mage as well
    _ailment("frostbite", "Frostbite"),
    _ailment("time_rot", "Time Rot", "time rot"),
    _ailment("damned", "Damned", "damn"),
    _ailment("fear", "Fear", "fear"),
    # what the build keeps up rather than what it inflicts - the game calls these buffs, and the
    # picker files them under the classes ("Frenzy and Reduced Frenzy Effect")
    _buff("frenzy", "Frenzy", exclude=("level of",)),
    _buff("haste", "Haste"),
    _buff("inspiration", "Inspiration"),
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
    # what has to happen for the affix to count (Health Gained on Block), or what has to be true of
    # the build first (Increased Damage per active Shadow with Shadow Cascade). Their own row: ticked,
    # it holds the other rows back to the condition asked for - Health with On kill still keeps
    # "Health On Kill" and drops "Chance to Poison on Hit".
    _condition("on_hit", "On hit", "on hit", "when hit"),
    _condition("on_kill", "On kill", "on kill", "when you kill"),
    _condition("on_block", "On block", "on block"),
    _condition("on_crit", "On crit", "on crit", "on crits", "on critical strike", "when you crit",
               whole=True),
    _condition("on_use", "On use", "when you ", "after you ", "whenever "),
    _condition("if_you_have", "If you have", "if you "),
    _condition("per_stack", "Per stack", "per stack", "per active", "stacks of"),
    # a class: its own affixes - the picker's category, its idols', and the ones only it may have
    *(Concept(c.lower(), c, "class", only=c) for c in CLASSES),
    # one chip per class skill: the affixes that name it ("Level of Puncture", "Physical Penetration
    # with Puncture"). A row of its own, so ticking Puncture narrows the class chip to it plus the
    # affixes no skill names - while ticked alone it takes just those.
    *_skill_concepts(),
)


def _matches(c: Concept, a: dict, name: str) -> bool:
    """One affix, one concept: by its lowered name (or its picker category taken whole), or - for a class
    concept - by being that class's own affix, which its class bits say whatever it's called."""
    if c.only:
        bit = AFFIX_CLASS_BITS[c.only]
        return bool(a["class"] & bit) and not (a["class"] & AFFIX_NONSPECIFIC)
    hit = (any(_word(p).search(name) for p in c.phrases) if c.whole else any(p in name for p in c.phrases)) \
        or a["category"] in c.categories
    return hit and not any(x in name for x in c.exclude)


def concept_affixes(affixes: list[dict]) -> dict[str, list[dict]]:
    """Concept key -> the affixes it takes, over every affix (the editor filters these by the build)."""
    lowered = [a["name"].lower() for a in affixes]
    return {c.key: [a for a, name in zip(affixes, lowered) if _matches(c, a, name)] for c in CONCEPTS}
