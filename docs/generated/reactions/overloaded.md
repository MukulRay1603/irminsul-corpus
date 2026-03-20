---
category: reactions
topic: Overloaded Reaction
slug: overloaded
generated: 2026-03-20
---

# Overloaded Reaction

The Overloaded reaction is a transformative elemental reaction in Genshin Impact, triggered by applying both Pyro and Electro auras to an enemy. Upon activation, Overloaded deals a burst of Pyro damage in a small Area of Effect (AoE) and, crucially, causes a significant knockback effect on affected enemies. Unlike amplifying reactions such as Vaporize or Melt, Overloaded's damage scales independently of the triggering attack's personal damage statistics (ATK, CRIT Rate, CRIT DMG, DMG% bonuses). Instead, its damage is determined by the triggering character's Elemental Mastery (EM), their character level, and any specific reaction damage bonuses.

## Mechanics and Damage Calculation

When an enemy has both Pyro and Electro applied, Overloaded occurs. The reaction consumes both auras, with the damage being dealt as Pyro. The base damage multiplier for Overloaded is 2.0x, which is then scaled by the triggering character's level and Elemental Mastery. The formula for Overloaded damage is:

`Overloaded Damage = Base_Damage * (1 + EM_Bonus + Reaction_Bonus)`

1.  **Base Damage**: This component scales purely with the triggering character's level. At Level 90, the base damage for Overloaded is approximately 2880. This value is constant for all transformative reactions at a given level.
2.  **Elemental Mastery (EM) Bonus**: Elemental Mastery provides a significant percentage bonus to transformative reaction damage. For example, 500 EM grants approximately a 200% damage bonus, while 1000 EM provides roughly a 360% bonus. This means a Level 90 character with 1000 EM would deal approximately 2880 * (1 + 3.6) = 13,248 damage from Overloaded, before enemy resistances.
3.  **Reaction Bonus**: Certain artifact sets, weapon passives, or character talents can provide additional percentage bonuses to Overloaded damage. The 4-piece bonus of the Thundering Fury artifact set, for instance, grants a 40% bonus to Overloaded damage. Similarly, the 4-piece Crimson Witch of Flames set provides a 15% bonus to Pyro reactions, which includes Overloaded. These bonuses are additive with the EM bonus.

The damage dealt by Overloaded is considered "flat" damage, meaning it cannot critically hit and does not benefit from DMG% bonuses (e.g., Pyro DMG Bonus goblet) that typically amplify a character's personal attack damage. This characteristic is a defining feature of all transformative reactions, distinguishing them from amplifying reactions. The frequency of Overloaded reactions is limited by the Internal Cooldown (ICD) of elemental application on both the triggering character and the enemy. Most character abilities have a 2.5-second ICD or trigger reactions every third hit, meaning Overload cannot be triggered continuously by a single source of elemental application.

## The Knockback Problem

The most significant characteristic and often the primary drawback of Overloaded is its substantial knockback effect. Upon triggering, enemies affected by Overloaded are launched backward and often upward, disrupting their position. While this can be useful for staggering certain enemies, it poses a severe problem for melee-oriented Main DPS characters such as Hu Tao, Raiden Shogun, Diluc, or Razor. These characters rely on being in close proximity to enemies to land their attacks, and the constant knockback forces them to waste valuable combat time chasing targets, leading to a significant loss in overall damage per second (DPS).

This knockback effect is particularly problematic in single-target scenarios or against small-to-medium sized enemies. Larger enemies, such as Ruin Graders, Lawachurls, or most boss enemies (e.g., weekly bosses, Abyss bosses), are either immune to knockback or highly resistant, making Overloaded less disruptive in these specific encounters. However, against common enemies like Hilichurls, Treasure Hoarders, or Fatui Skirmishers (before they activate their elemental armor), the knockback can scatter them, making crowd control (CC) efforts by characters like Sucrose or Kazuha less effective, as enemies are pushed out of their Anemo vortexes.

## Effective Team Compositions and Strategies

Despite the knockback, Overloaded can be effectively utilized in specific team compositions and niche scenarios, primarily when the main damage dealer is ranged or when the reaction itself serves a secondary purpose.

### Ranged DPS Focus

Teams built around ranged Pyro or Electro DPS characters can mitigate the knockback issue.
*   **Yoimiya**: Her long-range normal attacks make her an ideal candidate for Overloaded teams. Paired with off-field Electro applicators like Fischl (Oz's constant Electro application), Beidou (Burst), or Raiden Shogun (Skill), Yoimiya can consistently trigger Overloaded without needing to chase enemies. A common team might include Yoimiya, Fischl, Yelan/Xingqiu (for Hydro application and damage reduction), and Zhongli (for shields and resistance shred). Here, Overload contributes significant damage alongside Yoimiya's personal Pyro damage and Vaporize from Hydro.
*   **Klee/Yanfei**: While both are Pyro catalyst users, their attacks have a shorter range than Yoimiya's, and their charged attacks can still suffer from enemies being pushed out of their optimal AoE. However, their ability to apply Pyro consistently can still make them viable with strong off-field Electro support.
*   **Electro Ranged DPS**: Characters like Yae Miko (with her Sesshou Sakura turrets) or Fischl (as an off-field Electro applicator) can trigger Overload with off-field Pyro sources like Xiangling's Pyronado or Thoma's Blazing Barrier. A team like Yae Miko, Fischl, Xiangling, and Bennett can generate numerous Overloaded reactions, contributing to overall team DPS, especially if Yae Miko or Fischl are built with high EM.

### Thoma Burgeon/Overload Builds

A particularly strong niche for Overloaded damage comes from Thoma in specific Dendro-Hydro-Electro-Pyro teams. In these "Burgeon" teams, Thoma is typically built with extremely high Elemental Mastery to maximize the damage of the Burgeon reaction (Pyro + Dendro Core).
*   **Mechanism**: In a team with Dendro (e.g., Nahida), Hydro (e.g., Xingqiu, Yelan), Electro (e.g., Raiden Shogun EM build, Kuki Shinobu), and Thoma, Dendro Cores are generated by Dendro + Hydro. Thoma's Blazing Barrier (from his Skill/Burst) applies Pyro, triggering Burgeon. If Electro is also present, it can react with Pyro to cause Overload, or with Dendro to cause Quicken/Spread/Aggravate.
*   **Synergy**: Since Thoma is already built for high EM for Burgeon, any Overloaded reactions he triggers will also deal substantial damage. In such teams, Overload often acts as a significant secondary source of damage. For example, a team like Nahida, Xingqiu, Raiden Shogun (EM build), and Thoma (EM build) will see both potent Burgeon and Overloaded damage contributing to the overall DPS, with Raiden often triggering Electro-related reactions and Thoma triggering Pyro-related ones. The knockback is less of an issue as the team relies on off-field damage and AoE.

### Overload as a Secondary Reaction

In many powerful teams, Overloaded occurs naturally as a byproduct rather than the primary focus.
*   **Raiden National (Raiden Shogun, Xiangling, Bennett, Xingqiu)**: This team is renowned for its high damage output, primarily through Vaporize (Xiangling's Pyronado with Xingqiu's Rainswords) and Electro-Charged. However, due to the constant application of both Pyro (Xiangling, Bennett) and Electro (Raiden), numerous Overloaded reactions are triggered. While not the main damage driver, these Overloads contribute to the overall damage ceiling and can help stagger enemies, especially in multi-target scenarios.

## Niche Use Cases and Advantages

Despite its drawbacks, Overloaded possesses several unique advantages that make it useful in specific situations:

*   **Shield Breaking**: Overloaded is highly effective against certain enemy shields due to its Pyro damage type. It rapidly depletes Geo shields (e.g., Geo Mitachurls, Geovishap Hatchlings, Fatui Geochanters) and Wooden shields (e.g., Wooden Shield Hilichurls, Hilichurl Shamans). The AoE nature also helps against groups of shielded enemies.
*   **Staggering and Disabling**: While problematic for melee DPS, the knockback can be strategically used to repeatedly stagger smaller enemies, preventing them from attacking or executing dangerous abilities. More importantly, Overloaded is excellent for disabling Ruin Guards and Ruin Hunters. Hitting their weak points (eyes for Ruin Guards, head for Ruin Hunters in flight) with a Pyro attack while they are Electro-affected (or vice-versa) can trigger Overload, causing them to enter a downed state, allowing for free damage.
*   **Environmental Interactions**: Overloaded can be used to trigger environmental effects, such as exploding Pyro barrels or igniting flammable grass, which can then apply Pyro aura to enemies for further reactions.
*   **Specific Abyss Chambers**: In certain Spiral Abyss chambers where enemies are grouped but immune to knockback (e.g., certain boss encounters or larger elite enemies), or when the chamber's ley line disorders favor Pyro and Electro damage, Overloaded can be a potent source of supplementary damage.

## Comparison with Vaporize

It is crucial to contrast Overloaded with Vaporize, another prominent Pyro-related reaction, to understand their distinct roles in Genshin