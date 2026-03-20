---
category: mechanics
topic: Elemental Gauge Theory
slug: gauge_theory
generated: 2026-03-20
---

# Elemental Gauge Theory

Elemental Gauge Theory governs how elemental applications interact with enemies and the environment in Genshin Impact. Each elemental application, whether from a character's Skill, Burst, or Normal Attack, possesses an invisible "Gauge Unit" (GU) value, representing its strength and duration. These values dictate how quickly an elemental aura on an enemy can be overwritten by an opposing element and influence the frequency of triggering elemental reactions like Vaporize and Melt.

## Gauge Unit Values and Aura Strength

Elemental applications are categorized by their GU values, most commonly falling into 1U, 2U, or 4U. A 1U application is the weakest and shortest-lasting, while 4U is the strongest and most persistent.

*   **1U Applications:** These are typically single, rapid hits or weaker elemental infusions. Examples include the initial hit of Xiangling's Pyronado (though subsequent ticks are 2U), Xingqiu's Rain Swords (each sword is 1U), and most standard Normal/Charged Attacks that apply an element.
*   **2U Applications:** These are more potent and longer-lasting. Examples include the elemental application from Bennett's Elemental Skill (tap version), Chongyun's Elemental Skill's infused Normal Attacks, and the continuous elemental application from Klee's Elemental Skill (Sparks 'n' Splash). The ticks of Xiangling's Pyronado are also 2U.
*   **4U Applications:** These are the strongest and most enduring applications. Examples include the initial application of a character's Elemental Burst that applies an element (e.g., Raiden Shogun's Burst initial slash), or certain sustained AoE effects.

The GU value directly correlates to the "strength" of the elemental aura applied to an enemy. A stronger aura requires more opposing elemental applications to be completely removed or overwritten. For instance, a 1U Pyro application might leave a weak Pyro aura that can be easily replaced by a single Hydro application. However, a 4U Pyro aura would require multiple Hydro applications to break through.

This interaction is crucial for maintaining elemental auras for reactions. If an enemy has a strong Hydro aura, a single 1U Pyro application might not be enough to enable a Vaporize reaction, as the Hydro aura will persist. Conversely, a strong Pyro aura might prevent a Hydro character from applying Hydro consistently enough to trigger Vaporize reliably.

## Elemental Aura Decay and Overwriting

Elemental auras on enemies decay over time. The rate of decay is influenced by the initial GU value of the application. Stronger auras (higher GU) decay slower, meaning they persist for a longer duration.

When an opposing element is applied to an enemy with an existing elemental aura, the game checks the combined GU values. The element with the higher total GU value "wins," overwriting the aura. If the GU values are equal, the aura of the element that was applied *last* takes precedence.

*   **Example:** An enemy has a 2U Hydro aura.
    *   A 1U Pyro application will not be enough to remove the Hydro aura. The Pyro application will be "consumed" by the Hydro, and the Hydro aura will remain, albeit slightly weakened.
    *   A 2U Pyro application might be enough to remove the Hydro aura, leaving a weak Pyro aura.
    *   A 4U Pyro application will easily remove the Hydro aura and leave a strong Pyro aura.

This mechanic is fundamental for setting up reactions. To consistently trigger Vaporize with a Pyro attacker and a Hydro enabler, the Hydro enabler must apply Hydro faster and/or with stronger GU values than the Pyro attacker can apply Pyro, or vice-versa if the Pyro attacker is the one triggering.

## Elemental Gauge and Reactions

The GU system directly impacts the frequency and reliability of elemental reactions, particularly transformative reactions like Vaporize and Melt.

### Vaporize and Melt

Vaporize (Hydro + Pyro) and Melt (Pyro + Cryo) are reactions that consume the existing elemental aura on the target. The damage bonus for these reactions is applied to the instance of damage that *triggers* the reaction.

*   **Stronger Application First:** If a stronger elemental application is applied first, it creates a more persistent aura. This can make it harder for subsequent weaker applications of the opposing element to trigger the reaction.
    *   **Example:** Applying a 4U Pyro aura first makes it difficult for a 1U Hydro application to trigger Vaporize. The 1U Hydro will likely be consumed without triggering a reaction, or only trigger a single, weak Vaporize if the Pyro aura is already decaying significantly.
*   **Weaker Application First:** Applying a weaker elemental application first creates a less persistent aura, making it easier for subsequent stronger applications of the opposing element to trigger the reaction.
    *   **Example:** Applying a 1U Hydro aura first makes it easier for a 4U Pyro application to trigger Vaporize. The 1U Hydro aura is quickly consumed, and the 4U Pyro application triggers a strong Vaporize.

**Proc Frequency:** The ability to trigger Vaporize or Melt consistently relies on maintaining an aura of the "triggering" element on the enemy.

*   **Triggering with Hydro (Vaporize):** If a Pyro character is triggering Vaporize, they need to apply Pyro to an enemy that has a Hydro aura. The Hydro enabler must apply Hydro frequently enough to maintain this aura. Characters like Xingqiu (multiple 1U Hydro applications from his Burst) or Kokomi (Hydro application from her Skill and Burst) are excellent for this. If the Hydro application is too weak or infrequent, the Pyro character might apply Pyro without a Hydro aura present, or the Hydro aura might decay before the Pyro character can trigger.
*   **Triggering with Pyro (Vaporize/Melt):** If a Hydro or Cryo character is triggering Vaporize or Melt, they need to apply their element to an enemy that has a Pyro aura. The Pyro applicator must apply Pyro frequently enough. Xiangling's Pyronado (2U ticks) or Klee's sustained Pyro applications can establish a strong Pyro aura for a Hydro or Cryo character to react with.

**Gauge Strength and Reaction Multiplier:** While the reaction damage bonus itself is fixed (1.5x for Vaporize/Melt when triggering element is stronger, 2x when triggered element is stronger), the *frequency* at which you can apply the triggering element is dictated by the gauge mechanics. A character applying 4U elements can maintain an aura for much longer than a character applying 1U elements, allowing for more reaction procs.

## Elemental Gauge and Freeze

Freeze is a unique reaction that relies on the combined strength of Cryo and Hydro applications. When Cryo is applied to an enemy with a Hydro aura, or Hydro to an enemy with a Cryo aura, the Freeze reaction is triggered. The duration of the Freeze effect is directly proportional to the *total* GU value of the opposing elements that contributed to the Freeze.

*   **Freeze Duration Formula:** The base duration of Freeze is influenced by the sum of the GU values of the last two elemental applications that caused the Freeze.
    *   If a 2U Cryo application hits an enemy with a 2U Hydro aura, the Freeze duration is based on 2U + 2U = 4U.
    *   If a 4U Cryo application hits an enemy with a 1U Hydro aura, the Freeze duration is based on 4U + 1U = 5U.

This means that using characters with stronger elemental applications (higher GU values) for both Cryo and Hydro can lead to significantly longer Freeze durations. For example, a team utilizing Shenhe's strong Cryo buffs and her Elemental Skill (which can apply Cryo) alongside a Hydro applicator with consistent, strong Hydro applications like Mona's Burst or Ayato's Burst can achieve very long Freeze durations. Conversely, relying on weak, 1U applications for both elements will result in very short Freeze durations, making the crowd control less effective.

## Character Application Strength and Team Building

Understanding GU values is critical for optimizing team compositions.

*   **Strong Applicators:** Characters like Xiangling (Pyronado's 2U ticks), Klee (sustained Pyro), Raiden Shogun (Burst initial slash 4U), Ayato (Burst 2U), and Ganyu (Charged Shot 2U) are excellent at establishing and maintaining elemental auras due to their higher GU values or rapid, multi-hit applications.
*   **Weak Applicators:** Characters like Amber (initial arrow 1U), Kaeya (Elemental Skill 1U), and some standard Normal Attacks apply elements with lower GU values. These are often better suited for triggering reactions themselves with a strong reaction multiplier or for applying a secondary element that doesn't need to persist for long.
*   **Multi-Hit Applications:** Characters whose skills or bursts apply elements multiple times in quick succession, even if each individual hit is 1U, can effectively "stack" GU values. Xingqiu's Rain Swords are a prime example: each sword applies 1U Hydro, but with three swords, he can apply 3U Hydro over a short period, which is often enough to maintain a Hydro aura for a Pyro trigger. However, the game treats these as separate applications, and the aura strength is determined by the *last* application. For sustained auras, continuous applications or higher GU single applications are generally superior.

**Team Building Implications:**

*   **Vaporize Teams:** To ensure consistent Vaporize, the Hydro enabler should ideally have stronger or more frequent Hydro applications than the Pyro trigger. Xingqiu is a top-tier Hydro enabler because his Burst provides multiple 1U Hydro applications that can be triggered by powerful Pyro DPS like Hu Tao or Diluc. If the Pyro DPS has weaker Pyro application (e.g., some Normal Attack-focused characters), a Hydro character with a stronger initial application like Mona's Burst might be preferred.
*   **Melt Teams:** Similar to Vaporize, the element that is *not* triggering Melt needs to maintain its aura. For a Cryo character to trigger Melt, a Pyro character needs to apply Pyro consistently. Xiangling's Pyronado is excellent for this, providing continuous 2U Pyro ticks that a Cryo DPS like Ganyu or Ayaka can react with.
*   **Freeze Teams:** To maximize Freeze duration, both the Cryo and Hydro applicators should ideally have higher GU values. Characters like Kazuha or Venti can group enemies, making it easier for AoE elemental applications to hit multiple targets and maintain auras.
*   **Elemental Resonance:** Understanding gauge is also important for elemental resonance. For example, the Pyro resonance requires two Pyro characters. If one Pyro character's application is weak and easily overwritten, the resonance might not be as effective.

**"Weak" vs. "Strong" Application:** It's important to distinguish between an element's inherent GU value and its overall effectiveness. A character might have a 1U application, but if they can apply it extremely rapidly and frequently (like Xingqiu's swords), they can still be a powerful enabler. Conversely, a character with a 4U application might only be able to apply it once every 20 seconds, limiting their utility for sustained reactions. The key is the *rate* and *strength* of aura application over time.

In summary, Elemental Gauge Theory is a foundational mechanic that dictates the persistence and strength of elemental auras. By understanding GU values, players can optimize their team compositions to ensure consistent elemental aura uptime, maximize reaction damage, and achieve desired crowd control effects like Freeze.