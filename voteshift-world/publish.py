"""Publicerar VS-WORLD: bygger webbdata och VoteShift-sidan och för över till GitHub-arkivet.

  python publish.py            bygg och kopiera, men committa inte (torrkörning)
  python publish.py --push     bygg, kopiera, committa och pusha till main

Bara voteshift.html och mappen voteshift-world/ ändras i arkivet. Låsfilerna kontrolleras mot sina hashar
innan något publiceras, och en befintlig låsfil i arkivet skrivs aldrig över med annat innehåll.
"""
import subprocess, shutil, sys, json, hashlib, datetime
from pathlib import Path

HERE = Path(__file__).resolve().parent
APP = HERE.parent / "14_FEWS-PF_app"
REPO = Path.home() / "FieldShift-github"
DEST = REPO / "voteshift-world"
sys.path.insert(0, str(HERE))
import vsworld as vs

def run(cmd, cwd):
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode: raise SystemExit(f"fel i {' '.join(cmd)}:\n{r.stdout}\n{r.stderr}")
    return r.stdout

def main(push):
    locks = sorted((HERE / "locks").glob("*.json")) if (HERE / "locks").exists() else []
    bad = [p.name for p in locks if not vs.verify(p)]
    if bad: raise SystemExit(f"låsfiler stämmer inte med sina hashar: {bad}")
    vs.site(HERE / "site_data.js")
    run([sys.executable, "build_voteshift.py"], APP)
    run([sys.executable, "build_fixes.py"], APP)
    if not (REPO / ".git").exists(): raise SystemExit(f"arkivet saknas: {REPO}")
    if push: run(["git", "pull", "-q", "--ff-only", "origin", "main"], REPO)
    for p in locks:
        target = DEST / "locks" / p.name
        if target.exists() and target.read_bytes() != p.read_bytes():
            raise SystemExit(f"låsfilen {p.name} finns redan i arkivet med annat innehåll; inget publiceras")
    DEST.mkdir(exist_ok=True)
    for name in ("vsworld.py", "publish.py", "README.md"):
        if (HERE / name).exists(): shutil.copy2(HERE / name, DEST / name)
    for sub in ("config", "data", "locks", "scores", "results"):
        if (HERE / sub).exists(): shutil.copytree(HERE / sub, DEST / sub, dirs_exist_ok=True)
    src = APP / "fieldshift_final_med_FEWS-PF" / "voteshift.html"
    b = src.read_bytes().replace(b"\r\n", b"\n")
    old = REPO / "voteshift.html"
    if old.exists() and b"\r\n" in old.read_bytes(): b = b.replace(b"\n", b"\r\n")
    old.write_bytes(b)
    status = run(["git", "status", "--porcelain", "--", "voteshift.html", "voteshift-world"], REPO)
    print(status or "inga ändringar")
    if push and status.strip():
        run(["git", "add", "voteshift.html", "voteshift-world"], REPO)
        msg = (f"VS-WORLD weekly update {datetime.date.today().isoformat()}: {len(locks)} locked forecasts\n\n"
               "Automatic run: calendar, locks due within 7 days, scores. Lock files are hash-checked.\n\n"
               "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>")
        run(["git", "commit", "-q", "-m", msg], REPO)
        run(["git", "push", "-q", "origin", "main"], REPO)
        print("pushat:", run(["git", "log", "--oneline", "-1"], REPO).strip())

if __name__ == "__main__":
    main("--push" in sys.argv)
