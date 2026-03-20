---
category: characters
topic: Nahida
slug: nahida
generated: 2026-03-20
---

# Nahida

## Lore

Nahida, known as the Lesser Lord Kusanali, is the current Dendro Archon of Sumeru. For five centuries, she was confined to the Sanctuary of Surasthana, a gilded cage that prevented her from directly interacting with the world and its inhabitants. Despite her physical isolation, Nahida possessed an unparalleled connection to the Irminsul, the cosmic tree that records all knowledge and history of Teyvat. Through this connection, she could access the collective consciousness of humanity, observing their lives, dreams, and emotions. This unique perspective granted her profound emotional intelligence and a deep understanding of mortal desires and struggles, even as she was denied the very wisdom she was meant to embody.

Her existence as the God of Wisdom, yet deprived of true wisdom and experience, was a cruel irony. The Archon's confinement was a consequence of the forbidden knowledge surrounding the fall of the previous Dendro Archon and the subsequent destruction of the Akasha system. The Sages of Sumeru, fearing her potential influence and the secrets she might uncover, kept her isolated, feeding her curated information and limiting her access to the outside world. However, Nahida's innate curiosity and her connection to Irminsul allowed her to circumvent these restrictions, learning about the world and its people through their dreams and the vast repository of the Irminsul.

The cost of her eventual liberation and the restoration of true Dendro Archonship was immense, particularly concerning the erasure of the Fatui Harbinger Scaramouche from the Irminsul. When Nahida, with the aid of the Traveler and their companions, successfully rewrote history to remove Scaramouche's existence, the act had profound consequences. While it saved countless lives and prevented future suffering, it also meant that the memories of Scaramouche, and the events he caused, were wiped from the collective consciousness. This act of temporal manipulation, while necessary, represented a significant burden and a moral compromise for Nahida, highlighting the complex ethical dilemmas faced by deities. Her journey from a secluded, powerless figure to the benevolent God of Wisdom who actively guides her people is a testament to her resilience, her compassion, and her unwavering pursuit of truth and understanding. She learned to cherish the small joys and connections of mortal life, finding wisdom not just in grand knowledge but in the everyday experiences of her people.

## Kit Mechanics

Nahida's combat kit revolves around her ability to apply Dendro and amplify Elemental Reactions, making her an exceptional off-field support and a potent on-field driver.

### Elemental Skill: All Schemes to Know

**Press:** Nahida performs a single instance of Dendro DMG.
**Hold:** Nahida enters aiming mode, allowing her to select enemies within a certain range. When the hold ends, she marks up to 8 enemies with the **Seed of Skandha**. This mark lasts for 25 seconds.

When an active character within Nahida's party triggers an Elemental Reaction involving the Dendro element on an enemy afflicted by the Seed of Skandha, the following effects occur:
*   **Tri-Karma Purification:** The marked enemy takes Dendro DMG based on Nahida's ATK and Elemental Mastery (EM). This damage can trigger up to once every 0.2 seconds and can occur 3 times within a single instance of a reaction trigger. The damage instance is considered Elemental Skill DMG.
*   The damage multiplier for Tri-Karma Purification scales with Nahida's Elemental Mastery. At higher EM values, the damage dealt by Tri-Karma Purification increases significantly. This effect can be triggered by various Dendro-related reactions, including Bloom, Hyperbloom, Burgeon, Quicken, Aggravate, Spread, Burning, and Swirl (Dendro).

The damage of Tri-Karma Purification is calculated as follows:
`DMG = (Base DMG Multiplier) * (1 + EM Bonus) * (CRIT Rate Bonus) * (CRIT DMG Bonus) * (Elemental DMG Bonus) * (Enemy RES Reduction) * (Enemy DEF Multiplier)`

The EM Bonus component of the Tri-Karma Purification is derived from Nahida's Elemental Mastery. For every 100 EM Nahida possesses, the DMG dealt by Tri-Karma Purification increases by 0.1%. This bonus caps at 800 EM, providing a maximum of 0.8% increased DMG per 100 EM, or 6.4% increased DMG at 800 EM.

The cooldown for All Schemes to Know is 5 seconds.

### Elemental Burst: Illusory Heart

Nahida creates a **Shrine of Maya** field, dealing Dendro DMG to enemies within the area. This field lasts for 15 seconds.

The buffs provided by the Shrine of Maya depend on the Elemental Types of the characters in the party whose Elemental Skills are currently active within the field. The buffs are as follows:

*   **Pyro:** Increases the DMG dealt by Tri-Karma Purification by 20%. This effect can be triggered by having at least one Pyro character in the party.
*   **Electro:** Increases the CRIT Rate of Tri-Karma Purification by 12%. This effect can be triggered by having at least one Electro character in the party.
*   **Hydro:** Increases the duration of the Shrine of Maya field by 5 seconds. This effect can be triggered by having at least one Hydro character in the party.

These buffs are additive. For example, a party with Pyro, Electro, and Hydro characters will grant all three buffs: +20% Tri-Karma Purification DMG, +12% Tri-Karma Purification CRIT Rate, and +5 seconds to the Burst duration (total 20 seconds).

The maximum number of buffs Nahida can gain is 3. This means a party composition of Pyro, Electro, and Hydro characters will maximize the benefits of her Elemental Burst.

The Elemental Burst has an energy cost of 50 and a cooldown of 20 seconds.

Nahida's passive talents further enhance her kit:
*   **Awakening:** Increases the DMG dealt by Tri-Karma Purification and the Elemental Mastery bonus from Illusory Heart based on Nahida's Elemental Mastery.
    *   For every 1 point of Elemental Mastery Nahida has beyond 200, the DMG dealt by Tri-Karma Purification increases by 0.1%.
    *   For every 1 point of Elemental Mastery Nahida has beyond 200, the CRIT Rate of Tri-Karma Purification increases by 0.03%.
    *   These bonuses are capped at 800 EM. At 800 EM, Tri-Karma Purification DMG is increased by 60% (0.1% * 600 EM), and its CRIT Rate is increased by 18% (0.03% * 600 EM).
*   **Compassion:** When Illusory Heart is active, the Elemental Mastery of active characters within its field is increased based on Nahida's Elemental Mastery.
    *   The EM bonus is 0.03% of Nahida's EM for each point of EM she possesses.
    *   This bonus is capped at 800 EM, providing a maximum of 240 EM to party members.
    *   This effect is multiplicative with other EM buffs.
*   **Learn:** When using All Schemes to Know, if party members have Elemental types that can react with Dendro (Pyro, Hydro, Electro, Anemo, Geo, Cryo, Electro), Nahida gains the following buffs:
    *   Pyro: +30% DMG Bonus for Tri-Karma Purification.
    *   Electro: +20% ATK for Nahida.
    *   Hydro: +20% Burst DMG for Nahida.
    *   These buffs are independent of the Illusory Heart buffs and are applied based on the presence of specific elements in the active party.

## Builds

Nahida's build prioritizes Elemental Mastery and CRIT stats, with a strong emphasis on her supportive capabilities.

### Weapons

*   **Best-in-Slot (BiS):**
    *   **A Thousand Floating Dreams (5-star Catalyst):** This weapon is Nahida's signature and BiS. It provides a substantial amount of Elemental Mastery (substat) and its passive grants an Elemental Mastery bonus to the wielder and nearby party members based on their elemental types. The EM bonus is 0.03% of the wielder's EM for every 1 point of EM they possess, capped at 120 EM. Additionally, when party members' EM is 200 or more, their DMG is increased by 0.08% for every 1 point of EM they have above 200, capped at 0.24%. This synergizes perfectly with Nahida's kit and her role as an EM buffer.
*   **Strong F2P/4-star Options:**
    *   **Sacrificial Fragments (4-star Catalyst):** This weapon is an excellent F2P option. It offers a significant amount of Elemental Mastery as its substat. Its passive has a chance to reset the cooldown of Nahida's Elemental Skill, allowing for more frequent applications of Seed of Skandha and potentially more Tri-Karma Purification procs. This is particularly valuable for her off-field support role.
    *   **Wandering Evenstar (4-star Catalyst):** This event-exclusive weapon provides a substantial amount of Elemental Mastery and its passive grants an ATK bonus to the wielder based on their EM, which can then be converted into a DMG bonus for the party.
    *   **Mappa Mare (4-star Catalyst):** This craftable weapon provides Elemental Mastery as its substat. Its passive grants an Elemental DMG Bonus after triggering an Elemental Reaction, which is consistently active on Nahida.
*   **Competitive 3-star Option:**
    *   **Magic Guide (3-star Catalyst) R5:** At R5, Magic Guide provides a substantial amount of Elemental Mastery through its substat. Its passive grants increased DMG against enemies affected by Hydro or Electro, which can be situationally useful but is generally outclassed by higher rarity options. However, it's a viable budget choice for players who lack other EM catalysts.

### Artifacts

*   **4-piece Deepwood Memories:** This set is generally the best choice for Nahida when she is the primary Dendro applicator or when no other party member is consistently applying Dendro.
    *   **2-piece Bonus:** +15% Dendro DMG Bonus.
    *   **4-piece Bonus:** After hitting an enemy with an Elemental Skill or Burst, the opponent's Dendro RES is decreased by 30% for 8 seconds. This effect can be triggered even if Nahida is not on the field. This set is crucial for maximizing the damage of Dendro-based teams.
*   **4-piece Gilded Dreams:** This set is a strong option if Nahida is being used as an on-field DPS or if another party member is already equipped with 4-piece Deepwood Memories.
    *   **2-piece Bonus:** +80 Elemental Mastery.
    *   **4-piece Bonus:** Within 8 seconds of triggering an Elemental Reaction, the equipping character will gain buffs based on the Elemental Types of the other party members. ATK is increased by 14% for each party member whose Elemental Type is the same as the equipping character's, and Elemental Mastery is increased by 50 for each party member whose Elemental Type is different. This effect can be triggered once every 8 seconds. This set significantly boosts Nahida's personal damage and EM.

**Artifact Main Stats:**
*   **Sands:** Elemental Mastery (EM) is almost always the best choice due to her scaling.
*   **Goblet:** Elemental Mastery (EM) is generally preferred for maximum reaction damage and buffing capabilities. If Nahida is built as a primary on-field DPS and has very high EM from other sources, a Dendro DMG Bonus goblet can be considered, but EM is usually superior.
*   **Circlet:** CRIT Rate or CRIT DMG is preferred to maximize her personal damage output, especially with her passive talents.

**Artifact Substats Priority:**
1.  Elemental Mastery (until ~800-1000 EM)
2.  CRIT Rate
3.  CRIT DMG
4.  Energy Recharge (ER) - Aim for around 120-140% ER depending on team composition and weapon choice to ensure consistent Burst uptime.

## Top Team Compositions

Nahida excels in a variety of Dendro-based team compositions, significantly amplifying their damage output. Her role is typically as an off-field Dendro applicator and EM buffer.

*   **Hyperbloom Teams:** These teams focus on triggering the Hyperbloom reaction, which creates Sprawling Shots that deal Dendro DMG.
    *   **Core:** Nahida (Dendro), Hydro character (e.g., Xingqiu, Yelan), Electro character (e.g., Kuki Shinobu, Raiden Shogun - Electro).
    *   **Flex Slot:** Anemo character for Swirl (e.g., Kazuha, Sucrose) or another Dendro character for resonance and additional Dendro application.
    *   **Example:** Nahida, Xingqiu, Yelan, Kuki Shinobu. Nahida applies Dendro, Xingqiu and Yelan apply Hydro to create Dendro Cores, and Kuki Shinobu triggers Hyperbloom with Electro.
*   **Spread/Aggravate Teams:** These teams focus on amplifying the damage of Dendro and Electro attacks through the Spread and Aggravate reactions.
    *   **Core:** Nahida (Dendro), Electro character (e.g., Yae Miko, Fischl, Keqing - Electro DPS), Electro character or Anemo character.
    *   **Flex Slot:** An Anemo character for Swirl and RES shred (e.g., Kazuha, Sucrose), or another Electro character for resonance and consistent application. A second Dendro character can also be used for resonance.
    *   **Example:** Nahida, Yae Miko, Kazuha, Fischl. Nahida applies Dendro, Yae Miko and Fischl apply Electro, Kazuha groups enemies and buffs DMG, enabling Spread and Aggravate.
*   **Quickbloom Teams:** A hybrid of Hyperbloom and Spread/Aggravate, these teams aim to trigger both bloom-related reactions and Quicken reactions.
    *   **Core:** Nahida (Dendro), Hydro character (e.g., Xingqiu, Yelan), Electro character (e.g., Kuki Shinobu, Raiden Shogun - Electro).
    *   **Flex Slot:** An Electro character for consistent application and Aggravate, or an Anemo character for grouping and buffs.
    *   **Example:** Nahida, Xingqiu, Kuki Shinobu, Fischl. Nahida applies Dendro, Xingqiu applies Hydro, Kuki triggers Hyperbloom, and Fischl triggers Aggravate with her Electro application.
*   **Burgeon Teams:** These teams focus on triggering the Burgeon reaction, which causes Dendro Cores to explode after being hit by Pyro.
    *   **Core:** Nahida (Dendro), Hydro character (e.g., Xingqiu, Yelan), Pyro character (e.g., Thoma, Xiangling).
    *   **Flex Slot:** An Anemo character for grouping and Swirl, or another Hydro/Pyro character for resonance and application.
    *   **Example:** Nahida, Xingqiu, Thoma, Kazuha. Nahida applies Dendro, Xingqiu applies Hydro to create cores, Thoma applies Pyro to trigger Burgeon, and Kazuha groups enemies and buffs DMG.

Nahida's versatility allows her to fit into almost any team that utilizes the Dendro element, making her a highly valuable and sought-after character in the current meta. Her ability to provide consistent Dendro application, significant EM buffs, and personal damage makes her a cornerstone of many powerful team compositions.