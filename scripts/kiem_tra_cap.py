"""Kiem tra doc lap do phu cap gia tri (pairwise) cua file case PICT.

Dung de tu xac nhan so lieu cua `pict <model> /s` ma khong tin vao PICT:
  1. Doc model (models/*.txt): tham so, gia tri, rang buoc dang
     IF [a] = "x" THEN [b] = "y";
  2. Liet ke toan bo to hop hop le (exhaustive) -> tap cap gia tri hop le.
  3. Doc file case (cases/*.tsv) -> tap cap gia tri da duoc phu.
  4. In: so to hop vet can, so cap can phu, so case, so cap bi sot.

Cach chay (thu muc goc repo):
    python scripts/kiem_tra_cap.py models/household.txt cases/household.tsv
    python scripts/kiem_tra_cap.py --all

Chi dung thu vien chuan. Ma thoat 0 neu phu 100% cap, 1 neu con cap bi sot.
Chay duoc voi file case do PICT sinh ra o bat ky bac nao (/o:2, /o:3).
"""
import argparse
import itertools
import re
import sys
from pathlib import Path

RULE = re.compile(
    r'IF\s+\[(\w+)\]\s*=\s*"([^"]*)"\s+THEN\s+\[(\w+)\]\s*=\s*"([^"]*)"\s*;',
    re.IGNORECASE,
)


def read_text(path):
    # PICT tren PowerShell cu co the ghi UTF-16; chap nhan ca hai.
    raw = Path(path).read_bytes()
    for enc in ("utf-8-sig", "utf-16"):
        try:
            return raw.decode(enc)
        except UnicodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def parse_model(path):
    text = read_text(path)
    params, rules = {}, []
    body = []
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        body.append(s)
    joined = "\n".join(body)
    for m in RULE.finditer(joined):
        rules.append(m.groups())
    joined = RULE.sub("", joined)
    for line in joined.splitlines():
        if ":" not in line:
            continue
        name, vals = line.split(":", 1)
        params[name.strip()] = [v.strip() for v in vals.split(",") if v.strip()]
    return params, rules


def valid_combo(combo, rules):
    return all(not (combo[a] == x and combo[b] != y) for a, x, b, y in rules)


def all_valid_combos(params, rules):
    names = list(params)
    for values in itertools.product(*(params[n] for n in names)):
        combo = dict(zip(names, values))
        if valid_combo(combo, rules):
            yield combo


def pairs_of(combo, names):
    for a, b in itertools.combinations(names, 2):
        yield (a, combo[a], b, combo[b])


def read_cases(path):
    lines = [l for l in read_text(path).splitlines() if l.strip()]
    header = lines[0].split("\t")
    return [dict(zip(header, l.split("\t"))) for l in lines[1:]]


def check(model_path, case_path, verbose=True):
    params, rules = parse_model(model_path)
    names = list(params)
    total, needed = 0, set()
    for combo in all_valid_combos(params, rules):
        total += 1
        needed.update(pairs_of(combo, names))
    cases = read_cases(case_path)
    covered, bad = set(), 0
    for c in cases:
        if set(c) != set(names) or not valid_combo(c, rules):
            bad += 1
        covered.update(pairs_of(c, names))
    missing = needed - covered
    if verbose:
        print(f"Model     : {model_path}")
        print(f"Case      : {case_path}")
        print(f"Tham so   : {len(names)}")
        print(f"Vet can   : {total} to hop hop le")
        print(f"Cap can phu: {len(needed)}")
        print(f"So case   : {len(cases)}  (case vi pham rang buoc/cot: {bad})")
        print(f"Cap bi sot: {len(missing)}")
        for m in sorted(missing)[:10]:
            print("   thieu:", m)
        pct = 100.0 * (len(needed) - len(missing)) / len(needed)
        print(f"Do phu cap: {pct:.1f}%\n")
    return not missing and bad == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model", nargs="?")
    ap.add_argument("cases", nargs="?")
    ap.add_argument("--all", action="store_true", help="kiem tra 4 model cua nhom")
    args = ap.parse_args()
    if args.all:
        root = Path(__file__).resolve().parent.parent
        ok = True
        for n in ("demo", "household", "search", "permissions"):
            ok &= check(root / "models" / f"{n}.txt", root / "cases" / f"{n}.tsv")
        sys.exit(0 if ok else 1)
    if not (args.model and args.cases):
        ap.error("can <model> <cases> hoac --all")
    sys.exit(0 if check(args.model, args.cases) else 1)


if __name__ == "__main__":
    main()
