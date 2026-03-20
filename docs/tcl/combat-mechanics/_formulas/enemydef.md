<!-- Source: KQM Theorycrafting Library — docs\combat-mechanics\_formulas\enemydef.md -->
<!-- License: https://github.com/KQM-git/TCL/blob/master/LICENSE -->

$$
\text{EnemyDefMult} = \frac
  {\text{Level}_{\text{Character}} + 100}
  {(\text{Level}_{\text{Character}} + 100) + (\text{Level}_{\text{Enemy}} + 100) \times (1 - \text{DefReduction}) \times (1 - \text{DefIgnore})}
$$
