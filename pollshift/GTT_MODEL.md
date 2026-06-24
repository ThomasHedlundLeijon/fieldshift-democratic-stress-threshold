# Geometric Threshold Theory (GTT) — Modellbeskrivning

## Teoretisk grund

GTT modellerar valsystemet som ett **strukturellt tröskelssystem**.

Kärntanken: nära en kritisk tröskel kan små förändringar i opinionsläget orsaka stora utfallsförändringar. GTT kvantifierar detta strukturellt.

---

## Politisk tillståndsvektor

```
P_t = [S, V, C, MP, M, SD, KD, L]
```

Varje komponent är ett partis estimerade röstandel vid tidpunkt t.

**Normalisering:** Summan av partierna normaliseras till 100%.

---

## Blockstruktur

```
Vänsterblock L_t = S_t + V_t + C_t + MP_t
Högerblock   R_t = M_t + SD_t + KD_t + L_t

Blockmarginal B_t = R_t − L_t
```

- B_t > 0: högerblockets fördel
- B_t < 0: vänsterblockets fördel
- B_t ≈ 0: strukturell jämvikt (tröskelzon)

---

## PSI — Pressure Sensitivity Index

```
PSI_t = clip(0.5 + B_t / K, 0, 1)
```

K är en kalibreringskonstant estimerad från historiska val.

| PSI | Tolkning |
|-----|----------|
| < 0.5 | Vänster strukturell fördel |
| ≈ 0.5 | Tröskelzon |
| > 0.5 | Höger strukturell fördel |

---

## Tröskelzoner

| Zon | PSI-intervall |
|-----|--------------|
| Vänster stabil | < 0.42 |
| Vänster lutar | 0.42–0.48 |
| Tröskelzon | 0.48–0.52 |
| Höger lutar | 0.52–0.58 |
| Höger stabil | > 0.58 |

Trösklarna är kalibrerade från historiska val och kan uppdateras.

---

## Tröskelkänslighet

```
sensitivity = 1 / (ε + |B_t|)
```

Högt värde → valet är mer känsligt för små förändringar nära tröskeln.

---

## Övergångsrisk

Sammansatt poäng [0, 1] baserad på:
- Avstånd till tröskel (40%)
- Strukturell volatilitet (25%)
- Momentumriktning (20%)
- Tid till val (15%)

---

## Kalibrering

K estimeras från historiska val:

```
K = B_election / (PSI_empirical − 0.5)
```

Om historisk data saknas används standardvärde K = 20.
