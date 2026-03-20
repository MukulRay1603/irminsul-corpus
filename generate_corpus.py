"""
generate_corpus.py — Irminsul Corpus Generator
Generates a complete, RAG-optimized Genshin Impact knowledge base using Gemini 2.5 Flash-Lite.

Usage:
    python generate_corpus.py                        # generate all topics
    python generate_corpus.py --category reactions   # single category
    python generate_corpus.py --resume               # skip already-done files
    python generate_corpus.py --list                 # show all topics

Free tier: Gemini 2.5 Flash-Lite — 15 RPM, 1000 RPD. Script self-throttles automatically.
"""

import os
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

# ── Config ─────────────────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
MODEL          = "gemini-2.5-flash-lite"  # 15 RPM, 1000 RPD — separate quota from Flash
OUTPUT_DIR     = Path("./docs/generated")
LOG_FILE       = Path("./logs/generation.log")
PROGRESS_FILE  = Path("./logs/progress.json")

# Flash-Lite: 15 RPM = 1 request per 4s minimum
# Each request takes ~10s response time, so total cycle ~15s naturally
# Add 5s post-response delay = safe buffer under 15 RPM
REQUEST_DELAY  = 5   # seconds AFTER response before next request
MAX_RETRIES    = 3
RETRY_DELAY    = 65  # just over 60s — waits out the full rate limit window

# ── Logging ────────────────────────────────────────────────────────────────────
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)

# ── Topic Registry ─────────────────────────────────────────────────────────────
# Each topic: (category, slug, display_name, prompt_instructions)
# Prompts are tightly scoped — one topic per file for clean RAG chunking.

SYSTEM_PROMPT = """You are writing entries for a Genshin Impact knowledge base that will be used 
in a RAG (Retrieval-Augmented Generation) system. Your writing must follow these rules strictly:

FORMATTING RULES:
- Use Markdown with clear ## and ### headers
- Write in dense, factual prose paragraphs — no filler, no repetition
- Every section must contain specific, accurate details (numbers, names, mechanics)
- Use bullet lists ONLY for stat thresholds, team comps, or weapon rankings — never for lore
- MINIMUM LENGTH: Every entry must be at least 600 words. Aim for 800-1200 words.
- Start directly with content — no preamble like "Sure!" or "Here is..."
- If you find yourself writing less than 600 words, you are not being thorough enough. Keep going.

CONTENT RULES:
- Be precise: include exact multipliers, ER thresholds, CRIT ratios, cooldowns where relevant
- For lore: include relationships, motivations, key events, and in-game context
- For builds: include BiS, strong F2P, and budget options with clear reasoning
- For mechanics: explain the formula or interaction AND give practical examples
- For reactions: include the multiplier values, which direction is stronger, team examples
- Never write a section with only 1-2 sentences. Every section needs depth.
- Never invent details you are not confident about — say "details vary" rather than fabricate
- Write as if the reader is a serious Genshin player who wants depth, not a beginner summary
"""

TOPICS = [

    # ── ELEMENTAL REACTIONS ──────────────────────────────────────────────────
    ("reactions", "vaporize",        "Vaporize Reaction",          "Cover the Vaporize reaction completely: both directions (1.5x Pyro trigger vs 2.0x Hydro trigger), the role of Elemental Mastery in amplifying the multiplier, ICD interactions that affect proc rate, best characters to trigger each direction, and top team compositions built around Vaporize. Include specific EM breakpoints and how gauge theory affects uptime."),
    ("reactions", "melt",            "Melt Reaction",              "Cover the Melt reaction: both directions (2.0x Pyro trigger vs 1.5x Cryo trigger), why Ganyu Melt and Hu Tao Melt work differently, EM scaling, ICD interactions, Cryo aura maintenance, and top team compositions. Explain why Pyro-triggered Melt is rarer to sustain and what setups achieve it."),
    ("reactions", "freeze",          "Freeze Reaction",            "Cover Freeze mechanics: how Frozen status works, duration scaling with gauge strength, the Shatter interaction with heavy attacks, Blizzard Strayer 4pc synergy (+40% CRIT Rate on Frozen), Cryo Resonance bonus, perma-freeze team requirements, and why Freeze trivializes mobile enemies. Include best Hydro and Cryo applicators for Freeze teams."),
    ("reactions", "superconduct",    "Superconduct Reaction",      "Cover Superconduct: the 40% Physical RES shred mechanic, duration (12 seconds), why it only matters for Physical DPS, which characters trigger it most efficiently, and the Physical DPS teams that rely on it (Eula, Razor, physical Fischl). Include Cryo battery role and CRIT Rate bonuses from Cryo Resonance in Physical teams."),
    ("reactions", "overloaded",      "Overloaded Reaction",        "Cover Overloaded: the AoE Pyro-based damage, the knockback problem for melee DPS, EM scaling for the reaction damage, which teams can use it effectively despite knockback (ranged DPS, Thoma Burgeon builds), and the niche cases where Overloaded becomes useful. Contrast with Vaporize for Pyro+Electro contexts."),
    ("reactions", "electrocharged",  "Electrocharged Reaction",    "Cover Electrocharged: why it uniquely does not consume either elemental aura, how it chains between Hydro-affected enemies, periodic tick damage, the ability to enable other reactions simultaneously, and which team compositions exploit this. Cover Fischl/Beidou Electro + Hydro compositions and the special case of Childe teams."),
    ("reactions", "swirl",           "Swirl and Viridescent Venerer","Cover Swirl mechanics completely: how Anemo absorbs elements and spreads them, that Swirl damage scales with EM only (not ATK), the 40% RES shred from Viridescent Venerer 4pc, why VV is mandatory on Anemo supports, Sucrose's EM share passive, Kazuha's A4 DMG% buff from EM, and Venti's energy refund mechanic. Include the limitation that Anemo cannot Swirl Geo or Dendro."),
    ("reactions", "crystallize",     "Crystallize and Geo Reactions","Cover Crystallize: how it creates elemental shards, shield strength scaling with EM and level, Geo Resonance bonuses (+15% DMG while shielded, +15% shield strength), why Geo does not amplify elemental reactions, Zhongli's universal RES shred mechanic, and when Geo teams are optimal versus when they are suboptimal compared to reaction teams."),
    ("reactions", "quicken_aggravate_spread", "Quicken, Aggravate, and Spread", "Cover the Dendro-Electro reaction tree completely: Quicken as the base status, Aggravate (Electro hitting Quickened enemy = bonus Electro damage), Spread (Dendro hitting Quickened enemy = bonus Dendro damage), why neither reaction consumes the Quicken aura enabling sustained procs, EM scaling for both branches, and the top characters for each branch. Contrast the sustained uptime model with Vaporize/Melt timing requirements."),
    ("reactions", "bloom_hyperbloom_burgeon", "Bloom, Hyperbloom, and Burgeon", "Cover the full Bloom reaction tree: Bloom (Dendro + Hydro creates Dendro Cores), Hyperbloom (Electro detonates cores as homing projectiles, scales with Electro character EM), Burgeon (Pyro detonates cores in AoE, scales with Pyro character EM, can self-damage), and Pure Bloom (cores explode naturally). Include top team compositions for each branch and the EM investment requirements. Cover why Raiden is the premier Hyperbloom trigger."),
    ("reactions", "burning",         "Burning Reaction",           "Cover Burning (Dendro + Pyro): the continuous Pyro DoT on the target and the terrain, how it interacts with other reactions, the rare teams that use it intentionally (some Nahida compositions), and why it is generally avoided in meta compositions. Cover the Thoma-related Burning interactions and niche uses."),

    # ── GAME MECHANICS ───────────────────────────────────────────────────────
    ("mechanics", "damage_formula",  "Damage Formula and Calculation", "Explain the full Genshin damage formula step by step: Base Damage (scaling stat × ability%), DMG Bonus additive stacking, CRIT multiplier, Enemy DEF multiplier (attacker level vs enemy level), Enemy RES multiplier tiers (-100%/0%/75%+), Reaction multiplier. Explain why DEF shred and RES shred are multiplicative with other bonuses. Include the 1:2 CRIT ratio rule and why it maximizes average damage."),
    ("mechanics", "icd",             "Internal Cooldown (ICD)",    "Explain ICD (Internal Cooldown) in depth: the standard 2.5s/3-hit reset rule, what 'no ICD' means and which abilities have it, how ICD affects reaction proc rates for key characters (Xingqiu Rain Swords, Fischl Oz, Ganyu Charged Attacks), why ICD is critical for building Vaporize and Melt teams, and how to work around ICD in team construction. Include specific examples of characters with unusual ICD patterns."),
    ("mechanics", "gauge_theory",    "Elemental Gauge Theory",     "Explain Elemental Gauge Theory: invisible gauge units (1U, 2U, 4U), how stronger applications leave larger auras that take more opposing element to remove, how Freeze duration scales with combined gauge strength, why some characters apply elements weakly (low unit values) and others strongly, and practical team-building implications. Cover how gauge values affect Vaporize/Melt proc frequency."),
    ("mechanics", "er_and_energy",   "Energy Recharge and Energy System", "Explain the energy system completely: how particles are generated (on-kill vs on-hit), on-field vs off-field energy collection (60% penalty for off-field), elemental resonance for particle collection, ER thresholds for every major support (Xiangling 180-200%, Bennett 170-190%, Xingqiu 180-200%, Raiden 250-300%, Nahida 120-130%, Fischl 120%, Kazuha 140-160%), and why ER is the most common build bottleneck. Include Sacrificial weapon interactions and Favonius particle generation."),
    ("mechanics", "artifact_system", "Artifact System and Optimization", "Cover the artifact system completely: five slots and their main stat options, 2pc vs 4pc set bonus tradeoffs, why 4pc set bonuses often outweigh substat optimization, substat priority by role (DPS vs support), the sands/goblet/circlet main stat decision framework, RNG substat rolling mechanics, and artifact domain resin efficiency. Include the standard DPS build (ATK% sands, Elemental DMG goblet, CRIT circlet) and when to deviate."),
    ("mechanics", "constellations",  "Constellation System",       "Explain the constellation system: how duplicate characters unlock C1-C6, the power spike pattern (C1-C2 usually quality of life, C6 often transformative or dangerous), specific notable constellations that change playstyle (Bennett C6 Pyro infusion warning, Kazuha C2 +200 EM, Xingqiu C2 extra sword, Fischl C6 joint attack, Xiangling C4 Pyronado extension, Raiden C2 Burst DMG, Hu Tao C1 no stamina cost), and how to evaluate constellation value versus pulling for new characters."),
    ("mechanics", "talent_system",   "Talent Leveling and Priority", "Cover talent leveling: the three talent types (Normal Attack, Skill, Burst), which to prioritize for each role archetype, talent materials and domain scheduling by day, Crown of Insight for level 10 talents, and specific talent priority for major characters (Xiangling: Burst > Skill > Normal, Bennett: Burst > Skill > Normal, Kazuha: Skill > Burst > Normal, Hu Tao: Normal = Skill > Burst). Explain why some characters' Normal Attacks are irrelevant."),
    ("mechanics", "team_building",   "Team Building Fundamentals", "Cover team building from first principles: the four roles (Main DPS, Sub-DPS, Support, Battery), why teams need both reaction enablers and reaction triggers, energy particle flow between team members, the double-carry vs hypercarry archetypes, resonance bonuses worth building around (Pyro +25% ATK, Cryo +15% CRIT, Geo +15% DMG shielded, Dendro +50 EM), and why the same support (Bennett, Kazuha, Xingqiu) appears in so many top teams."),
    ("mechanics", "spiral_abyss",    "Spiral Abyss Guide",         "Cover Spiral Abyss completely: floor structure (Floors 1-12, 9-12 are rotating content), the two-team split mechanic requiring two independent teams, star system (3 stars per chamber, 36 total for full clear), time limits, buff cards and modifiers, the biweekly reset, enemy lineup patterns, and meta team archetypes for clearing (Hypercarry, Dual DPS, Reaction team, Mono-element). Include how to build two teams that share no key supports."),
    ("mechanics", "exploration",     "Exploration Mechanics",      "Cover Genshin exploration mechanics: stamina system (climbing, swimming, gliding), elemental sight, wind currents and updrafts, ley line disorders, treasure compass, oculi collection (Anemoculus, Geoculus, Electroculus, etc.), statue upgrades, reputation systems per nation, and the regional specialty gathering for ascension materials. Include phygon mechanics in Natlan."),
    ("mechanics", "resin_system",    "Resin and Progression System","Cover the resin system: Original Resin (160 cap, 8-min regeneration), Condensed Resin (max 5), Fragile Resin sources, domain costs (20 resin), boss costs (40 resin weekly/40 resin world), the daily commission system, weekly bosses and their caps, Battle Pass structure, and efficient resin spending priority by account progression stage (early: level up cost, mid: talent books, late: artifact domains)."),
    ("mechanics", "weapons",         "Weapon System and Refinement","Cover the weapon system: 1-5 star tiers, refinement (R1-R5) and how it affects passive strength, weapon ascension materials, the substat system (all 5-stars have ATK% primary except exceptions), which 3-4 star weapons are genuinely competitive (Black Tassel on Zhongli, Favonius weapons for ER, The Catch for Xiangling/Raiden, Dragon's Bane for EM characters), and refinement priority for free-to-play weapons."),

    # ── PYRO CHARACTERS ──────────────────────────────────────────────────────
    ("characters", "hu_tao",         "Hu Tao",                     "Complete Hu Tao guide: lore (77th director of Wangsheng, her philosophy on death, relationship with Zhongli), kit mechanics (E HP consumption and Pyro infusion, A1 low-HP buff, Charged Attack focus), best builds (Staff of Homa BiS, Dragon's Bane F2P, White Tassel budget), artifact sets (4pc Crimson Witch), team compositions (Vaporize with Yelan+Xingqiu+Zhongli, Melt variant, budget team), why Bennett is ANTI-synergy, ER thresholds, and constellation value. Include her stat priority."),
    ("characters", "yoimiya",        "Yoimiya",                    "Complete Yoimiya guide: lore (Naganohara fireworks master, personality and relationships in Inazuma), kit mechanics (E Normal Attack Pyro conversion, unique Burst mechanic that marks enemies to chain damage), builds (Thundering Pulse BiS, Aqua Simulacra alt, Rust F2P, Hamayumi craftable), artifact sets (4pc Shimenawa's Reminiscence tradeoffs), team compositions (Vaporize team, Mono Pyro), her single-target weakness, and how her Burst enables off-field Pyro application."),
    ("characters", "xiangling",      "Xiangling",                  "Complete Xiangling guide: lore (Liyue chef, free character from Spiral Abyss 3-3, why she is top-tier despite being 4-star), kit mechanics (Guoba AoE Pyro, Pyronado off-field Burst that snapshots buffs), builds (The Catch BiS F2P, Kitain Cross Spear alt, 4pc Emblem of Severed Fate), ER threshold (180-200%), team compositions (National Team, Childe-Xiangling, Raiden National), and the critical interaction between Bennett's ATK buff and Pyronado snapshot."),
    ("characters", "bennett",        "Bennett",                    "Complete Bennett guide: lore (Mondstadt adventurer with legendary bad luck, found by Adventurers' Guild), kit mechanics (Burst field healing + ATK buff based on Base ATK, threshold behavior at C0 vs C1), builds (Aquila Favonia to maximize Base ATK, Favonius Sword for ER, 4pc Noblesse Oblige for team ATK buff), ER threshold (170-190%), the C6 WARNING (Pyro infusion that destroys certain teams), why he appears in nearly every meta team, and how to use him correctly."),
    ("characters", "dehya",          "Dehya",                      "Complete Dehya guide: lore (Eremite warrior, Desert Mercenaries leader, backstory in Sumeru desert), kit mechanics (Fiery Sanctum damage redirection field, how she absorbs hits for allies, Burst rapid punch window), unique tank identity versus shield-based protection, builds (Beacon of the Reed Sea signature, 4pc Tenacity of the Millelith), team synergy with Furina (Furina rewards HP loss, Dehya provides HP loss), and why she underperforms in typical DPS roles."),
    ("characters", "lyney",          "Lyney",                      "Complete Lyney guide: lore (Fontaine magician, House of the Hearth, relationship with Lynette and Freminet), kit mechanics (Prop Surplus stack system, Grin-Malkin Hat Pyro bombs, Charged Attack focus), the Mono Pyro team requirement (he loses damage in teams with non-Pyro allies), builds (Bridal Remorse signature, The First Great Magic alternative, 4pc Marechaussee Hunter), optimal team compositions (Mono Pyro with Bennett/Xiangling/Kazuha), and his high single-target damage ceiling."),
    ("characters", "arlecchino",     "Arlecchino",                 "Complete Arlecchino guide: lore (4th Harbinger Knave, House of the Hearth director, how she took over from the previous director, her complex maternal relationship with her operatives), kit mechanics (Bond of Life stacking system, HP drain that feeds damage bonus, Normal Attack focus in Burst state), builds (Crimson Moon's Semblance signature, Staff of Homa alt, 4pc Whimsy or Fragment of Harmonic Whimsy), team compositions, and why she does not want traditional healers."),
    ("characters", "mavuika",        "Mavuika",                    "Complete Mavuika guide: lore (Pyro Archon of Natlan, warrior Archon who fights alongside her people, relationship with the tribes, role in Natlan's conflict against the Abyss), kit mechanics (Nightsoul mechanics unique to Natlan characters, motorcycle-style Night Realm traversal, Burst as combat entry), builds and team compositions, her role in Natlan story, and how her kit interacts with other Natlan characters' Phlogiston system."),

    # ── HYDRO CHARACTERS ─────────────────────────────────────────────────────
    ("characters", "yelan",          "Yelan",                      "Complete Yelan guide: lore (Yuheng of the Liyue Qixing operating as spy/intelligence, mysterious background, connection to the Ministry of Civil Affairs), kit mechanics (Breakthrough Barbs Exquisite Throw, Burst Dice off-field Hydro + ramping DMG% buff from 1% to 50% over 15s), builds (Aqua Simulacra BiS, Fading Twilight F2P, 4pc Emblem of Severed Fate), team compositions (double Hydro with Xingqiu, Furina teams, Neuvillette teams), and why she is considered a Xingqiu upgrade for most teams."),
    ("characters", "xingqiu",        "Xingqiu",                    "Complete Xingqiu guide: lore (second son of the Feiyun Commerce Guild, scholar and martial artist, friendship with Chongyun), kit mechanics (Rain Swords off-field Hydro on Normal Attacks, damage reduction from Rain Swords, ICD on Hydro application), builds (Sacrificial Sword BiS for double E, 4pc Emblem of Severed Fate), ER threshold (180-200%), team compositions (National Team, Hu Tao team, any Pyro Vaporize team), and why he remains meta despite being 4-star."),
    ("characters", "neuvillette",    "Neuvillette",                 "Complete Neuvillette guide: lore (Chief Justice Iudex of Fontaine, revealed as the Dragon of Water sovereign predating current divine order, his relationship with Furina and his grief-induced rain), kit mechanics (Charged Attack Water Droplet collection system, passive CRIT Rate buffs, self-sufficient damage without reaction partners), builds (Tome of the Eternal Flow signature, Sacrificial Jade F2P, 4pc Marechaussee Hunter), team compositions (Furina+Kazuha+Jean premier team, budget variants), and his self-sufficient playstyle."),
    ("characters", "furina",         "Furina",                      "Complete Furina guide: lore (the full tragedy — Focalors splitting herself, Furina's 500-year performance as a false god, her breakdown when the truth is revealed, Focalors' sacrifice, Furina choosing to live as an ordinary human), kit mechanics (Salon members HP drain + Hydro damage, Fanfare stack accumulation from HP changes, Burst team DMG% bonus scaling with Fanfare), builds (Splendor of Tranquil Waters signature, Favonius Codex F2P, 4pc Golden Troupe), team compositions, and why she requires a dedicated healer."),
    ("characters", "kokomi",         "Kokomi",                     "Complete Kokomi guide: lore (Divine Priestess of Watatsumi Island, military strategist who opposed the Shogunate, relationship with Gorou and the Resistance), kit mechanics (Bake-Kurage healing jellyfish, Ceremonial Garment Burst that enhances healing and enables Normal Attack damage, intentional negative CRIT Rate -100%), builds (Everlasting Moonglow signature, Prototype Amber F2P for healing, 4pc Ocean-Hued Clam for healing-to-damage), role as premier Hydro applicator and healer, and Freeze team usage."),
    ("characters", "barbara",        "Barbara",                     "Complete Barbara guide: lore (deaconess of the Church of Favonius, Lumine/Aether's introduction to healing in Mondstadt, idol singer persona, relationship with Jean), kit mechanics (Let the Show Begin Hydro application + Melody Loop self-healing AoE, Shining Miracle burst heal), builds (Thrilling Tales of Dragon Slayers for ATK buff support role, 4pc Ocean-Hued Clam), her role as budget Hydro applicator and emergency revive specialist (C6 revives one character per fight), and when she is preferable over Kokomi."),

    # ── ELECTRO CHARACTERS ───────────────────────────────────────────────────
    ("characters", "raiden_shogun",  "Raiden Shogun",              "Complete Raiden Shogun guide: lore (Ei vs the Shogun puppet, Makoto's death and Ei's grief, Vision Hunt Decree motivation, resolution with Traveler, Yae Miko's role as her anchor), kit mechanics (Resolve stack accumulation from team Burst damage, Musou Isshin state, team energy refund after Burst), builds (Engulfing Lightning signature, The Catch BiS F2P, 4pc Emblem of Severed Fate), ER threshold (250-300%), team compositions (Raiden National, Raiden Hypercarry with Sara+Kazuha+Bennett), and Hyperbloom trigger role."),
    ("characters", "cyno",           "Cyno",                       "Complete Cyno guide: lore (General Mahamatra of Sumeru, childhood with Tighnari, the justice vs law tension in his story quest, terrible joke reputation), kit mechanics (18-second extended Burst state, Skill CD reduction through Burst, A4 state extension, Pactsworn Pathclearer stacks), best in Dendro reaction teams (Aggravate and Quickbloom), builds (Staff of the Scarlet Sands signature, 4pc Thundering Fury), team compositions (Aggravate: Nahida+Fischl+Baizhu, Quickbloom variant), and his ER management within extended Burst."),
    ("characters", "fischl",         "Fischl",                     "Complete Fischl guide: lore (Amy's real identity, the Fischl persona as coping mechanism, relationship with Mona, Oz as Vision manifestation), kit mechanics (Oz summoning and duration, C6 joint ATK on every Electro reaction, Nightrider repositioning), builds (The Stringless for EM+Skill DMG, 4pc Golden Troupe or 4pc Thundering Fury at C6), team compositions (Aggravate teams, Quickbloom, Superconduct physical, National variants), and why she is the best off-field Electro applicator in the game."),
    ("characters", "yae_miko",       "Yae Miko",                   "Complete Yae Miko guide: lore (Guuji of Grand Narukami Shrine, Ei's longest companion, kitsune nature, her centuries of watching over Inazuma while Ei meditated, the complicated emotional dynamic between them), kit mechanics (Sesshou Sakura totems with chaining Electro damage, Burst that detonates all totems for massive damage, totem placement strategy), builds (Kagura's Verity signature, The Widsith alt, 4pc Golden Troupe), team compositions (Aggravate with Nahida, Hyperbloom trigger, Quicken teams), and ER management."),
    ("characters", "keqing",         "Keqing",                     "Complete Keqing guide: lore (Yuheng of Liyue Qixing, pragmatic skeptic of divine authority, her reaction to Zhongli's staged death, belief in human self-determination), kit mechanics (Stellar Restoration teleport and Electro infusion, Burst AoE slashes, the transition from Physical to Electro build), builds (Primordial Jade Cutter for Electro, 4pc Thundering Fury for Aggravate), team compositions (Aggravate: Keqing+Nahida+Fischl+Baizhu), and why Aggravate transformed her viability."),
    ("characters", "beidou",         "Beidou",                     "Complete Beidou guide: lore (Captain of the Crux Fleet, defeated the sea beast Haishan barehanded, her relationship with Fischl and the crew, underground fighting scene in Liyue), kit mechanics (Tidecaller counter mechanic with perfect parry bonus, Stormbreaker Burst lightning bouncing between enemies — unique AoE Electro off-field), builds (Serpent Spine BP weapon, 4pc Emblem of Severed Fate), team compositions (Beidou shines in multi-enemy content, pairs with Fischl for double Electro), ER threshold and Burst uptime requirements."),

    # ── CRYO CHARACTERS ──────────────────────────────────────────────────────
    ("characters", "ganyu",          "Ganyu",                      "Complete Ganyu guide: lore (half-adeptus qilin secretary of Liyue Qixing for 3000 years, identity struggle between human and divine, relationship with Xiao and Cloud Retainer, Lantern Rite emotional arc), kit mechanics (Frostflake Arrow Level 2 Charged Attack always-crits explosion, Celestial Shower off-field Cryo Burst, Trail of the Qilin ice lotus), builds (Amos' Bow BiS, Prototype Crescent F2P craftable, 4pc Blizzard Strayer for free CRIT Rate), team compositions (Freeze: Kokomi+Kazuha+Shenhe, Melt with Xiangling+Bennett+Zhongli), and her ceiling as one of the highest AoE DPS characters."),
    ("characters", "ayaka",          "Ayaka",                      "Complete Ayaka guide: lore (eldest Kamisato daughter, her isolation within the Yashiro Commission, the contrast between her public duty and private vulnerability, relationship with Thoma and her brothers), kit mechanics (Dash Cryo application on exit, Normal Attack chain, Kamisato Art: Soumetsu Burst snowstorm), builds (Mistsplitter Reforged BiS, Amenoma Kageuchi craftable F2P, 4pc Blizzard Strayer), ER threshold, team compositions (premier Freeze: Kokomi+Kazuha+Shenhe, Ayaka+Mona+Venti+Diona classic), and stamina management."),
    ("characters", "shenhe",         "Shenhe",                     "Complete Shenhe guide: lore (human child raised by adeptus Cloud Retainer, emotional binding training, her suppressed feelings and slow recovery, connection to Xiao and Liyue adepti), kit mechanics (Icy Quill Cryo damage bonus charges — flat damage added to Cryo hits, limited number per use, Burst Cryo RES shred), why she is a pure Cryo team buffer, builds (Calamity Queller signature, Favonius Lance ER option, 4pc Noblesse Oblige), team compositions (mandatory in top Ganyu and Ayaka teams), and her unique flat damage bonus mechanic."),
    ("characters", "wriothesley",    "Wriothesley",                 "Complete Wriothesley guide: lore (Duke of Meropide Fortress, won leadership through combat, his own criminal past and self-acceptance, relationship with Furina as one of the few who treated her as a person), kit mechanics (Gracious Tribute HP management rhythm, Chilling Penalty HP-consuming Charged Attacks, HP recovery threshold, passive that heals on crossing thresholds), builds (Cashflow Supervision signature, 4pc Marechaussee Hunter for HP-fluctuation CRIT), team compositions (Furina+Shenhe+Kazuha premier), and his comfortable playstyle."),
    ("characters", "rosaria",        "Rosaria",                    "Complete Rosaria guide: lore (Sister of the Church of Favonius with a dark and violent past before joining, her unorthodox methods, the mysterious background hinted at in her story quest), kit mechanics (Rites of Termination Burst Cryo field with CRIT Rate share to party from behind-enemy Skill position), builds (Favonius Lance for ER support role, 4pc Noblesse Oblige), her role as Cryo battery and CRIT Rate share support in physical and Melt teams, and how the CRIT share mechanic works."),

    # ── ANEMO CHARACTERS ─────────────────────────────────────────────────────
    ("characters", "kazuha",         "Kazuha",                     "Complete Kazuha guide: lore (wandering samurai of Inazuma, his friend's death during the Vision Hunt Decree, self-imposed exile, finding purpose through travel, relationship with Beidou and the Crux Fleet), kit mechanics (Chihayaburu Skill grouping and plunge, Kazuha Slash Burst Swirl, A4 passive EM-to-elemental-DMG% conversion at 200 EM = 40% elemental DMG for whole team), builds (Freedom-Sworn BiS, Iron Sting craftable F2P, 4pc Viridescent Venerer mandatory), team role as the single best elemental support, and why he appears in more meta teams than any other character."),
    ("characters", "venti",          "Venti",                      "Complete Venti guide: lore (Barbatos the wind spirit, the nameless bard who died liberating Mondstadt, Venti wearing his appearance as tribute, centuries of absence, relationship with Dvalin, loss of Gnosis to Signora), kit mechanics (Skyward Sonnet Skill launch, Stormeye Burst vacuum for 8 seconds, elemental absorption and additional damage, 15-energy refund to absorbed element characters), builds (Elegy for the End BiS support, Favonius Warbow F2P, 4pc Viridescent Venerer), team compositions, and his weakness against large/boss enemies."),
    ("characters", "xiao",           "Xiao",                       "Complete Xiao guide: lore (last surviving Yaksha, centuries of karmic debt from demon slaying, the suffering that never fully heals, his lost fellow Yakshas, his relationship with the Traveler as rare genuine solace, connection to Morax), kit mechanics (Lemniscatic Wind Cycling Skill double-cast, Bane of All Evil Burst that converts Normal/Charged/Plunge to Anemo and buffs them at cost of continuous HP drain), builds (Staff of Homa, Calamity Queller, Deathmatch, 4pc Vermillion Hereafter or Marechaussee Hunter), team compositions (needs strong healer/shielder due to HP drain), and his unique Anemo DPS identity outside reaction teams."),
    ("characters", "sucrose",        "Sucrose",                    "Complete Sucrose guide: lore (Knights of Favonius alchemist obsessed with bio-alchemy, relationship with Albedo, extremely anxious personality, friendship with Fischl in a genuine way), kit mechanics (Forbidden Creation Isomer Skill AoE Anemo, Chaos Theory Burst Anemo field, 20% EM share to team on Swirl trigger, Burst additional EM buff), builds (Sacrificial Fragments for double Skill, 4pc Viridescent Venerer), budget replacement role for Kazuha, team compositions (National Team budget version, Taser teams), and how her EM share mechanic works."),
    ("characters", "wanderer",       "Wanderer (Scaramouche)",     "Complete Wanderer guide: lore (created by Ei as prototype vessel and discarded, found by Niwa the craftsman, his accumulated cruelty as armor against abandonment, 6th Harbinger Scaramouche, attempt to become a god in Sumeru, defeat, Nahida erasing him from the Irminsul, rebirth as Wanderer without memories — the meditation on identity without continuity of memory), kit mechanics (Windfavored flying state, Kuugo Sakuretsu Skill in air, Kyougen Burst), builds (Tulaytullah's Remembrance signature, 4pc Desert Pavilion Chronicle), team compositions, and his unique aerial DPS playstyle."),

    # ── GEO CHARACTERS ───────────────────────────────────────────────────────
    ("characters", "zhongli",        "Zhongli",                    "Complete Zhongli guide: lore (Morax the Geo Archon, 6000 years of governance through contracts, the adepti and their service to him, staging his own death to test Liyue, handing his Gnosis to the Tsaritsa, his mortal life at Wangsheng Funeral Parlor, the mora problem, relationship with Hu Tao and the adepti), kit mechanics (Dominus Lapidis Stele resonance and 20% universal RES shred, Planet Befall petrification Burst, shield scaling with HP), builds (Black Tassel 3-star as legitimate BiS for shielding, Staff of Homa for DPS hybrid, 4pc Tenacity of the Millelith), and why he is the gold standard defensive support."),
    ("characters", "itto",           "Itto",                       "Complete Itto guide: lore (Oni of Oni-Goroshi, leader of the Arataki Gang, relationship with Kuki Shinobu and Ushi, his rivalry with Kujou Sara, his surprisingly gentle nature behind the bravado), kit mechanics (Superlative Superstrength stacks from Normal Attacks, Raging Oni King Burst that converts Normal Attacks to Geo and buffs DEF-based damage, unique Charged Attack Arataki Kesagiri combo), builds (Redhorn Stonethresher BiS, Serpent Spine BP, 4pc Husk of Opulent Dreams), team compositions (Itto+Gorou+Zhongli+Albedo double-Geo support), and DEF scaling explained."),
    ("characters", "albedo",         "Albedo",                     "Complete Albedo guide: lore (homunculus created by Rhinedottir/Gold, the mystery of his synthetic nature, what defines consciousness for a created being, his research at Dragonspine, relationship with Sucrose, the doppelganger who appeared during Chalk Prince event), kit mechanics (Tectonic Tide Burst, Solar Isotoma off-field DEF-scaled sub-DPS platform, Fatal Reckoning stacks), builds (Cinnabar Spindle event sword BiS, Harbinger of Dawn 3-star alt, 4pc Husk of Opulent Dreams), and his role as premium off-field Geo sub-DPS that fits almost any team."),

    # ── DENDRO CHARACTERS ────────────────────────────────────────────────────
    ("characters", "nahida",         "Nahida",                     "Complete Nahida guide: lore (Lesser Lord Kusanali confined in the Sanctuary of Surasthana for 500 years, her access to the world through the Irminsul and people's dreams, what she lost by being the God of Wisdom denied wisdom, her emotional intelligence from watching humanity, the cost of erasing Scaramouche from the Irminsul), kit mechanics (All Schemes to Know Skill marks with Seed of Skandha for multi-target Dendro damage on reactions, Illusory Heart Burst buffs based on team element composition — EM from Pyro, CRIT from Electro, duration from Hydro), builds (A Thousand Floating Dreams BiS, Sacrificial Fragments F2P, Magic Guide R5 competitive 3-star, 4pc Deepwood Memories for support or 4pc Gilded Dreams for DPS), and top team compositions."),
    ("characters", "tighnari",       "Tighnari",                   "Complete Tighnari guide: lore (forest ranger of Avidya Forest, trained scholar who chose practical conservation over Akademiya politics, friendship with Cyno, his early resistance to the Akademiya's abuses), kit mechanics (Vijnana-Phala Mine Skill that buffs Charged Attack speed and creates Clusterbloom Arrows, Fashioner's Tanglevine Shaft Burst), builds (Hunter's Path BiS, The Stringless alt, 4pc Deepwood Memories), team compositions (Aggravate: Tighnari+Yae Miko+Fischl+Nahida), and why he is primarily a Charged Attack focused DPS."),
    ("characters", "baizhu",         "Baizhu",                     "Complete Baizhu guide: lore (owner of Bubu Pharmacy in Liyue, his personal quest for immortality to stay with Qiqi, what he sacrificed to prolong Qiqi's existence, his relationship with Changsheng his snake), kit mechanics (Holistic Revivification Burst that creates Gossamer Sprites that heal and apply Dendro, unique seamless healing that also provides shields and Dendro application), builds (Jadefall's Splendor signature, Prototype Amber craftable F2P, 4pc Deepwood Memories for Dendro support or 4pc Tenacity of Millelith), role as premier healer in Dendro reaction teams."),

    # ── FONTAINE CHARACTERS ──────────────────────────────────────────────────
    ("characters", "navia",          "Navia",                      "Complete Navia guide: lore (President of Spina di Rosula, her father's false accusation and death, the conspiracy she uncovered, her warm generosity built on genuine grief, relationship with Clorinde and Furina), kit mechanics (Crystalline Cyst Dust stack collection from Geo and Crystallize, Ceremonial Crystallization Burst that fires Shrapnel, unique Geo DPS that uses Crystallize productively rather than defensively), builds (Verdict signature, 4pc Nighttime Whispers in the Echoing Woods), team compositions that maximize Crystallize shards, and her position as the best Geo DPS after Itto."),
    ("characters", "clorinde",       "Clorinde",                   "Complete Clorinde guide: lore (Champion Duelist of Fontaine, her childhood bond with Navia, the demonic pact in her arm and how she lives with it, her deeply loyal and precise personality), kit mechanics (Hunter's Vigil Electro-enhanced Normal Attacks in Bind state, Ombres Dansantes swift Burst movement), builds (Absolution signature, 4pc Fragment of Harmonic Whimsy), team compositions (Aggravate or Quickbloom with Nahida), and her position as a top-tier Electro DPS."),
    ("characters", "sigewinne",      "Sigewinne",                  "Complete Sigewinne guide: lore (melusine nurse of Meropide Fortress, her warm relationship with Wriothesley, what it means to be a melusine in Fontaine's society), kit mechanics (Rebound Hydrotherapy HP-scaling Hydro damage, Bolstering Bubblebalm Burst healing and HP max buffs), builds (Silvershower Heartstrings signature, Prototype Amber craftable, 4pc Ocean-Hued Clam), team compositions as Hydro support and buffer in HP-scaling teams."),

    # ── NATLAN CHARACTERS ────────────────────────────────────────────────────
    ("characters", "kinich",         "Kinich",                     "Complete Kinich guide: lore (Scions of the Canopy tribe representative, his relationship with his Dragonlord companion Ajaw, their bickering dynamic that hides genuine partnership, his role in Natlan's defense), kit mechanics (Canopy Hunter Riding High Nightsoul state, Scalespiker Cannon Burst with Ajaw), builds (Peak Patrol Song signature, 4pc Obsidian Codex), team compositions in Natlan Phlogiston teams, and the Nightsoul mechanic explained."),
    ("characters", "xilonen",        "Xilonen",                    "Complete Xilonen guide: lore (Ocelot tribe member, master craftsperson who forged the Stone Slate, her role in Natlan's cultural preservation and memory), kit mechanics (Yohual's Scratch Blade Nightsoul infusion, Ocelotl Xochitl Burst with team RES shred), builds (Peak Patrol Song, 4pc Obsidian Codex), her role as the best support in Natlan teams providing massive RES shred, and how she enables Natlan team compositions."),

    # ── ARCHON LORE DEEP DIVES ───────────────────────────────────────────────
    ("lore", "barbatos_venti_lore",  "Barbatos and Mondstadt History", "Deep dive into Barbatos and Mondstadt lore: the ancient wind spirit Barbatos before the Archon War, the nameless bard who dreamed of liberating Mondstadt from Decarabian the Storm God, the uprising and the bard's death, why Barbatos took the bard's form as tribute, how Mondstadt was shaped by the ideal of freedom without a ruling god, the Lawrence Clan aristocracy and their overthrow, Barbatos's centuries of wandering, the loss of his Gnosis to Signora, and what his absence says about his philosophy of freedom."),
    ("lore", "morax_zhongli_lore",   "Morax and Liyue History",    "Deep dive into Morax and Liyue lore: Morax as one of the oldest and most powerful Archons, the contract philosophy that built Liyue, the Archon War battles, creation of the adepti-human pact, Rex Lapis mythology and the Rite of Descension, the defeat of Osial and other ancient gods, thousands of years of governance alongside the adepti, the decision to fake his death, why he handed his Gnosis to the Tsaritsa (terms he designed himself), and his assessment that Liyue's people are ready to govern without a god."),
    ("lore", "ei_makoto_inazuma_lore","Ei, Makoto, and Inazuma History","Deep dive: Makoto the original Electro Archon and her death in the cataclysm, Ei's grief and five hundred years alone, the creation of the Shogun puppet as a governance proxy, the Vision Hunt Decree as policy born from grief (preserving by preventing change), the philosophical difference between Eternity-as-stasis and true eternal preservation, the Yashiro Commission and Kujou Commission history, Watatsumi Island's worship of Orobashi and resentment toward the mainland, and how the Traveler's confrontation in the Plane of Euthymia begins Ei's change."),
    ("lore", "nahida_sumeru_lore",   "Nahida and Sumeru History",  "Deep dive: the original Dendro Archon Rukkhadevata and her sacrifice in the cataclysm, the Akademiya's founding and slow corruption into a knowledge-control apparatus, Nahida being born and immediately imprisoned as politically inconvenient, her five hundred years of access to the world only through the Irminsul and dreams, King Deshret's ancient civilization in the desert and what it means for Sumeru's deeper history, the Scarlet King mythology, the Akademiya's scheme with Scaramouche and the Gnosis, and what Nahida gave up to protect the Irminsul."),
    ("lore", "furina_focalors_lore", "Furina, Focalors, and Fontaine History","Deep dive: the ancient prophecy that Fontaine's people would dissolve into the Primordial Sea, Focalors' plan to break it by splitting herself into a powerless human vessel (Furina) and a waiting divine consciousness, what Furina's five hundred years of performance actually cost her psychologically, the Court of Fontaine's justice system as a theatrical institution built on her illusion, the melusines and their role in Fontaine society, how the prophecy was broken through Neuvillette's tears and Focalors' sacrifice, and Furina's choice to continue living as an ordinary human."),

    # ── WORLD LORE ───────────────────────────────────────────────────────────
    ("lore", "celestia_mystery",     "Celestia and the True Nature of Teyvat", "Deep dive into the Celestia mystery: what Celestia physically is (structures visible in sky, seat of divine authority), the Sustainer of Heavenly Principles who defeated the Traveler, hints that the world of Teyvat is a controlled or fabricated reality (painted sky references, the Traveler's sibling's discoveries), the Primordial One and the Second Who Came mythology, how the Gnoses function as Celestia's control mechanism over the Archons, the pattern of history being erased or edited (Irminsul editing, characters written out of history), and what the recurring theme of divine authority as coercive control implies about the endgame."),
    ("lore", "khaenriah_abyss",      "Khaenri'ah and the Abyss",   "Complete Khaenri'ah lore: the underground nation without a god that achieved alchemical and technological mastery, Rhinedottir/Gold who created both synthetic life (Albedo) and the means of Khaenri'ah's destruction, King Irmin corrupted into the Eclipse King, the cataclysm five hundred years ago, Celestia's punishment of Khaenri'ah's people (nobility became monsters, commoners became Hilichurls — immortal cursed wanderers), Dainsleif the Bough Keeper cursed with immortality to watch it all, what the Abyss Order is and what they actually want, and the Traveler's sibling's role in leading them."),
    ("lore", "traveler_sibling",     "The Traveler and Their Sibling","Cover the Traveler's core narrative: two siblings from another world who arrived in Teyvat, the Sustainer separating them, the sibling's transformation after witnessing the cataclysm and Khaenri'ah's fate, their decision to lead the Abyss Order against the celestial order, the emotional tension of their relationship with the Traveler across the story, what we know of their goals versus their methods, the Natlan storyline's revelations about their involvement, and the unresolved question of whether their cause is just even if their methods are harmful."),
    ("lore", "fatui_tsaritsa",       "The Fatui and the Tsaritsa",  "Cover Fatui and Tsaritsa lore: Snezhnaya as the Cryo Archon's nation, the Tsaritsa described as a god who lost love for her people and pursues revolution against Celestia, the Eleven Harbingers as elite agents, the Fatui's global intelligence and coercion network, Gnosis collection plan, each Harbinger's personality and role (Childe, Scaramouche, Arlecchino, Signora who died, Columbina, Pantalone), the sympathetic framing of the Tsaritsa's anti-Celestia stance, and what her plan actually requires the collected Gnoses to accomplish."),
    ("lore", "archon_war",           "The Archon War and Ancient History","Cover the Archon War period: the era when countless gods competed for territory and worshippers, how the current Seven Archons came to power by defeating rivals, Morax's battles and the shaping of Liyue's borders, Barbatos and the nameless bard liberating Mondstadt from Decarabian, what happened to the defeated gods (some survived as diminished beings, some died entirely), the Adepti War and how the adepti bonded to Morax through contracts, and how the Archon War's end created the current world order under Celestia."),
    ("lore", "five_hundred_years",   "The Cataclysm Five Hundred Years Ago","Cover the cataclysm comprehensively: the simultaneous catastrophes five hundred years ago, Khaenri'ah's destruction by Celestia after the Eclipse King incident, the original Dendro Archon's death, how multiple Archons were affected or changed, the creation of the Abyss Order from Khaenri'ah's survivors, Dainsleif's loss and curse, the deployment of the Yakshas to purge the demon tide that flooded Liyue afterward, how Fontaine's prophecy connects to this period, and why the cataclysm is the pivotal event the entire main story circles around."),
    ("lore", "visions_and_gnoses",   "Visions and Gnoses Explained","Cover the Vision and Gnosis systems in depth: what Visions are (divine gifts from Celestia based on strong human ambition and will), how they grant elemental power, the philosophical question of whether they are gifts or tethers to the divine order, the Gnoses as the Archons' divine power sources and Celestia's control mechanism, the Gnosis collection by the Tsaritsa and what it means to strip Archons of formal divine status, how multiple Archons have voluntarily or involuntarily lost their Gnoses and what happened afterward, and what this implies about the relationship between divine authority and individual power."),

    # ── NATIONS DEEP DIVES ───────────────────────────────────────────────────
    ("nations", "mondstadt",         "Mondstadt — Nation of Freedom","Complete Mondstadt guide: geography (island city, Stormterror's Lair, Dragonspine ancient civilization, Wolvendom, Cape Oath), the Knights of Favonius and their reputation for inefficiency, the Lawrence Clan aristocracy history and overthrow, the Church of Favonius, the winery culture and Dawn Winery, Dvalin/Stormterror's story and corruption, major factions and their tensions, Dragonspine's ancient inhabitants and what the Sheer Cold mechanic represents narratively, and the Mondstadt Archon Quest's themes of freedom and trust."),
    ("nations", "liyue",             "Liyue — Nation of Contracts", "Complete Liyue guide: geography (Liyue Harbor as Teyvat's trade center, Jueyun Karst adepti territory, Qingce Village, Stone Gate, Guyun Stone Forest where Osial was imprisoned), the Liyue Qixing merchant governance structure, the adepti and their contract with Morax, the Rite of Descension and Rex Lapis mythology, annual Lantern Rite celebration, the Wangsheng Funeral Parlor's cultural role, Osial's backstory as a defeated sea god, and how Liyue functions as a civilization built entirely on trust and contract law."),
    ("nations", "inazuma",           "Inazuma — Nation of Eternity", "Complete Inazuma guide: the five major islands (Narukami, Kannazuka, Yashiori, Watatsumi, Seirai), the three Commissions (Yashiro — Grand Narukami Shrine; Kanjou — trade; Kujou — military), the Vision Hunt Decree's societal impact, Watatsumi Island's worship of Orobashi and historical tension, the Tatarigami curse on Yashiori Island from Orobashi's remains, Thunder Manifestation, the Raiden Shogun's design as a governance mechanism, and how Inazuma's arc is fundamentally about what is lost when a nation optimizes for preventing loss."),
    ("nations", "sumeru",            "Sumeru — Nation of Wisdom",   "Complete Sumeru guide: the rainforest-desert divide and their cultural differences, the Akademiya's six Darshans (schools of thought), the Akasha Terminal network and its social control implications, King Deshret's ancient desert empire and the Scarlet King mythology, the Aaru Village and Devout of the Sands culture, the Aranaras forest spirits and their relationship with the Irminsul, Ley Lines and their connection to the Dendro Archon, Port Ormos and the trade route, and Sumeru's core thematic tension between accumulated knowledge and actual wisdom."),
    ("nations", "fontaine",          "Fontaine — Nation of Justice", "Complete Fontaine guide: the underwater geography (Court of Fontaine above water, Fontaine Research Institute, the Fortress of Meropide underwater prison, the Hydro Dragon's tear basin), the Court of Fontaine trial system and its cultural importance, the melusines as Fontaine's unique citizens, the ancient prophecy and its origins, the Pneuma and Ousia mechanical system for Fontaine puzzles, the Primordial Sea lore, how Fontaine's steampunk technology developed without Geo or divine backing, and why justice (not law) is Fontaine's true value."),
    ("nations", "natlan",            "Natlan — Nation of War",       "Complete Natlan guide: the six tribes (Children of Echoes, Flower-Feather Clan, Ocelot Tribe, Scions of the Canopy, Clearwater Tribe, Night-Wind's Numen), the Dragonlord companion culture unique to Natlan, the Phlogiston movement system and how it changes exploration, the Night Kingdom and Night Realm lore, the Abyss incursion as direct military conflict unlike other nations' more political Archon Quests, the Pyro Archon's warrior leadership style, and the cultural significance of the Drum of the Soulferry."),
    ("nations", "snezhnaya",         "Snezhnaya and the Fatui",     "Cover everything known about Snezhnaya: the frozen nation of the Cryo Archon, the Fatui as diplomatic cover for a global intelligence and military network, the Eleven Harbingers and their ranks, the Tsaritsa's loss of love for her people and what caused it (hinted connections to the cataclysm and Celestia's actions), Snezhnaya's industrial and military capability implied by Fatui operations worldwide, what is known about the Tsaritsa's plan for the collected Gnoses, and the unanswered question of whether she is a villain or a necessary revolutionary."),
]


# ── Progress tracking ──────────────────────────────────────────────────────────
def load_progress() -> dict:
    if PROGRESS_FILE.exists():
        return json.loads(PROGRESS_FILE.read_text())
    return {}


def save_progress(progress: dict):
    PROGRESS_FILE.parent.mkdir(parents=True, exist_ok=True)
    PROGRESS_FILE.write_text(json.dumps(progress, indent=2))


# ── Generator ─────────────────────────────────────────────────────────────────
def generate_topic(client, category: str, slug: str, name: str, instructions: str) -> str:
    prompt = f"""Write a comprehensive Genshin Impact knowledge base entry for: **{name}**

Category: {category}

Instructions: {instructions}

CRITICAL REQUIREMENTS:
- Minimum 600 words. Do not stop early.
- Start directly with a # {name} heading
- Cover every aspect mentioned in the instructions with real depth
- Include specific numbers, names, and examples throughout
- This will be used in a RAG system — users depend on this being complete and accurate
"""
    for attempt in range(MAX_RETRIES):
        try:
            response = client.models.generate_content(
                model=MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    temperature=0.4,
                    max_output_tokens=4096,
                )
            )
            return response.text
        except Exception as e:
            err = str(e).lower()
            is_rate_limit = "429" in err or "quota" in err or "rate" in err or "resource" in err
            is_timeout    = "timeout" in err or "timed out" in err or "read operation" in err
            if is_rate_limit or is_timeout:
                wait = RETRY_DELAY * (attempt + 1)
                reason = "Rate limited" if is_rate_limit else "Timeout"
                logger.warning(f"{reason}. Waiting {wait}s before retry {attempt+1}/{MAX_RETRIES}...")
                time.sleep(wait)
            else:
                logger.error(f"Error generating {slug}: {e}")
                raise
    raise RuntimeError(f"Failed to generate {slug} after {MAX_RETRIES} retries")


def run(category_filter: str = None, resume: bool = True):
    if not GEMINI_API_KEY:
        raise EnvironmentError("GEMINI_API_KEY not set in .env")

    client = genai.Client(api_key=GEMINI_API_KEY)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    progress = load_progress() if resume else {}

    topics = TOPICS
    if category_filter:
        topics = [t for t in topics if t[0] == category_filter]
        if not topics:
            logger.error(f"No topics found for category '{category_filter}'")
            logger.info(f"Available categories: {sorted(set(t[0] for t in TOPICS))}")
            return

    total    = len(topics)
    done     = 0
    skipped  = 0
    failed   = []

    logger.info(f"Starting corpus generation — {total} topics")
    logger.info(f"Output: {OUTPUT_DIR.resolve()}")
    logger.info(f"Model: {MODEL}")
    logger.info("=" * 60)

    for i, (category, slug, name, instructions) in enumerate(topics, 1):
        out_path = OUTPUT_DIR / category / f"{slug}.md"

        if resume and out_path.exists() and out_path.stat().st_size > 200:
            logger.info(f"[{i:3}/{total}] SKIP  {category}/{slug}")
            skipped += 1
            continue

        logger.info(f"[{i:3}/{total}] GEN   {category}/{slug} — {name}")

        try:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            content = generate_topic(client, category, slug, name, instructions)

            header = f"---\ncategory: {category}\ntopic: {name}\nslug: {slug}\ngenerated: {datetime.now().strftime('%Y-%m-%d')}\n---\n\n"
            out_path.write_text(header + content, encoding="utf-8")

            word_count = len(content.split())
            logger.info(f"         DONE  {word_count} words -> {out_path}")

            progress[slug] = {"status": "done", "words": word_count, "file": str(out_path)}
            save_progress(progress)
            done += 1

        except Exception as e:
            logger.error(f"         FAIL  {slug}: {e}")
            failed.append(slug)
            progress[slug] = {"status": "failed", "error": str(e)}
            save_progress(progress)

        if i < total:
            time.sleep(REQUEST_DELAY)

    logger.info("=" * 60)
    logger.info(f"COMPLETE — {done} generated, {skipped} skipped, {len(failed)} failed")
    if failed:
        logger.warning(f"Failed topics: {failed}")
    logger.info(f"Total files in {OUTPUT_DIR}: {sum(1 for _ in OUTPUT_DIR.rglob('*.md'))}")


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Irminsul Corpus Generator")
    parser.add_argument("--category", type=str, default=None,
                        help="Generate only topics in this category (reactions/mechanics/characters/lore/nations)")
    parser.add_argument("--resume",   action="store_true", default=True,
                        help="Skip already-generated files (default: True)")
    parser.add_argument("--no-resume", dest="resume", action="store_false",
                        help="Regenerate all files, even existing ones")
    parser.add_argument("--list",     action="store_true",
                        help="List all topics and exit")
    args = parser.parse_args()

    if args.list:
        categories = {}
        for cat, slug, name, _ in TOPICS:
            categories.setdefault(cat, []).append((slug, name))
        for cat, items in sorted(categories.items()):
            print(f"\n── {cat.upper()} ({len(items)} topics) ──")
            for slug, name in items:
                status = "✓" if (OUTPUT_DIR / cat / f"{slug}.md").exists() else "·"
                print(f"  {status} {slug:<35} {name}")
        print(f"\nTotal: {len(TOPICS)} topics")
    else:
        run(category_filter=args.category, resume=args.resume)
