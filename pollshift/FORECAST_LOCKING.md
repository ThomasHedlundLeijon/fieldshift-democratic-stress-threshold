# Prognosskyddning och hashkedja

## Syfte

Varje publik prognos låses med ett SHA-256-hashvärde före valdagen.
Detta gör det möjligt att i efterhand verifiera att prognosen inte modifierats.

## Vad som ingår i hashen

- forecast_id
- model_version, gtt_version, calibration_version
- election_id, timestamp
- party_shares (alla partiprocentenheter)
- left_pct, right_pct, block_margin
- PSI, zon, använda tröskelgränser
- predicted_winner, win_probability
- previous_forecast_hash (kedjelänk)

## Kryptografisk hashkedja

Varje prognos refererar till föregående prognosens hash.
Kedjan kan verifieras fullständigt bakåt till den första prognosen.

```
prognos_1: previous=NULL  → hash_1
prognos_2: previous=hash_1 → hash_2
prognos_3: previous=hash_2 → hash_3
```

Om någon prognos modifieras bryts kedjan och avvikelsen detekteras.

## Verifiering

```python
from audit.forecast_lock import ForecastLock
lock = ForecastLock()
result = lock.verify("forecast-id-här")
print(result["valid"])  # True/False
```

## Prognosstatus

| Status | Beskrivning |
|--------|-------------|
| draft | Internt utkast |
| internal | Intern granskning |
| locked | Låst, ej publik |
| public | Publik prognos |
| evaluated | Jämförd med faktiskt valresultat |
