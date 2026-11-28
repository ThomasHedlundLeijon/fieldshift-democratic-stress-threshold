"""VS-WORLD v1: VoteShift-prognoser för nationella val i hela världen (protokoll: config/protocol.json).

Kommandon:
  python vsworld.py forecast data/polls/<id>.json        skriv prognos (VoteShift/reserv, M0, M1, M2, M3) till stdout
  python vsworld.py lock data/polls/<id>.json            lås prognosen: locks/<id>.json med SHA-256 (kräver låsfönstret)
  python vsworld.py score locks/<id>.json data/outcomes/<id>.json   poängsätt mot officiellt utfall -> scores/<id>.json
  python vsworld.py board                                jämförelsetabell + regeln för 'bäst' -> results/board.json
  python vsworld.py site <out.js>                        bygg data till webbsidan

Indatafil för ett val (data/polls/<id>.json):
  {"id":"2027-04-11_FRA_presidential","country":"France","iso3":"FRA","office":"presidential","date":"2027-04-11",
   "threshold":null, "competitive":true,
   "parties":[{"id":"RN","name":"..."}],
   "previous":{"date":"2022-04-10","shares":{"RN":23.2,...}},
   "polls":[{"pollster":"Ifop","field_end":"2027-03-30","published":"2027-03-31","n":1200,"shares":{"RN":31,...}}],
   "markets":[{"source":"Polymarket","url":"...","captured_utc":"...","winner_probs":{"RN":0.55}}],
   "forecasters":[{"source":"...","url":"...","captured_utc":"...","winner_probs":{...},"shares":{...}}]}
Endast standardbiblioteket används.
"""
import json, sys, math, random, hashlib, datetime, statistics, os
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROTOCOL_SHA = json.loads((HERE / "config" / "protocol.lock").read_text(encoding="utf-8"))["sha256"]
DRAWS = 20000
SEED0 = 20261128

def d(s): return datetime.date.fromisoformat(s[:10])

def sigma_hist(p):  # p i procent
    return min(4.0, max(0.8, 2.5 * math.sqrt(max(p, 0.0) / 25.0)))

def lock_date(e):  # valdag minus 7 dagar
    return d(e["date"]) - datetime.timedelta(days=7)

def eligible(polls, cutoff, notes):
    out = []
    for p in polls:
        fe = d(p["field_end"])
        pub = d(p["published"]) if p.get("published") else fe + datetime.timedelta(days=1)
        if not p.get("published"): notes.add("publiceringsdatum saknas för vissa mätningar: fältperiodens slut + 1 dag används")
        if fe <= cutoff and pub <= cutoff: out.append(dict(p, _fe=fe))
    return out

def b2(polls, parties, cutoff):
    """PollEngine B2: tidsvikt, urvalsvikt, max 3 per institut, huseffekter. Returnerar (andelar, n_eff, använda, fönster)."""
    for window in (60, 180):
        use = [p for p in polls if (cutoff - p["_fe"]).days <= window]
        if len(use) >= 3: break
    else:
        return None
    use.sort(key=lambda p: p["_fe"], reverse=True)
    per, kept = {}, []
    for p in use:
        per.setdefault(p["pollster"], 0)
        if per[p["pollster"]] < 3: kept.append(p); per[p["pollster"]] += 1
    def w(p): return 0.5 ** ((cutoff - p["_fe"]).days / 14.0) * math.sqrt(min(p.get("n") or 1000, 3000))
    def avg(ps, j):
        ws = [(w(p), p["shares"].get(j)) for p in ps if p["shares"].get(j) is not None]
        return sum(a * b for a, b in ws) / sum(a for a, _ in ws) if ws else None
    ids = [q["id"] for q in parties]
    house = {}
    pollsters = sorted({p["pollster"] for p in kept})
    if len(pollsters) >= 2:
        for ps in pollsters:
            mine = [p for p in kept if p["pollster"] == ps]; others = [p for p in kept if p["pollster"] != ps]
            k = len(mine)
            for j in ids:
                a, b = avg(mine, j), avg(others, j)
                if a is not None and b is not None: house[(ps, j)] = k / (k + 5) * (a - b)
    est = {}
    for j in ids:
        ws = [(w(p), p["shares"][j] - house.get((p["pollster"], j), 0.0)) for p in kept if p["shares"].get(j) is not None]
        est[j] = sum(a * b for a, b in ws) / sum(a for a, _ in ws) if ws else 0.0
    tot = sum(max(v, 0) for v in est.values()) or 1.0
    est = {j: max(v, 0) * 100.0 / tot for j, v in est.items()}
    n_eff = sum(min(p.get("n") or 1000, 3000) for p in kept)
    return est, n_eff, kept, window

def simulate(shares, sig, seed, threshold=None):
    rnd = random.Random(seed); ids = list(shares)
    wins = {j: 0 for j in ids}; thr = {j: 0 for j in ids}; samples = {j: [] for j in ids}
    for _ in range(DRAWS):
        x = {j: max(0.0, rnd.gauss(shares[j], sig[j])) for j in ids}
        t = sum(x.values()) or 1.0
        x = {j: v * 100.0 / t for j, v in x.items()}
        wins[max(x, key=x.get)] += 1
        for j in ids:
            samples[j].append(x[j])
            if threshold is not None and x[j] >= threshold: thr[j] += 1
    q = lambda v, a: sorted(v)[int(a * (len(v) - 1))]
    out = {"shares": {j: round(shares[j], 2) for j in ids},
           "interval80": {j: [round(q(samples[j], .1), 2), round(q(samples[j], .9), 2)] for j in ids},
           "winner_probs": {j: round(wins[j] / DRAWS, 4) for j in ids}}
    if threshold is not None: out["threshold_probs"] = {j: round(thr[j] / DRAWS, 4) for j in ids}
    return out

def forecast(e, seed_index=0):
    notes = set(); cutoff = lock_date(e); ids = [q["id"] for q in e["parties"]]
    polls = eligible(e.get("polls", []), cutoff, notes)
    seed = SEED0 + seed_index; thr = e.get("threshold")
    prev = {j: float(e.get("previous", {}).get("shares", {}).get(j, 0.0)) for j in ids}
    res = {"id": e["id"], "country": e["country"], "iso3": e.get("iso3"), "office": e["office"], "date": e["date"],
           "lock_date": cutoff.isoformat(), "protocol_sha256": PROTOCOL_SHA, "competitive": e.get("competitive", True), "models": {}}
    b = b2(polls, e["parties"], cutoff)
    if b:
        est, n_eff, kept, window = b
        sig = {j: math.sqrt(est[j] * (100 - est[j]) / max(n_eff, 1) + sigma_hist(est[j]) ** 2) for j in ids}
        res["models"]["VoteShift"] = dict(simulate(est, sig, seed, thr), kind="polls", polls_used=len(kept), window_days=window)
        recent = [p for p in polls if (cutoff - p["_fe"]).days <= 14]
        if len(recent) < 3: recent = sorted(polls, key=lambda p: p["_fe"], reverse=True)[:5]
        m1 = {j: statistics.mean([p["shares"].get(j, 0.0) for p in recent]) for j in ids}
        t = sum(m1.values()) or 1.0; m1 = {j: v * 100 / t for j, v in m1.items()}
        sig1 = {j: math.sqrt(m1[j] * (100 - m1[j]) / max(n_eff, 1) + sigma_hist(m1[j]) ** 2) for j in ids}
        res["models"]["M1_poll_average"] = dict(simulate(m1, sig1, seed + 1, thr), polls_used=len(recent))
        res["group"] = "a" if res["competitive"] else "c"
    else:
        sigf = {j: 2 * sigma_hist(prev[j]) for j in ids}
        res["models"]["VoteShift"] = dict(simulate(prev, sigf, seed, thr), kind="fallback", label="reservmodell – inga mätningar")
        res["group"] = "b" if res["competitive"] else "c"
    sig0 = {j: 2 * sigma_hist(prev[j]) for j in ids}
    res["models"]["M0_previous"] = simulate(prev, sig0, seed + 2, thr)
    if e.get("markets"): res["models"]["M2_markets"] = e["markets"]
    if e.get("forecasters"): res["models"]["M3_forecasters"] = e["forecasters"]
    res["notes"] = sorted(notes)
    return res

def lock(path, now=None):
    e = json.loads(Path(path).read_text(encoding="utf-8"))
    now = now or datetime.datetime.now(datetime.timezone.utc)
    if now.date() >= d(e["date"]): raise SystemExit("för sent: valdagen har passerat")
    if (d(e["date"]) - now.date()).days < 1: raise SystemExit("för sent: mindre än 1 dag kvar (protokollet: ej låst i tid)")
    if now.date() < lock_date(e): raise SystemExit(f"för tidigt: låsning tidigast {lock_date(e)}")
    out = HERE / "locks" / f"{e['id']}.json"
    if out.exists(): raise SystemExit(f"redan låst: {out.name} (låsta prognoser ändras aldrig)")
    idx = int(hashlib.sha256(e["id"].encode()).hexdigest(), 16) % 100000
    f = forecast(e, idx); f["locked_utc"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    f["input_sha256"] = hashlib.sha256(Path(path).read_bytes()).hexdigest()
    body = json.dumps(f, ensure_ascii=False, indent=1, sort_keys=True)
    f2 = json.loads(body); f2["sha256"] = hashlib.sha256(body.encode("utf-8")).hexdigest()
    out.parent.mkdir(exist_ok=True); out.write_text(json.dumps(f2, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return out

def verify(lock_path):
    f = json.loads(Path(lock_path).read_text(encoding="utf-8")); h = f.pop("sha256")
    return h == hashlib.sha256(json.dumps(f, ensure_ascii=False, indent=1, sort_keys=True).encode("utf-8")).hexdigest()

def score_model(m, actual, winner, thr_hits):
    out = {}
    if "shares" in m:
        ids = [j for j in m["shares"] if j in actual]
        out["mae"] = round(statistics.mean(abs(m["shares"][j] - actual[j]) for j in ids), 3) if ids else None
    wp = m.get("winner_probs")
    if wp:
        allk = set(wp) | {winner}
        out["brier"] = round(sum((wp.get(k, 0.0) - (1.0 if k == winner else 0.0)) ** 2 for k in allk), 4)
        out["log"] = round(-math.log(max(wp.get(winner, 0.0), 0.001)), 4)
    if thr_hits is not None and m.get("threshold_probs"):
        out["threshold_brier"] = round(statistics.mean((m["threshold_probs"][j] - (1.0 if thr_hits[j] else 0.0)) ** 2 for j in thr_hits if j in m["threshold_probs"]), 4)
    return out

def score(lock_path, outcome_path):
    if not verify(lock_path): raise SystemExit("låsfilen stämmer inte med sin hash")
    f = json.loads(Path(lock_path).read_text(encoding="utf-8")); o = json.loads(Path(outcome_path).read_text(encoding="utf-8"))
    actual = {k: float(v) for k, v in o["shares"].items()}; winner = max(actual, key=actual.get)
    thr = o.get("threshold"); hits = {j: actual[j] >= thr for j in actual} if thr is not None else None
    res = {"id": f["id"], "group": f["group"], "winner": winner, "source": o.get("source"), "scored_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "models": {}}
    for name, m in f["models"].items():
        if name in ("M2_markets", "M3_forecasters"):
            for i, src in enumerate(m):
                res["models"][f"{name}:{src.get('source', i)}"] = score_model(src, actual, winner, hits)
        else:
            res["models"][name] = score_model(m, actual, winner, hits)
    out = HERE / "scores" / f"{f['id']}.json"; out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    return out

def board():
    sc = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((HERE / "scores").glob("*.json"))] if (HERE / "scores").exists() else []
    rows = {}
    for s in sc:
        for name, m in s["models"].items():
            r = rows.setdefault((s["group"], name), {"n": 0, "brier": [], "mae": [], "log": []})
            r["n"] += 1
            for k in ("brier", "mae", "log"):
                if m.get(k) is not None: r[k].append(m[k])
    table = [{"group": g, "model": n, "elections": r["n"], **{k: (round(statistics.mean(r[k]), 4) if r[k] else None) for k in ("brier", "mae", "log")}} for (g, n), r in sorted(rows.items())]
    # regeln för 'bäst' (protokollets claim_rule), grupp a
    verdict = {}
    a = [s for s in sc if s["group"] == "a"]
    for other in sorted({n for s in a for n in s["models"] if n != "VoteShift"}):
        common = [s for s in a if other in s["models"] and "VoteShift" in s["models"]]
        need = 15 if other.startswith(("M2", "M3")) else 30
        res = {"common_elections": len(common), "required": need}
        if len(a) >= 30 and len(common) >= need:
            def diffs(key): return [s["models"][other][key] - s["models"]["VoteShift"][key] for s in common if s["models"][other].get(key) is not None and s["models"]["VoteShift"].get(key) is not None]
            rnd = random.Random(SEED0); ok = True
            for key in ("brier", "mae"):
                dv = diffs(key)
                if not dv: ok = False; res[key] = None; continue
                boots = sorted(statistics.mean(rnd.choice(dv) for _ in dv) for _ in range(2000))
                lo, hi = boots[50], boots[1949]; res[key] = {"mean_advantage": round(statistics.mean(dv), 4), "ci95": [round(lo, 4), round(hi, 4)]}
                ok = ok and lo > 0
            res["verdict"] = "bättre" if ok else "inte visat"
        else:
            res["verdict"] = "för tidigt att avgöra"
        verdict[other] = res
    out = {"protocol_sha256": PROTOCOL_SHA, "scored_elections": len(sc), "group_a": len(a), "table": table, "vs_others": verdict}
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "board.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out

def site(out_js):
    cal = {}
    for p in sorted((HERE / "data").glob("calendar_*.json")):
        for e in json.loads(p.read_text(encoding="utf-8")).get("elections", []):
            cal[(e.get("iso3"), e.get("office"), e.get("date") or e.get("date_note"))] = e
    locks = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((HERE / "locks").glob("*.json"))] if (HERE / "locks").exists() else []
    scores = {json.loads(p.read_text(encoding="utf-8"))["id"]: json.loads(p.read_text(encoding="utf-8")) for p in sorted((HERE / "scores").glob("*.json"))} if (HERE / "scores").exists() else {}
    data = {"generated_utc": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"), "protocol_sha256": PROTOCOL_SHA,
            "calendar": sorted(cal.values(), key=lambda e: (e.get("date") or "9999", e.get("country", ""))),
            "locks": locks, "scores": scores, "board": board()}
    Path(out_js).write_text("window.VS_WORLD = " + json.dumps(data, ensure_ascii=False) + ";\n", encoding="utf-8")
    return out_js

if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    if cmd == "forecast": print(json.dumps(forecast(json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))), ensure_ascii=False, indent=1))
    elif cmd == "lock": print(lock(sys.argv[2]))
    elif cmd == "score": print(score(sys.argv[2], sys.argv[3]))
    elif cmd == "board": print(json.dumps(board(), ensure_ascii=False, indent=1))
    elif cmd == "site": print(site(sys.argv[2]))
    elif cmd == "verify": print(all(verify(p) for p in (HERE / "locks").glob("*.json")))
    else: print(__doc__)
