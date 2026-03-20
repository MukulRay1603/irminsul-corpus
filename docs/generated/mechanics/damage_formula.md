---
category: mechanics
topic: Damage Formula and Calculation
slug: damage_formula
generated: 2026-03-20
---

# Damage Formula and Calculation

The damage dealt by an attack in Genshin Impact is calculated through a multi-stage formula that accounts for various character stats, buffs, enemy attributes, and elemental reactions. Understanding this formula is crucial for optimizing character builds and team compositions. The general damage formula can be broken down as follows:

**Final Damage = Base Damage × (1 + DMG Bonus) × CRIT Multiplier × Enemy DEF Multiplier × Enemy RES Multiplier × Reaction Multiplier**

Each component of this formula will be explained in detail.

## Base Damage

The Base Damage is the foundational value upon which all other multipliers act. It is determined by the character's specific scaling stat and the base multiplier of the ability being used.

**Base Damage = (Attacker's Scaling Stat × Ability Multiplier %) + Flat Damage Bonus**

The "Attacker's Scaling Stat" refers to the primary stat that governs an ability's damage. This is typically the character's ATK stat, but it can also be HP (e.g., Hu Tao's Elemental Skill, Yelan's Elemental Burst) or DEF (e.g., Albedo's Elemental Skill, Itto's Elemental Burst). The "Ability Multiplier %" is the percentage value provided by the specific skill or burst at a given talent level. For example, a character's Normal Attack might have a multiplier of 150% at talent level 6.

"Flat Damage Bonus" is a less common source of damage, primarily coming from certain artifact set bonuses (like the 2-piece bonus of the Noblesse Oblige set adding 20 ATK) or specific character abilities. These flat values are added directly to the calculated damage before any percentage multipliers are applied.

## DMG Bonus

The DMG Bonus represents all additive percentage increases to damage. This category includes bonuses from:

*   **Character's Elemental DMG Bonus:** This is the most significant component, gained from artifacts (e.g., the 4-piece bonus of the Gladiator's Finale set granting 35% ATK, which indirectly increases damage, or the 2-piece bonus of various elemental DMG goblets granting 15% of a specific element's DMG).
*   **Artifact Set Bonuses:** Many artifact sets provide DMG bonuses to specific attack types or elemental types.
*   **Weapon Passives:** Some weapons offer direct DMG bonuses.
*   **Team Buffs:** Character abilities that provide DMG buffs (e.g., Bennett's Elemental Burst, Kazuha's Elemental Skill/Burst when infused).
*   **Enemy Debuffs:** Certain enemy debuffs can reduce incoming damage, effectively acting as a negative DMG Bonus.

All these sources of DMG Bonus are additive. For instance, if a character has a 15% Pyro DMG Bonus from a goblet and receives a 20% Pyro DMG Bonus from Bennett's Elemental Burst, their total Pyro DMG Bonus for that calculation will be 35%.

**DMG Bonus = (Character Elemental DMG Bonus %) + (Artifact Set Bonus %) + (Weapon Passive Bonus %) + (Team Buff Bonus %) + ...**

## CRIT Multiplier

Critical hits significantly increase damage output. When a critical hit occurs, the damage is multiplied by a factor determined by the character's CRIT DMG stat.

**CRIT Multiplier = 1 + CRIT DMG %**

A standard CRIT DMG stat of 50% means a critical hit deals 1.5 times the normal damage (1 + 0.50). The CRIT DMG stat is primarily increased through artifact substats and the weapon's secondary stat.

### The 1:2 CRIT Ratio Rule

To maximize average damage output, players often aim for a CRIT Rate to CRIT DMG ratio of approximately 1:2. This means for every 1% CRIT Rate, a character should ideally have 2% CRIT DMG. For example, a character with 50% CRIT Rate and 100% CRIT DMG is generally better than a character with 25% CRIT Rate and 150% CRIT DMG, assuming all other stats are equal.

The reason for this rule lies in the expected value of damage. Let CR be the CRIT Rate and CD be the CRIT DMG. The average damage multiplier from CRIT is:

**Average CRIT Multiplier = (1 - CR) × 1 + CR × (1 + CD)**

To maximize this value for a fixed amount of CR + CD, the optimal distribution is when CD = 2 * CR. For instance, if a player has 100% total CRIT stat points to distribute between CRIT Rate and CRIT DMG, allocating 33.3% to CRIT Rate and 66.7% to CRIT DMG yields the highest average damage. This is because CRIT Rate determines the *chance* of the CRIT DMG multiplier activating, making it more efficient to have a higher CRIT DMG when the CRIT Rate is already substantial.

## Enemy DEF Multiplier

Enemies in Genshin Impact have a Defense (DEF) stat that reduces incoming damage. The damage reduction is calculated based on the attacker's level and the enemy's level.

**Enemy DEF Multiplier = (Attacker Level × 4 + 500) / ((Attacker Level × 4 + 500) + (Enemy DEF × (1 - DEF Reduction %)))**

Where "Enemy DEF" is the enemy's base DEF value, and "DEF Reduction %" refers to effects that directly reduce the enemy's DEF (e.g., the 4-piece bonus of the Superconduct reaction or certain character abilities like the 2-piece bonus of the Viridescent Venerer set for Anemo damage).

*   **At equal levels (Attacker Level = Enemy Level):** The formula simplifies to approximately `(4L + 500) / (4L + 500 + DEF)`, resulting in a damage reduction that increases with the enemy's DEF.
*   **When Attacker Level > Enemy Level:** The damage multiplier increases, meaning the attacker deals more damage.
*   **When Attacker Level < Enemy Level:** The damage multiplier decreases, meaning the attacker deals less damage.

This is why leveling up characters is crucial for damage scaling, especially against higher-level content.

### DEF Shred

Effects that reduce enemy DEF, often called "DEF Shred," are multiplicative with other damage bonuses. This means they are applied *after* the base DEF calculation. For example, if an enemy has 500 DEF and an effect reduces DEF by 30%, the enemy's effective DEF becomes 500 * (1 - 0.30) = 350. This reduced DEF is then used in the DEF Multiplier formula. This multiplicative nature makes DEF shred exceptionally powerful, as it bypasses the diminishing returns of additive DMG Bonuses.

## Enemy RES Multiplier

Enemies have resistances (RES) to different elemental and physical damage types. This resistance acts as a multiplier on the damage dealt.

**Enemy RES Multiplier = 1 - Enemy RES %**

*   **Base Resistances:** Most enemies start with 10% RES to all elements and physical damage.
*   **Negative Resistances:** Some effects can lower enemy RES below 0%. For example, the 4-piece bonus of the Viridescent Venerer artifact set reduces the RES of enemies to the Swirled element by 40%. If an enemy has 10% RES to Hydro and is hit by a Swirl that triggers Viridescent Venerer, their Hydro RES becomes 10% - 40% = -30%. This means they take 130% of the Hydro damage (1 - (-0.30) = 1.30).
*   **High Resistances:** Enemies like Slimes often have high innate resistances to their corresponding element. Some bosses can also have very high resistances to specific damage types.

### RES Shred

Similar to DEF Shred, RES Shred effects are multiplicative. This means they are applied to the enemy's base RES *before* the final RES Multiplier is calculated. For example, if an enemy has 10% Hydro RES and a RES Shred effect reduces it by 30%, the enemy's effective RES becomes 10% - 30% = -20%. The damage multiplier then becomes 1 - (-0.20) = 1.20, meaning the Hydro damage taken is increased by 20%. This multiplicative interaction makes RES Shred extremely potent, especially when combined with other damage-increasing mechanics.

## Reaction Multiplier

Elemental Reactions are a core part of Genshin Impact's combat system and significantly amplify damage. The multiplier for an elemental reaction depends on the specific reaction, the triggering element, and the character's Elemental Mastery (EM).

**Reaction Damage = Base Reaction Damage × (1 + EM Bonus % + Reaction Bonus %)**

*   **Base Reaction Damage:** This is a fixed multiplier provided by the game for each reaction. For example, Vaporize and Melt have a base multiplier of 1.5x (for Hydro triggering Vaporize) or 2x (for Pyro triggering Melt). Transformative reactions like Overload, Electro-Charged, Superconduct, Swirl, and Shatter have their own base multipliers.
*   **EM Bonus %:** This is derived from the triggering character's Elemental Mastery. The formula for EM bonus is complex and scales differently for each reaction type. For Transformative reactions, the EM bonus percentage is calculated as:
    **EM Bonus % = EM / (EM + 1400)**
    This means that as EM increases, the percentage bonus from EM becomes smaller, but the absolute increase in damage still grows.
*   **Reaction Bonus %:** This includes any percentage increases to the specific reaction's damage from artifacts (e.g., the 4-piece bonus of the Crimson Witch of Flames for Vaporize/Melt, or the 4-piece bonus of the Thundering Fury set for Electro-related reactions) or character abilities.

**Crucially, Transformative Reaction damage (Overload, Electro-Charged, Superconduct, Swirl, Shatter, Bloom, Hyperbloom, Burgeon) scales with the character's level and Elemental Mastery, not ATK, HP, or DEF.** Amplifying reactions (Vaporize, Melt) add their multiplier to the *damage instance* of the attack that triggers them, meaning they benefit from the attacker's ATK, CRIT, DMG Bonuses, etc., in addition to the reaction multiplier itself.

**Example:** A Pyro character triggering Vaporize with a 150% multiplier. The base damage of the Pyro attack is 1000. The character has 200 EM and a 15% Vaporize DMG Bonus from artifacts.

1.  **Base Damage:** 1000
2.  **DMG Bonus:** Assume 50% (from goblet, set, etc.)
3.  **CRIT Multiplier:** Assume 100% CRIT DMG (so 2x multiplier)
4.  **Enemy DEF/RES:** Assume neutral (1x multiplier)
5.  **Reaction Multiplier:**
    *   Base Vaporize: 1.5x
    *   EM Bonus %: 200 EM / (200 + 1400) = 200 / 1600 = 0.125 or 12.5%
    *   Reaction Bonus %: 15%
    *   Total Reaction Multiplier = 1.5 × (1 + 0.125 + 0.15) = 1.5 × 1.275 = 1.9125x

**Final Damage = 1000 × (1 + 0.50) × 2 × 1 × 1.9125 = 1000 × 1.5 × 2 × 1.9125 = 5737.5**

This detailed breakdown illustrates the complex interplay of various factors that contribute to the final damage output in Genshin Impact, emphasizing the importance of balancing stats and understanding multiplicative interactions.