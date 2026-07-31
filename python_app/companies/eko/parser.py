"""益高編號解析器（泛用）。

seg1 = 代碼 + 選用修飾字母，其餘段以尾碼/型式分類。範例：
  FS12W-2-1300H-400L → code=FS12, mods=W(=fix), serial=2, H=1300, L=400
  CM1E-300H-4"       → code=CM1,  mods=E,        H=300, pipe=4.0
  EB2-M16-125L-U     → code=EB2,  msize=16, L=125, flags=['U']
  S1-6"-100H         → code=S1,   pipe=6.0, H=100
  DFS4E-1-500H       → code=DFS4, mods=E(=fix), serial=1, H=500

尺寸皆字面 mm（與 IEC Type 的 ×100 不同）。管徑段帶尾碼 " (吋)，可含分數(1.1/2")。
段落順序不拘；以尾碼/型式判定。code 由 seg1 的『字母+數字』組成，尾隨字母為修飾(固定方式/型式)。
"""
import re

_SEG1_RE = re.compile(r"^([A-Za-z]+)(\d*)([A-Za-z]*)$")

# 無字母(純位置)編號的欄位填入順序：第1個裸數字=序號，其後依序填未設定的維度。
# 依各代號文法圖；預設 FS12 風格(序號→L→H→H1)。未列代號用 _DEFAULT_ORDER。
_POSITIONAL_ORDER = {
    "FS12": ["L", "H", "H1"],
}
_DEFAULT_ORDER = ["L", "H", "H1"]


def parse_inch(token):
    """'6"'->6.0, '1.1/2\"'->1.5, '3/4\"'->0.75, '2.1/2'->2.5。無法解析回 None。"""
    s = str(token).replace('"', "").replace("'", "").strip()
    if not s:
        return None
    try:
        if "." in s and "/" in s:                 # 混合分數 1.1/2
            whole, frac = s.split(".", 1)
            num, den = frac.split("/")
            return int(whole) + int(num) / int(den)
        if "/" in s:                                # 純分數 3/4
            num, den = s.split("/")
            return int(num) / int(den)
        return float(s)
    except (ValueError, ZeroDivisionError):
        return None


def parse_designation(fullstring, code=None):
    raw = (fullstring or "").strip()
    parts = [p.strip() for p in raw.split("-") if p.strip() != ""]
    seg1 = parts[0] if parts else ""

    mods = ""
    if code and seg1.upper().startswith(code.upper()):
        detected = code.upper()
        mods = seg1[len(code):].upper()
    else:
        m = _SEG1_RE.match(seg1)
        if m:
            detected = (m.group(1) + m.group(2)).upper()
            mods = m.group(3).upper()
        else:
            detected = seg1.upper()

    parsed = {
        "raw": raw, "code": detected, "mods": mods, "fix": mods,
        "serial": None, "pipe": None,
        "L": None, "L1": None, "H": None, "H1": None, "H2": None,
        "cold": None, "msize": None, "tcount": None,
        "flags": [], "extra": [], "duplicates": [], "L_list": [], "parse_warnings": [],
    }

    def assign(field, value):
        if parsed.get(field) is not None:
            parsed["duplicates"].append(field)
        parsed[field] = value

    bare_ints = []          # 無字母裸數字(位置備援用)
    for s in parts[1:]:
        u = s.upper()
        m = re.fullmatch(r"(\d+)H1", u)
        if m: assign("H1", int(m.group(1))); continue
        m = re.fullmatch(r"(\d+)H2", u)
        if m: assign("H2", int(m.group(1))); continue
        m = re.fullmatch(r"(\d+)H", u)
        if m: assign("H", int(m.group(1))); continue
        m = re.fullmatch(r"(\d+)L1", u)
        if m: assign("L1", int(m.group(1))); continue
        m = re.fullmatch(r"(\d+)L", u)
        if m:
            assign("L", int(m.group(1)))
            parsed["L_list"].append(int(m.group(1)))
            continue
        m = re.fullmatch(r"C(\d+)", u)
        if m: assign("cold", int(m.group(1))); continue
        m = re.fullmatch(r"M(\d+)", u)
        if m: assign("msize", int(m.group(1))); continue
        m = re.fullmatch(r"T(\d+)", u)
        if m: assign("tcount", int(m.group(1))); continue
        if s.endswith('"'):
            val = parse_inch(s)
            if val is not None:
                assign("pipe", val); continue
        if re.fullmatch(r"\d+", s):
            bare_ints.append(int(s)); continue
        if re.fullmatch(r"[A-Za-z]\d*", s):
            parsed["flags"].append(u); continue
        parsed["extra"].append(s)

    # ── 裸數字處理：字母優先(上面已解析)，剩下的裸數字才做位置備援 ──
    # 第1個裸數字 = 序號；其後依代號文法順序填「尚未設定」的維度(L/H/H1…)，並警告。
    if bare_ints:
        parsed["serial"] = bare_ints[0]
        extra = bare_ints[1:]
        if extra:
            order = _POSITIONAL_ORDER.get(detected, _DEFAULT_ORDER)
            filled, idx = [], 0
            for val in extra:
                while idx < len(order) and parsed[order[idx]] is not None:
                    idx += 1
                if idx < len(order):
                    parsed[order[idx]] = val
                    filled.append(f"{order[idx]}={val}")
                    idx += 1
                else:
                    parsed["extra"].append(str(val))
            if filled:
                parsed["parse_warnings"].append(
                    f"編號含無字母數字，依文法位置推定 {', '.join(filled)}"
                    f"(序號={bare_ints[0]})；如順序不符請改用帶字母寫法(例 400L-1300H)")
    return parsed
