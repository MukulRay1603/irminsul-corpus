---
category: reactions
topic: Burning Reaction
slug: burning
generated: 2026-03-20
---

# Burning Reaction

The Burning reaction is a **Dendro + Pyro** elemental reaction that applies a continuous Pyro Damage over Time (DoT) effect to enemies and the surrounding terrain. This DoT is classified as Pyro damage and scales with the Elemental Mastery (EM) of the character who triggers the reaction, as well as their Level. The base damage of Burning is determined by a multiplier applied to the character's Level and EM, with the formula being `(127 * Level + 323) * (1 + 1.2 * EM / (2000 + EM))`. This multiplier is then further modified by the character's Elemental Mastery, the target's resistance, and any buffs or debuffs applied.

Burning applies a Pyro aura that deals damage every 2 seconds. The initial trigger of Burning deals a small amount of damage, and subsequent ticks of the Burning aura deal damage based on the same scaling as the initial trigger. The Burning aura has a duration of 9 seconds, but this duration can be extended by reapplying Dendro or Pyro to the affected target, allowing the Burning DoT to persist for longer periods. A key characteristic of Burning is its ability to spread to the terrain, igniting grass and other flammable objects. This can be both beneficial and detrimental, as it can create persistent AoE Pyro damage zones but also potentially hinder movement or cause unintended reactions.

## Burning Mechanics and Interactions

Burning damage is a flat damage calculation, meaning it does not benefit from Critical Rate or Critical Damage. This is a significant drawback for many DPS-focused characters, as their primary damage scaling attributes become irrelevant for the Burning DoT. The reaction itself has a base multiplier of 0.5 for the initial trigger and 0.25 for subsequent ticks, which is then multiplied by the character's Level and EM scaling. For example, a Level 90 character with 800 EM would have a base multiplier of approximately `(127 * 90 + 323) * (1 + 1.2 * 800 / (2000 + 800)) ≈ 11753 * (1 + 1.2 * 0.2857) ≈ 11753 * 1.3428 ≈ 15776`. This base damage is then subject to enemy resistances and any damage buffs.

Burning does not consume the elemental auras on the target as quickly as other reactions. A single application of Dendro or Pyro can sustain Burning for its full duration, and subsequent ticks of Burning apply a weak Pyro aura. This means that if a target has a Hydro aura, Burning will not be able to apply its Pyro aura until the Hydro aura is consumed or overwritten. Conversely, if a target has a Pyro aura, applying Dendro will trigger Burning and consume the Pyro aura, but the Burning DoT will then reapply a weak Pyro aura.

The interaction of Burning with other elemental reactions is generally unfavorable for meta compositions.

*   **Overload (Pyro + Electro):** Overload deals significant AoE Electro damage and knocks back smaller enemies. If Burning is active, the Electro damage from Overload can trigger Burning again, but the knockback often disrupts the continuous nature of Burning.
*   **Vaporize (Pyro + Hydro):** Vaporize is a damage-multiplication reaction that significantly boosts Pyro damage. If Burning is active and a Hydro character applies Hydro, Vaporize will trigger on the initial Pyro hit, but the subsequent Burning DoT will not benefit from Vaporize's multiplier. Furthermore, the Hydro application will consume the Pyro aura, potentially stopping the Burning DoT until another Pyro source reapplies it.
*   **Melt (Pyro + Cryo):** Similar to Vaporize, Melt is a damage-multiplication reaction. If Burning is active and a Cryo character applies Cryo, Melt will trigger on the initial Pyro hit, but the Burning DoT will not benefit. The Cryo application will consume the Pyro aura, interrupting Burning.
*   **Burgeon (Dendro + Hydro + Pyro):** Burgeon involves creating Dendro Cores (from Bloom, Hydro + Dendro) and then triggering them with Pyro. While Burning can occur as a byproduct if Pyro is applied to an enemy with a Dendro aura before the Dendro Core is formed, Burgeon's primary damage comes from the explosion of the Dendro Core, not the continuous Burning DoT.
*   **Hyperbloom (Dendro + Hydro + Electro):** Hyperbloom involves Dendro Cores being struck by Electro, transforming them into Sprawling Shots. Burning has no direct interaction with Hyperbloom beyond potentially consuming Pyro auras that could be used for other reactions.
*   **Quicken/Aggravate/Spread (Dendro + Electro):** Quicken creates an Electro-charged state on enemies, which can then be amplified by Electro (Aggravate) or Dendro (Spread). If Burning is active, the Pyro application can consume the Dendro aura needed for Spread or the Electro aura needed for Aggravate, thus disrupting these reactions.

## Niche Applications and Team Compositions

Despite its generally unfavorable interactions with meta-defining reactions, Burning has found niche applications, particularly in teams that can leverage its continuous Pyro application or mitigate its drawbacks.

One of the most prominent intentional uses of Burning involves **Thoma**. Thoma's Elemental Burst, "Crimson Oyl," applies Pyro damage to enemies in an area around the active character. When combined with Dendro, this can continuously trigger Burning. Thoma's kit is designed around shields and his Burst's damage scaling with EM, making him a unique candidate for Burning-focused teams. A common strategy involves building Thoma with high EM and using him as an off-field Pyro applicator.

**Nahida** is another character who can facilitate Burning teams. Her Elemental Skill, "All Schemes to End," applies Dendro to enemies. If a Pyro character with sufficient EM and consistent Pyro application (like Thoma) is present, Burning can be sustained. These teams often aim to maximize the EM scaling of both the Dendro and Pyro applicators. For example, a team might consist of Nahida (for Dendro application and EM buff), Thoma (for Pyro application and EM scaling), and two other characters to provide buffs, debuffs, or utility. The goal is to have Thoma's Burning ticks deal significant damage, especially when built with high EM.

However, these Burning-centric teams are generally considered niche and often fall behind more established meta compositions in terms of overall damage output and consistency. The lack of critical damage scaling on Burning, its susceptibility to aura consumption, and the disruptive nature of other reactions make it difficult to optimize.

## Why Burning is Avoided in Meta Compositions

The primary reasons Burning is avoided in most meta compositions are:

1.  **Lack of Critical Scaling:** Burning damage does not benefit from Critical Rate or Critical Damage. This means that characters built for critical hits will see their damage output significantly reduced when relying on Burning. Meta teams often revolve around maximizing critical damage through buffs and strong critical stats.
2.  **Low Base Damage Multiplier:** While EM and Level increase Burning damage, its base multipliers are relatively low compared to other reaction types like Vaporize, Melt, or the amplified damage from Aggravate and Spread.
3.  **Aura Consumption and Interruption:** Burning's continuous Pyro application can consume Dendro auras, preventing Spread reactions. Conversely, Hydro or Cryo applications can consume the Pyro aura, stopping Burning. This makes it difficult to maintain Burning alongside other powerful reactions that rely on specific aura management.
4.  **Enemy Knockback:** Reactions like Overload, which are often triggered in Pyro-heavy teams, can knock back smaller enemies, disrupting the continuous nature of Burning and requiring characters to reposition.
5.  **Terrain Ignition:** While sometimes useful, the uncontrolled ignition of terrain can lead to unintended consequences, such as burning the player's own characters or creating hazards that hinder combat.
6.  **Better Alternatives:** For Dendro-based teams, reactions like Bloom, Hyperbloom, Burgeon, Aggravate, and Spread offer significantly higher damage potential and more synergistic team-building options. For Pyro-focused teams, Vaporize and Melt provide substantial damage multipliers that are far more impactful than Burning.

In essence, Burning is a reaction that offers consistent, albeit relatively low, damage that does not scale with critical stats. While it has specific interactions with characters like Thoma and can be intentionally triggered, its drawbacks in terms of scaling, aura management, and synergy with other powerful reactions make it an unfavorable choice for most high-level, meta-defining team compositions in Genshin Impact. Its utility is limited to very specific scenarios where its continuous Pyro application can be leveraged without disrupting the core strategy of the team.