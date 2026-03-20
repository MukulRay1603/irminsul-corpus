---
category: reactions
topic: Quicken, Aggravate, and Spread
slug: quicken_aggravate_spread
generated: 2026-03-20
---

## Quicken, Aggravate, and Spread

The Quicken reaction forms the foundational interaction between Dendro and Electro elements, establishing a unique damage amplification system distinct from transformative or multiplicative reactions. Unlike Vaporize or Melt, Quicken itself does not deal direct damage upon application. Instead, it applies a persistent status effect, the "Quicken Aura," to an enemy, which then enables subsequent Electro or Dendro attacks to trigger enhanced damage reactions: Aggravate and Spread, respectively.

### Quicken Aura Mechanics

Quicken is triggered when Dendro and Electro elements react on an enemy. The primary effect is the application of the Quicken Aura, a status that lasts for a base duration of 10 seconds. This duration can be extended by the Elemental Mastery (EM) of the character who triggers the Quicken reaction. Crucially, the Quicken Aura is not consumed by subsequent applications of either Electro or Dendro, nor by the Aggravate or Spread reactions it enables. This non-consumption property is fundamental to the sustained damage model of these reactions, allowing for prolonged periods of enhanced damage output.

The Quicken Aura can coexist with other elemental auras, such as Hydro or Pyro, leading to more complex elemental interactions (e.g., Hyperbloom or Burgeon can still occur if Hydro or Pyro is applied to a Quickened enemy, consuming the Dendro or Electro aura respectively, but not the Quicken aura itself if it's considered a separate status). The internal cooldown (ICD) rules for applying Dendro or Electro still apply when attempting to trigger Quicken, meaning a character's abilities will only apply their element and trigger Quicken at specific intervals.

### Aggravate: Electro Damage Amplification

Aggravate is a damage-amplifying reaction triggered when an Electro attack hits an enemy currently affected by the Quicken Aura. This reaction *increases the damage of that specific Electro hit* by adding a flat damage bonus to the attack's base damage calculation.

The additive damage bonus from Aggravate is calculated using the following formula:
`Aggravate_Bonus = Level_Multiplier * (1 + (5 * EM / (EM + 1200))) * Aggravate_Reaction_Bonus`

*   **Level_Multiplier:** This value scales with the triggering character's level. At Level 90, this multiplier is approximately 1446.85.
*   **EM:** The Elemental Mastery of the character triggering the Aggravate reaction. Higher EM significantly increases the bonus.
*   **Aggravate_