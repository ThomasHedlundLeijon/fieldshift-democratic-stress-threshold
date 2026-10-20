# PollShift v15.0

**Vetenskapligt spårbar valprognos baserad på Geometric Threshold Theory.**

FieldShift Research Institute · Scientific Election Intelligence

---

## Kom igång

```bash
pip install -r requirements.txt
streamlit run app.py
```

### Driftlägen

```bash
POLLSHIFT_MODE=demo    streamlit run app.py   # Syntetisk demodata (standard)
POLLSHIFT_MODE=internal streamlit run app.py  # Experimentell diagnostik
POLLSHIFT_MODE=public   streamlit run app.py  # Publik produktion
```

---

## Arkitektur

```
pollshift/
  app.py                   Streamlit-applikation
  config.py                Konfiguration och konstanter
  gtt/                     Geometric Threshold Theory
    state_vector.py        Politisk tillståndsvektor P_t
    psi.py                 Pressure Sensitivity Index
    zones.py               GTT-zonklassificering
    thresholds.py          Kalibrerade tröskelgränser
    transition_risk.py     Övergångsriskpoäng
    diagnostics.py         GTT-diagnostikmodul
  models/
    forecast_engine.py     GTT-prognosmotor
    mandate_model.py       Mandatberäkning (förenklad)
    calibration.py         Historisk kalibrering och MAE
    uncertainty.py         Osäkerhetsintervall
    scenario_engine.py     Deterministisk scenarioanalys
  data/
    collector.py           Datainsamling och aggregering
    validation.py          Indatavalidering
    quality.py             Datakvalitetsbedömning
    historical_loader.py   Historiska valresultat
  audit/
    forecast_lock.py       Prognosskyddning med SHA-256
    hash_chain.py          Kryptografisk hashkedja
    snapshot.py            Dataögonblicksbilder
    backtest_registry.py   Backtestregister
  ui/
    components.py          Streamlit-komponenter
    charts.py              Plotly-diagram
    transparency.py        Metod- och begränsningssida
  tests/                   37 automatiserade tester
```

---

## Tester

```bash
python -m pytest tests/ -v
```

---

## Vetenskapliga krav

- MAE visas **endast** när den är empiriskt beräknad från backtests
- Vinstsannolikhet visas **endast** när kalibrering finns
- Prognoser låses med SHA-256-hashvärden
- Kryptografisk hashkedja möjliggör granskning
- Inga slumpmässiga prognoser — all osäkerhet är deterministisk och källbetecknad
