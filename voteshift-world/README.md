# VS-WORLD: VoteShift för nationella val i hela världen

**Status:** prospektiv studie från 2026-11-28. Varje prognos låses och publiceras före valdagen och poängsätts mot det officiella resultatet. Protokollet `config/protocol.json` är låst med SHA-256 i `config/protocol.lock`.

## Hur det fungerar
1. **Kalender:** `data/calendar_*.json` innehåller alla nationella parlaments- och presidentval med källor. Den uppdateras varje vecka.
2. **Underlag:** för varje val som ska låsas samlas mätningar, föregående resultat, prediktionsmarknader och publicerade prognoser i `data/polls/<id>.json`. Bara mätningar med fältperiodens slut senast låsdagen (valdagen minus 7 dagar) används.
3. **Låsning:** `python vsworld.py lock data/polls/<id>.json` skriver `locks/<id>.json` med SHA-256. Låsning är möjlig från valdagen minus 7 dagar till dagen före valet, och en låst prognos kan aldrig skrivas över.
4. **Publicering:** `python publish.py --push` lägger låsfilerna i GitHub-arkivet (`voteshift-world/locks/`). Committidpunkten är det offentliga beviset på att prognosen fanns före valet.
5. **Poängsättning:** när det officiella resultatet finns skrivs det till `data/outcomes/<id>.json`, och `python vsworld.py score locks/<id>.json data/outcomes/<id>.json` skriver `scores/<id>.json`.
6. **Jämförelse:** `python vsworld.py board` räknar fram tabellen och tillämpar protokollets regel för när VoteShift får kallas bättre.

## Modeller
| Modell | Innehåll |
|---|---|
| VoteShift | PollEngine B2 (tidsvikt, urvalsvikt, max 3 mätningar per institut, huseffekter) och 20 000 simuleringar |
| VoteShift reserv | Används när mätningar saknas: föregående resultat med dubbel osäkerhet, märkt och poängsatt separat |
| M0 | Föregående valresultat |
| M1 | Enkelt snitt av mätningar de sista 14 dagarna |
| M2 | Prediktionsmarknadens pris vid låsningen (bara vinnaren) |
| M3 | Publicerade prognoser vid låsningen |

## När får VoteShift kallas bäst?
Mot en jämförelsemodell gäller följande krav:
- Minst 30 poängsatta val med mätningar.
- Lägre medel-Brier för vinnaren och lägre medelfel för röstandelarna.
- Ett 95 %-intervall som utesluter noll i en parad bootstrap.
- Mot marknader och prognosmakare jämförs bara gemensamma val, och det krävs minst 15 sådana.

Innan dess visar sidan "för tidigt att avgöra".

## Automatisk körning
En schemalagd uppgift i Claude-appen (`voteshift-world-weekly`) kör varje måndag kl. 06.00. Om appen är stängd körs uppgiften när den startas nästa gång. Varje körning gör fyra saker:
- uppdaterar kalendern;
- låser de val vars låsfönster är öppet;
- poängsätter val där det officiella resultatet finns;
- publicerar.

**Rättvisa:** körningen kan ske upp till sex dagar efter låsdagen. VoteShift får ändå bara använda mätningar till och med låsdagen, medan marknader och prognosmakare hämtas vid körningen. Det är en nackdel för VoteShift och kan inte gynna modellen.

## Filer
| Fil | Innehåll |
|---|---|
| `vsworld.py` | Motor: prognos, låsning, poängsättning, jämförelse, webbdata (bara standardbiblioteket) |
| `publish.py` | Bygger sidan och publicerar till GitHub |
| `config/` | Låst protokoll |
| `data/` | Kalender, underlag per val, utfall |
| `locks/`, `scores/`, `results/` | Låsta prognoser, poäng, jämförelsetabell |
