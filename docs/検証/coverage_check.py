#!/usr/bin/env python3
"""Coverage Check (prototype): did every obligation in the SOP survive into the Blueprint?

Input : one Markdown page with  === SOP ===  /  === BLUEPRINT ===  /  === DISPOSITION ===  (optional)
Output: one Markdown file (coverage.md)

Standard library only: argparse, hashlib, re, sys, pathlib.
Not used on purpose: json, open(), re.compile(), unicodedata, decimal, eval, exec, subprocess, network, time, random.
"""
import argparse
import hashlib
import re
import sys
from pathlib import Path

DEFAULT_OUTPUT_NAME = "coverage.md"
# Report order: the clearest defects first, then the ones a human still has to judge, then the clean ones.
ORDER = ("MISSING", "WEAKENED", "EXCEPTION_LOST", "ROLE_MISMATCH", "VALUE_MISMATCH", "UNCLASSIFIED", "COVERED")
PRIORITY = ("ROLE_MISMATCH", "VALUE_MISMATCH", "WEAKENED", "EXCEPTION_LOST")

# ---------------------------------------------------------------------------
# text helpers
# ---------------------------------------------------------------------------
FULLWIDTH = dict((c, c - 0xFEE0) for c in range(0xFF01, 0xFF5F))
FULLWIDTH[0x3000] = 0x20
FULLWIDTH[0xFFE5] = 0xA5


def norm(text):
    return text.translate(FULLWIDTH)


def collapse(text):
    return re.sub(r"\s+", " ", text).strip()


def digest8(text):
    return hashlib.sha256(collapse(text).lower().encode("utf-8")).hexdigest()[:8]


def cell(text):
    return text.replace("|", "\\|")


def jstr(s):
    s = re.sub(r"[\x00-\x1f]", " ", s)
    return '"' + s.replace("\\", "\\\\").replace('"', '\\"') + '"'


# ---------------------------------------------------------------------------
# words: two rules only
#   1. lower-case, drop one trailing "s" (not "ss")
#   2. two words are the same word if their first 6 characters are the same
# Japanese: a run of kanji / katakana (length >= 2) is one word; no stemming.
# ---------------------------------------------------------------------------
STOP_WORDS = (
    "the and for with that this from are was were been being will would can could has have had its their any all "
    "each per into out not but than then when where which who whom whose how why what there here also such only "
    "more most less least other another same both either neither nor yet still just very much many some none one "
    "two after before during while within about above below over under between through against upon onto off "
    "step steps system systems process processes procedure procedures responsible responsibility complete "
    "completion apply applies applied use uses used using ensure ensures need needs should shall must may might "
    "require required requires according accordance following follow follows "
    "never prohibited forbidden allowed permitted cannot unless except otherwise every without whether because "
    "since until exceed exceeds exceeding greater fewer lower higher maximum minimum"
)
JP_STOP = ("場合", "必要", "以上", "以下", "未満", "以内", "以外", "例外", "事項", "内容")
JP_RUN = "[\u3400-\u4dbf\u4e00-\u9fff\u30a1-\u30fa\u30fc]+"


def key(word):
    w = word.lower()
    if len(w) > 3 and w.endswith("s") and not w.endswith("ss"):
        w = w[:-1]
    return w[:6]


STOP = set(key(w) for w in STOP_WORDS.split())


def word_keys(text):
    keys = set()
    for w in re.findall("[A-Za-z]+", text):
        if len(w) < 3:
            continue
        k = key(w)
        if k not in STOP:
            keys.add(k)
    for w in re.findall(JP_RUN, text):
        if len(w) >= 2 and w not in JP_STOP:
            keys.add(w[:6])
    return keys


# ---------------------------------------------------------------------------
# numbers: integer arithmetic only (values are scaled by 1000)
# fact = (comparator, unit, value)
# ---------------------------------------------------------------------------
NUM = r"\d[\d,]*(?:\.\d+)?"
MULT_EN = {"k": 1000, "thousand": 1000, "m": 1000000, "million": 1000000,
           "bn": 1000000000, "billion": 1000000000}
MULT_JP = {"千": 1000, "万": 10000, "億": 100000000}
CUR_PREFIX = {"us$": "USD", "$": "USD", "usd": "USD", "€": "EUR", "eur": "EUR",
              "£": "GBP", "gbp": "GBP", "¥": "JPY", "jpy": "JPY"}
SUFFIX_CUR = {"usd": "USD", "dollar": "USD", "dollars": "USD", "eur": "EUR", "euro": "EUR",
              "euros": "EUR", "gbp": "GBP", "jpy": "JPY", "yen": "JPY"}
TIME_EN = {"business day": "BDAY", "business days": "BDAY", "working day": "BDAY",
           "working days": "BDAY", "calendar day": "DAY", "calendar days": "DAY",
           "day": "DAY", "days": "DAY", "hour": "HOUR", "hours": "HOUR", "hr": "HOUR",
           "hrs": "HOUR", "week": "WEEK", "weeks": "WEEK", "month": "MONTH",
           "months": "MONTH", "year": "YEAR", "years": "YEAR"}
TIME_JP = {"営業日": "BDAY", "日間": "DAY", "日": "DAY", "時間": "HOUR", "週間": "WEEK",
           "週": "WEEK", "か月": "MONTH", "ヶ月": "MONTH", "ヵ月": "MONTH", "カ月": "MONTH",
           "年": "YEAR"}
CMP_BEFORE = sorted((
    ("at least", "GE"), ("no less than", "GE"), ("minimum of", "GE"),
    ("up to", "LE"), ("at most", "LE"), ("no more than", "LE"), ("maximum of", "LE"),
    ("not exceeding", "LE"), ("within", "LE"),
    ("more than", "GT"), ("greater than", "GT"), ("in excess of", "GT"), ("exceeding", "GT"),
    ("exceeds", "GT"), ("exceed", "GT"), ("above", "GT"), ("over", "GT"),
    ("less than", "LT"), ("fewer than", "LT"), ("lower than", "LT"), ("below", "LT"), ("under", "LT"),
), key=lambda x: -len(x[0]))
CMP_AFTER = sorted((
    ("or more", "GE"), ("or above", "GE"), ("and above", "GE"), ("and over", "GE"),
    ("or greater", "GE"), ("or higher", "GE"), ("以上", "GE"),
    ("or less", "LE"), ("or below", "LE"), ("or fewer", "LE"), ("and below", "LE"),
    ("or lower", "LE"), ("以下", "LE"), ("以内", "LE"),
    ("超", "GT"), ("未満", "LT"),
), key=lambda x: -len(x[0]))


def scaled(numstr, mult=1):
    s = numstr.replace(",", "")
    if "." in s:
        ip, fp = s.split(".", 1)
        v = int(ip or "0") * 1000 + int((fp + "000")[:3])
    else:
        v = int(s) * 1000
    return v * mult


def fmt_value(v):
    if v % 1000 == 0:
        return str(v // 1000)
    return ("%d.%03d" % (v // 1000, v % 1000)).rstrip("0")


def fact_str(f):
    return "%s %s %s" % (f[1], f[0], fmt_value(f[2]))


def compatible(c1, c2):
    """Same comparator, or one of them says nothing (EQ): e.g. 'within 2 days' and '2 days'."""
    return c1 == c2 or c1 == "EQ" or c2 == "EQ"


def comparator(low, s, e):
    ctx = low[max(0, s - 24):s]
    ctx = ctx.replace(">=", " at least ").replace("<=", " at most ")
    ctx = ctx.replace("≥", " at least ").replace("≤", " at most ")
    ctx = ctx.replace(">", " over ").replace("<", " under ")
    before = " " + collapse(re.sub(r"[^\w\s]", " ", ctx))
    for phrase, c in CMP_BEFORE:
        if before.endswith(" " + phrase):
            return c
    after = low[e:e + 14].lstrip()
    for phrase, c in CMP_AFTER:
        if after.startswith(phrase):
            return c
    return "EQ"


def numeric_facts(text):
    """Return (facts, text with the matched numbers blanked)."""
    low = text.lower()
    state = {"work": low}
    hits = []

    def sweep(rx, conv):
        found = []
        for m in re.finditer(rx, state["work"]):
            c = conv(m)
            if c is not None:
                found.append((m.start(), m.end(), c[0], c[1]))
        w = state["work"]
        for s, e, _unit, _val in found:
            w = w[:s] + " " * (e - s) + w[e:]
        state["work"] = w
        hits.extend(found)

    def years(m, table):
        v = scaled(m.group(1))
        if table[m.group(2)] == "YEAR" and v >= 1000000:
            return None  # 2026年 is a date, not a duration
        return (table[m.group(2)], v)

    sweep(r"(us\$|\$|usd|€|eur|£|gbp|¥|jpy)\s?(" + NUM + r")(?:\s?(thousand|million|billion|bn|k|m)\b)?",
          lambda m: (CUR_PREFIX[m.group(1)], scaled(m.group(2), MULT_EN.get(m.group(3) or "", 1))))
    sweep(r"(" + NUM + r")\s?(usd|eur|gbp|jpy|dollars?|euros?|yen)\b",
          lambda m: (SUFFIX_CUR[m.group(2)], scaled(m.group(1))))
    sweep(r"(" + NUM + r")\s?(万|千|億)?\s?円",
          lambda m: ("JPY", scaled(m.group(1), MULT_JP.get(m.group(2) or "", 1))))
    sweep(r"(" + NUM + r")\s?(?:%|percent\b|per cent\b)",
          lambda m: ("PCT", scaled(m.group(1))))
    sweep(r"(?<![\d.,])(" + NUM + r")\s?(business days?|working days?|calendar days?|days?|hours?|hrs?|weeks?|months?|years?)\b",
          lambda m: years(m, TIME_EN))
    sweep(r"(?<![\d.,月])(" + NUM + r")\s?(営業日|日間|日(?!本)|時間|週間|週|か月|ヶ月|ヵ月|カ月|年)",
          lambda m: years(m, TIME_JP))
    facts = []
    for s, e, unit, val in sorted(hits):
        facts.append((comparator(low, s, e), unit, val))
    return facts, state["work"]


# ---------------------------------------------------------------------------
# roles: dictionary, longest surface form first, the matched range is masked
# ---------------------------------------------------------------------------
ROLES = (
    ("DEPT_HEAD", ("department head", "head of department", "head of the department", "部門長")),
    ("CFO", ("cfo", "chief financial officer", "財務責任者")),
    ("FIN_DIR", ("finance director", "director of finance", "財務部長")),
    ("CONSULTANT", ("consultant", "コンサルタント")),
    ("REQUESTER", ("requester", "requestor", "employee", "起案者")),
    ("MANAGER", ("manager", "マネージャー", "上長")),
    ("PURCHASING", ("purchasing", "procurement", "購買")),
    ("FINANCE", ("finance", "経理", "財務")),
    ("RECEIVING", ("receiving", "warehouse", "受入")),
    ("SIGNATORY", ("authorised signatory", "authorized signatory", "signatory", "署名権者")),
)
ROLE_PATTERNS = sorted(((p, r) for r, ps in ROLES for p in ps), key=lambda x: -len(x[0]))


def role_scan(text):
    low = text.lower()
    found = set()
    for pat, role in ROLE_PATTERNS:
        if all(ord(c) < 128 for c in pat):
            rx = r"(?<![a-z])" + re.escape(pat) + r"s?(?![a-z])"
        else:
            rx = re.escape(pat)
        if re.search(rx, low):
            found.add(role)
            low = re.sub(rx, lambda m: " " * len(m.group(0)), low)
    return found


def analyse(text):
    t = norm(text)
    facts, work = numeric_facts(t)
    return {"text": collapse(text), "facts": facts, "roles": role_scan(work), "keys": word_keys(work)}


# ---------------------------------------------------------------------------
# page parsing
# ---------------------------------------------------------------------------
ELEMENTS = (
    ("Atomic Thinking Step Register", ("atomic thinking step register", "atomic thinking step", "atomic step")),
    ("Human-in-the-Loop Specification", ("human-in-the-loop specification", "human-in-the-loop", "hitl")),
    ("Agent Definition Register", ("agent definition register", "agent definition")),
    ("Data Products", ("data products", "data product")),
    ("Integration with Systems of Record", ("integration with systems of record", "systems of record")),
    ("MCP Tool Register", ("mcp tool register", "mcp tool")),
    ("Skills Library", ("skills library", "skill library")),
)
ALIASES = sorted(((a, name) for name, al in ELEMENTS for a in al), key=lambda x: -len(x[0]))


def element_label(heading):
    low = heading.lower()
    for alias, name in ALIASES:
        if alias in low:
            return name
    return None


def split_sentences(line):
    line = re.sub(r"([。！？])", r"\1\n", line)
    out = []
    for part in line.split("\n"):
        for p in re.split(r"(?<=[.!?])\s+", part):
            p = p.strip()
            if p:
                out.append(p)
    return out


BULLET = r"^(?:[-*•]|\d+[.)])\s+"
OBL_RX = (r"(?<![a-z])(must|shall|required?|requires|should|never|prohibited|forbidden|cannot|may not|"
          r"not allowed|not permitted)(?![a-z])|なければならない|ねばならない|してはならない|てはならない|必要がある|必須|禁止|義務")
EXC_RX = r"(?<![a-z])(?:unless|except|otherwise)(?![a-z])|ただし|例外"
MUST_RX = r"(?<![a-z])(must|shall|required?|requires)(?![a-z])|なければならない|ねばならない|必須"
WEAK_RX = r"(?<![a-z])(may|should|optional|optionally|recommended)(?![a-z])|推奨|任意|望ましい"
PROHIB_RX = (r"(?<![a-z])(must not|shall not|may not|cannot|never|prohibited|forbidden|not allowed|not permitted)(?![a-z])"
             r"|禁止|してはならない|てはならない|てはいけない|できない")
NEG_RX = (r"(?<![a-z])(not|cannot|never|prohibit\w*|forbid\w*|disallow\w*)(?![a-z])"
          r"|禁止|不可|できない|できません|てはいけ|てはなら|しない|行わない")


def split_exception(sentence):
    m = re.search(EXC_RX, sentence, re.I)
    if not m:
        return sentence, ""
    main = sentence[:m.start()].strip(" ;,、，。")
    exc = sentence[m.end():].strip(" ;,、，。.")
    if len(re.findall(r"\w", main)) < 3 or not exc:
        return sentence, ""
    return main, exc


def parse_sop(body):
    obligations, skipped = [], []
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        s = re.sub(BULLET, "", s)
        for sent in split_sentences(s):
            if re.search(OBL_RX, sent.lower()):
                obligations.append(sent)
            else:
                skipped.append(sent)
    return obligations, skipped


def parse_blueprint(body):
    units = []
    label = "(none)"
    lines = body.splitlines()
    i = 0
    while i < len(lines):
        s = lines[i].strip()
        i += 1
        if not s:
            continue
        hm = re.match(r"^#{1,6}\s+(.*)$", s)
        if hm:
            lab = element_label(hm.group(1))
            label = lab if lab else hm.group(1).strip()[:40]
            continue
        if s.startswith("|"):
            cells = [c.strip() for c in s.strip("|").split("|")]
            if all(re.fullmatch(r":?-{3,}:?", c) for c in cells if c):
                continue
            if i < len(lines) and re.match(r"^\s*\|?\s*:?-{3,}", lines[i]):
                continue  # header row
            text = " / ".join(c for c in cells if c)
            if text:
                units.append(dict(analyse(text), idx=len(units) + 1, label=label))
            continue
        s = re.sub(BULLET, "", s)
        for sent in split_sentences(s):
            if len(sent) >= 4:
                units.append(dict(analyse(sent), idx=len(units) + 1, label=label))
    return units


def parse_disposition(body):
    out = {}
    for raw in body.splitlines():
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        parts = [p.strip() for p in s.strip("|").split("|")]
        if len(parts) < 2 or not re.fullmatch(r"OB-\d{3,}-[0-9a-f]{8}", parts[0]):
            continue
        status = parts[1].upper()
        if status in ("WONTFIX", "REVIEWED"):
            out[parts[0]] = (status, " | ".join(parts[2:]))
    return out


def split_page(text):
    parts = re.split(r"^===\s*(SOP|BLUEPRINT|DISPOSITION)\s*===\s*$", text, flags=re.M)
    sections = {}
    for i in range(1, len(parts) - 1, 2):
        sections[parts[i]] = parts[i + 1]
    return sections


# ---------------------------------------------------------------------------
# matching and verdicts
# ---------------------------------------------------------------------------
def threshold(n):
    if n <= 1:
        return 1
    if n <= 6:
        return 2
    return 3


def effective(keys, generic):
    kept = set(k for k in keys if k not in generic)
    if kept:
        return kept
    return set(keys)


def score(S, ob, u):
    w = len(S & u["keys"])
    r = len(ob["roles"] & u["roles"])
    n = 0
    for (_c, unit, val) in ob["facts"]:
        if any(unit == f[1] and val == f[2] for f in u["facts"]):
            n += 1
    return (w, r, n)


def nearest(S, ob, units):
    best, best_key, best_score = None, None, None
    for u in units:
        sc = score(S, ob, u)
        k = (sc[0], sc[1], sc[2], -u["idx"])
        if best_key is None or k > best_key:
            best, best_key, best_score = u, k, sc
    return best, best_score


def kw(keys):
    return "[" + " ".join(sorted(keys)) + "]"


def value_check(facts, u, units, where):
    """Compare the numbers of an SOP sentence with the nearest statement; look elsewhere if it has none."""
    bad, notes = [], []
    for (c, unit, val) in facts:
        same = [f for f in u["facts"] if f[1] == unit]
        if same:
            if not any(f[2] == val and compatible(f[0], c) for f in same):
                bad.append("%sSOP %s vs Blueprint %s" % (where, fact_str((c, unit, val)),
                                                          " / ".join(fact_str(f) for f in same)))
        else:
            found = [x for x in units if any(f[1] == unit and f[2] == val and compatible(f[0], c)
                                             for f in x["facts"])]
            if found:
                notes.append("%sSOP %s is stated in U%02d, not in the nearest statement"
                             % (where, fact_str((c, unit, val)), found[0]["idx"]))
            else:
                bad.append("%sSOP %s appears nowhere in the Blueprint" % (where, fact_str((c, unit, val))))
    return bad, notes


def classify(ob, units, generic):
    main = ob["main"]
    S = effective(main["keys"], generic)
    info = {"S": S, "t": 0, "w": 0, "r": 0, "n": 0, "unit": None}
    if not S:
        info.update(verdict="UNCLASSIFIED", ev="no content word left after stop words and domain words")
        return info
    t = threshold(len(S))
    u, (w, r, n) = nearest(S, main, units)
    info.update(t=t, w=w, r=r, n=n, unit=u)
    core = "w=%d t=%d r=%d n=%d %s" % (w, t, r, n, kw(S))

    if w < t:
        if w == 0 and r == 0 and n == 0:
            info.update(verdict="MISSING", unit=None,
                        ev=core + "; no word, number or role in common with any Blueprint statement")
        else:
            info.update(verdict="UNCLASSIFIED",
                        ev=core + "; below the threshold, so the nearest statement is not accepted as the counterpart")
        return info

    hits = {}
    notes = []
    # ROLE_MISMATCH
    if main["roles"] and u["roles"] and not (main["roles"] & u["roles"]):
        hits["ROLE_MISMATCH"] = "SOP role %s vs Blueprint role %s" % (
            "+".join(sorted(main["roles"])), "+".join(sorted(u["roles"])))
    elif main["roles"] and not u["roles"]:
        absent = sorted(r for r in main["roles"] if not any(r in x["roles"] for x in units))
        if absent:
            hits["ROLE_MISMATCH"] = "SOP role %s appears nowhere in the Blueprint" % "+".join(absent)
    # VALUE_MISMATCH (main clause)
    bad, nts = value_check(main["facts"], u, units, "")
    notes.extend(nts)
    # exception clause: has its own counterpart?
    exc = ob["exc"]
    if exc:
        S2 = effective(exc["keys"], generic)
        if S2:
            t2 = threshold(len(S2))
            u2, (w2, _r2, _n2) = nearest(S2, exc, units)
            if w2 < t2:
                hits["EXCEPTION_LOST"] = 'exception clause "%s" has no counterpart (w=%d t=%d %s)' % (
                    exc["text"], w2, t2, kw(S2))
            else:
                bad2, nts2 = value_check(exc["facts"], u2, units, "exception clause: ")
                bad.extend(bad2)
                notes.extend(nts2)
    if bad:
        hits["VALUE_MISMATCH"] = "; ".join(bad)
    # WEAKENED
    sop = ob["sentence"].lower()
    ulow = u["text"].lower()
    if re.search(PROHIB_RX, sop) and not re.search(NEG_RX, ulow):
        hits["WEAKENED"] = "the SOP prohibits, the nearest statement has no negation"
    elif re.search(MUST_RX, sop) and not re.search(WEAK_RX, sop) and re.search(WEAK_RX, ulow):
        hits["WEAKENED"] = "the SOP is mandatory, the nearest statement is optional"

    ordered = [v for v in PRIORITY if v in hits]
    if ordered:
        first = ordered[0]
        ev = "%s; %s" % (core, hits[first])
        if len(ordered) > 1:
            ev += "; also " + "; ".join("%s (%s)" % (v, hits[v]) for v in ordered[1:])
        info.update(verdict=first, ev=ev, notes=notes)
        return info

    ev = core
    if main["roles"]:
        ev += "; role " + "+".join(sorted(main["roles"]))
    if main["facts"]:
        ev += "; " + ", ".join(fact_str(f) for f in main["facts"])
    if notes:
        ev += "; NOTE " + "; ".join(notes)
    info.update(verdict="COVERED", ev=ev, notes=notes)
    return info


def build(text, input_sha, debug=False):
    sections = split_page(text)
    head = ["# Coverage Check", "", "- input_sha256: %s" % input_sha]
    for need in ("SOP", "BLUEPRINT"):
        if need not in sections:
            return "\n".join(head + ["", "## UNPARSED", "",
                                     "- delimiter `=== %s ===` was not found; nothing was checked." % need, ""])
    sops, skipped = parse_sop(sections["SOP"])
    units = parse_blueprint(sections["BLUEPRINT"])
    if not sops:
        return "\n".join(head + ["", "## UNPARSED", "", "- no obligation sentence was found in the SOP.", ""])
    if not units:
        return "\n".join(head + ["", "## UNPARSED", "", "- no statement was found in the Blueprint.", ""])

    N = len(units)
    df = {}
    for u in units:
        for k in u["keys"]:
            df[k] = df.get(k, 0) + 1
    generic = set()
    if N >= 8:
        generic = set(k for k, c in df.items() if c >= 3 and c * 4 >= N)

    obs = []
    for i, sent in enumerate(sops, 1):
        main_text, exc_text = split_exception(sent)
        ob = {"seq": i, "sentence": sent, "id": "OB-%03d-%s" % (i, digest8(sent)),
              "main": analyse(main_text), "exc": analyse(exc_text) if exc_text else None}
        ob.update(classify(ob, units, generic))
        obs.append(ob)

    disp = parse_disposition(sections.get("DISPOSITION", ""))
    for o in obs:
        o["handled"] = o["id"] in disp and o["verdict"] != "COVERED"
    ids = set(o["id"] for o in obs)
    by_no = dict((o["id"].split("-")[1], o["id"]) for o in obs)
    stale = [(d, by_no.get(d.split("-")[1])) for d in sorted(disp) if d not in ids]

    total = len(obs)
    covered = sum(1 for o in obs if o["verdict"] == "COVERED")
    noted = sum(1 for o in obs if o["verdict"] == "COVERED" and o.get("notes"))
    pct = (covered * 100 + total // 2) // total

    out = list(head)
    out += ["- obligations extracted from the SOP: %d" % total,
            "- Blueprint statements: %d" % N,
            "- domain words ignored in the overlap (in 3+ statements and in 25%%+ of them): %s"
            % (kw(generic) if generic else ("none" if N >= 8 else "none (filter is off below 8 statements)")),
            ""]
    out += ["## Summary", "", "| Verdict | Count | Handled | Open |", "|---|---|---|---|"]
    for v in ORDER:
        c = sum(1 for o in obs if o["verdict"] == v)
        h = sum(1 for o in obs if o["verdict"] == v and o["handled"])
        out.append("| %s | %d | %s | %s |" % (v, c, "-" if v == "COVERED" else h, "-" if v == "COVERED" else c - h))
    out += ["",
            "- COVERED / obligations extracted: %d / %d (%d%%). A guide only: obligations the script could not "
            "extract are outside the denominator, and COVERED can still be wrong." % (covered, total, pct),
            "- COVERED but with an SOP number found only in another statement: %d (spot-check these first)" % noted, ""]
    out += ["## Findings", "", "| ID | Verdict | SOP | Nearest Blueprint statement | Evidence |", "|---|---|---|---|---|"]
    ordered = sorted(obs, key=lambda o: (ORDER.index(o["verdict"]), o["seq"]))
    for o in ordered:
        d = disp.get(o["id"])
        verdict = o["verdict"] + (" (%s%s)" % (d[0], ": " + d[1] if d[1] else "") if d and o["verdict"] != "COVERED" else "")
        if o["verdict"] == "MISSING" or o["unit"] is None:
            near = "(none)"
        else:
            u = o["unit"]
            near = "U%02d [%s] %s" % (u["idx"], u["label"], u["text"])
        out.append("| %s | %s | %s | %s | %s |" % (o["id"], cell(verdict), cell(o["sentence"]), cell(near), cell(o["ev"])))
    out.append("")
    extra = []
    for s in skipped:
        a = analyse(s)
        if a["facts"] or a["roles"]:
            extra.append(s)
    out += ["## Not extracted (no obligation word, but it carries a number or a role)", ""]
    out += (["- " + s for s in extra] if extra else ["- none"])
    out.append("")
    out += ["## Stale dispositions", ""]
    if stale:
        for did, cur in stale:
            out.append("- %s: %s" % (did, "the SOP text changed (now %s); this disposition is out of date" % cur
                                     if cur else "no such obligation"))
    else:
        out.append("- none")
    out.append("")
    rows = []
    for o in ordered:
        d = disp.get(o["id"])
        unit_id = "U%02d" % o["unit"]["idx"] if o["unit"] is not None else ""
        rows.append('{"id":%s,"verdict":%s,"unit":%s,"disposition":%s}' % (
            jstr(o["id"]), jstr(o["verdict"]), jstr(unit_id), jstr(d[0] if d and o["verdict"] != "COVERED" else "")))
    out += ["## Machine-readable result", "", "```json",
            '{"input_sha256":%s,"obligations":%d,"statements":%d,"results":[%s]}' % (
                jstr(input_sha), total, N, ",".join(rows)),
            "```", ""]
    if debug:
        sys.stderr.write("generic=%s N=%d\n" % (kw(generic), N))
        for u in units:
            sys.stderr.write("U%02d [%s] keys=%s roles=%s facts=%s\n" % (
                u["idx"], u["label"][:12], kw(u["keys"]), sorted(u["roles"]), [fact_str(f) for f in u["facts"]]))
        for o in obs:
            sys.stderr.write("%s %-15s S=%s t=%d w=%d r=%d n=%d unit=%s\n" % (
                o["id"], o["verdict"], kw(o["S"]), o["t"], o["w"], o["r"], o["n"],
                "U%02d" % o["unit"]["idx"] if o["unit"] is not None else "-"))
            sys.stderr.write("      keys=%s roles=%s facts=%s\n" % (
                kw(o["main"]["keys"]), sorted(o["main"]["roles"]), [fact_str(f) for f in o["main"]["facts"]]))
            if o["exc"]:
                sys.stderr.write("      exc keys=%s facts=%s\n" % (
                    kw(o["exc"]["keys"]), [fact_str(f) for f in o["exc"]["facts"]]))
    return "\n".join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description="SOP to Blueprint coverage check (prototype)")
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", default=DEFAULT_OUTPUT_NAME)
    ap.add_argument("--debug", action="store_true")
    args = ap.parse_args(argv)
    try:
        raw = Path(args.input).read_bytes()
    except OSError as exc:  # the page itself is unreadable: nothing to report on, so fail with one line
        sys.stderr.write("error: cannot read input %s (%s)\n" % (args.input, type(exc).__name__))
        return 1
    sha = hashlib.sha256(raw).hexdigest()
    text = raw.decode("utf-8", errors="replace")
    try:
        result = build(text, sha, args.debug)
    except Exception as exc:  # the page was readable, so report instead of failing
        result = "\n".join(["# Coverage Check", "", "- input_sha256: %s" % sha, "", "## UNPARSED", "",
                            "- internal error: %s" % type(exc).__name__, ""])
    Path(args.output).write_bytes(result.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
