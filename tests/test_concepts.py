"""The Wanted affixes tab's build concepts: what its chips take, and that the editor can label them."""
from pathlib import Path
import re
import sys

from lefilter import i18n
from lefilter.concepts import CONCEPTS, CONCEPT_GROUPS, concept_affixes
from lefilter.gamedata import AFFIX_CLASS_BITS, AFFIX_NONSPECIFIC, SKILLS

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "packaging"))
import translate_ui  # noqa: E402


def affix(name, category="Damage Type", cls=0):
    return {"name": name, "category": category, "class": cls}


def takes(key, *names):
    return {a["name"] for a in concept_affixes([affix(n) for n in names])[key]}


def test_a_damage_concept_takes_the_type_and_leaves_the_others():
    got = takes("physical", "Physical Damage", "Melee Physical Damage", "Physical Penetration", "Fire Damage",
                "Increased Physical Damage over Time")
    assert got == {"Physical Damage", "Melee Physical Damage", "Physical Penetration",
                   "Increased Physical Damage over Time"}


def test_the_elemental_concept_is_its_own_affix_not_the_three_elements():
    got = takes("elemental", "Elemental Damage", "Fire Damage", "Cold Penetration")
    assert got == {"Elemental Damage"}


def test_one_ailment_per_concept_and_the_poison_chip_leaves_the_poison_damage_alone():
    bleed = takes("bleed", "Chance to Inflict Bleed on Hit", "Increased Bleed Duration", "Bleed Resistance")
    assert bleed == {"Chance to Inflict Bleed on Hit", "Increased Bleed Duration", "Bleed Resistance"}
    poison = takes("poison_ailment", "Chance to Poison on Hit", "Poison Damage", "Poison Penetration")
    assert poison == {"Chance to Poison on Hit"}, "Poison Damage and Penetration belong to the damage chip"


def test_the_stun_chip_leaves_out_the_health_affix_that_also_avoids_stun():
    assert takes("stun", "Increased Stun Chance", "Health and Stun Avoidance") == {"Increased Stun Chance"}


def test_a_class_concept_takes_only_the_classs_own_affixes():
    rogue, mage = AFFIX_CLASS_BITS["Rogue"], AFFIX_CLASS_BITS["Mage"]
    mine = affix("Rogue Skill", "Rogue", rogue)
    theirs = affix("Mage Skill", "Mage", mage)
    idol = affix("Rogue Idol Affix", "Rogue Idols", rogue)
    anyone = affix("Everyone's", "Other", AFFIX_NONSPECIFIC)
    untyped = affix("Increased Health", "Health", 0)
    got = concept_affixes([mine, theirs, idol, anyone, untyped])
    assert [a["name"] for a in got["rogue"]] == ["Rogue Skill", "Rogue Idol Affix"]
    assert [a["name"] for a in got["mage"]] == ["Mage Skill"]
    assert got["sentinel"] == []


def test_a_skill_chip_takes_the_affixes_naming_that_skill_as_a_whole_word():
    got = takes("skill_rogue_net", "Level of Net", "Increased Net Damage", "Magnetic Network")
    assert got == {"Level of Net", "Increased Net Damage"}, "Network isn't the Rogue's Net skill"


def test_a_skill_leaves_the_longer_one_it_sits_inside_to_it():
    assert takes("skill_mage_static", "Level of Static", "Level of Static Orb") == {"Level of Static"}
    assert takes("skill_mage_static_orb", "Level of Static", "Level of Static Orb") == {"Level of Static Orb"}


def test_a_skill_takes_the_spellings_the_affixes_give_it():
    assert takes("skill_mage_frost_wall", "Level of Frostwall", "Frost Wall Duration") \
        == {"Level of Frostwall", "Frost Wall Duration"}
    assert takes("skill_rogue_synchronized_strike", "Mana Efficiency with Synchronised Strike") \
        == {"Mana Efficiency with Synchronised Strike"}


def test_every_class_skill_gets_a_chip_of_its_own():
    def slug(name):
        return re.sub(r"\W+", "_", name.lower()).strip("_")
    want = {(f"skill_{cls.lower()}_{slug(name)}", name) for cls in SKILLS for name, _ in SKILLS[cls]}
    assert {(c.key, c.label) for c in CONCEPTS if c.group == "skills"} == want


def test_every_skill_name_is_the_games_own_word_for_it():
    """The chips' label comes from the game's Descriptors table, one key each - and so all nine languages."""
    assert all(name == name.strip() and key for skills in SKILLS.values() for name, key in skills)
    assert {name for skills in SKILLS.values() for name, _ in skills} <= set(i18n.UI_GAME_TERMS)


def test_a_weapon_chip_takes_only_the_affixes_that_need_that_weapon():
    got = takes("dagger", "Increased Damage while wielding a Dagger", "Physical Penetration while wielding a Dagger",
                "Increased Critical Strike Chance per Equipped Dagger", "Increased Damage while wielding a Sword")
    assert got == {"Increased Damage while wielding a Dagger", "Physical Penetration while wielding a Dagger",
                   "Increased Critical Strike Chance per Equipped Dagger"}


def test_a_condition_chip_takes_only_what_needs_that_condition():
    assert takes("on_block", "Health Gained on Block", "Block Chance", "Health on Kill") == {"Health Gained on Block"}
    assert takes("on_kill", "Health On Kill", "Health Gained on Block") == {"Health On Kill"}
    assert takes("per_stack", "Increased Damage per active Shadow with Shadow Cascade", "Health Regen per Second") \
        == {"Increased Damage per active Shadow with Shadow Cascade"}


def test_on_crit_is_whole_word_so_a_minion_crit_is_not_one():
    assert takes("on_crit", "Chance to Cast Fire Aura on Critical Strike", "Minion Critical Strike Chance") \
        == {"Chance to Cast Fire Aura on Critical Strike"}


def test_the_ailment_and_buff_chips_take_what_the_picker_files_under_the_classes():
    assert takes("frostbite", "Frostbite Duration", "Cold Penetration with Frostbite") \
        == {"Frostbite Duration", "Cold Penetration with Frostbite"}
    assert takes("time_rot", "Increased Time Rot Duration", "Void Damage") == {"Increased Time Rot Duration"}
    assert takes("haste", "Haste Effect and Haste duration on Evade") == {"Haste Effect and Haste duration on Evade"}
    assert takes("frenzy", "Frenzy and Reduced Frenzy Effect", "Level of Summon Frenzy Totem") \
        == {"Frenzy and Reduced Frenzy Effect"}, "the skill called Frenzy Totem isn't the buff"


def test_every_concept_has_a_label_of_a_group_the_editor_shows():
    groups = {key for key, _ in CONCEPT_GROUPS}
    assert len(groups) == len(CONCEPT_GROUPS)
    assert len({c.key for c in CONCEPTS}) == len(CONCEPTS)
    assert all(c.label and c.key for c in CONCEPTS)
    assert all(c.phrases or c.only for c in CONCEPTS)   # matched by name, or a class's own affixes
    assert groups == {c.group for c in CONCEPTS}
    for g in groups:   # no two chips of one row looking the same
        labels = [c.label for c in CONCEPTS if c.group == g]
        assert len(labels) == len(set(labels)), g


def test_concept_affixes_covers_every_concept():
    picks = concept_affixes([affix("Physical Damage"), affix("Rogue Skill", "Rogue", AFFIX_CLASS_BITS["Rogue"])])
    assert set(picks) == {c.key for c in CONCEPTS}
    assert [a["name"] for a in picks["physical"]] == ["Physical Damage"]
    assert len(picks["rogue"]) == 1


def test_the_catalogs_are_asked_for_every_concept_label():
    """server_labels() feeds collect(): without it the i18n test can't see the labels the server sends."""
    labels = translate_ui.server_labels()
    assert {c.label for c in CONCEPTS} <= labels
    assert {label for _, label in CONCEPT_GROUPS} <= labels
