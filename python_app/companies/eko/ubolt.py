"""益高 U型螺栓(UB1)共用解析：依配管管徑給「實際規格」＋師傅叫料的直觀說法。

被 FS/PU/SS/VA 等父支撐引用時，不再只寫「詳 UB1-X"」，而是直接算出：
  幾分/幾寸(台灣水電俗稱) · 牙數(公制Mxx 及英制UNC) · 線徑φ · 展開長 · 重量。
資料源 configs/ub1.json(UB1.pdf 全 21 列)；重量=彎鋼棒近似(展開長≈πR+2H, 斷面 π/4·d1²)。
"""
import math
from core.bolt import add_custom_entry
from .config_loader import load_eko_config

_DENSITY = 7.85e-6  # kg/mm³

# 公制牙 → 英制 UNC(依 UB1.pdf 螺紋 d2 欄)
_UNC = {"M10": "3/8\"-16UNC", "M12": "1/2\"-13UNC", "M16": "5/8\"-11UNC",
        "M20": "3/4\"-10UNC", "M24": "1\"-8UNC", "M30": "1.1/4\"-8UNC", "M36": "1.3/8\"-8UNC"}

# 台灣水電叫料 分/寸 俗稱(依公稱管徑吋)
_FEN = {0.375: "3分", 0.5: "4分", 0.75: "6分", 1: "1寸", 1.25: "1寸2", 1.5: "1寸半",
        2: "2寸", 2.5: "2寸半", 3: "3寸", 3.5: "3寸半", 4: "4寸", 5: "5寸", 6: "6寸"}


def fen_label(size):
    """公稱管徑(吋) → 台灣叫料俗稱(4分/6分/1寸半…)；表外用『N吋』。"""
    if size in _FEN:
        return _FEN[size]
    try:
        f = float(size)
        return f"{int(f)}吋" if f.is_integer() else f"{f}吋"
    except (TypeError, ValueError):
        return f"{size}吋"


def _row_for(table, pipe):
    if pipe is None:
        return None
    exact = [r for r in table if abs(r["size"] - pipe) < 1e-6]
    if exact:
        return exact[0]
    ge = [r for r in table if r["size"] >= pipe - 1e-6]
    return min(ge, key=lambda r: r["size"]) if ge else None


def lookup(pipe):
    """回傳 UB1 規格 dict(含師傅叫料欄位)；查不到→None。"""
    cfg = load_eko_config("UB1")
    if cfg is None:
        return None
    row = _row_for(cfg.get("table", []), pipe)
    if row is None:
        return None
    dev = round(math.pi * row["R"] + 2 * row["H"])          # 展開長 mm
    weight = round(math.pi / 4 * row["d1"] ** 2 * dev * _DENSITY, 3)
    thread = row["thread"]
    return {
        "label": row["label"], "fen": fen_label(row["size"]),
        "thread": thread, "unc": _UNC.get(thread, ""), "rod_dia": row["d1"],
        "developed_len": dev, "weight": weight,
        "R": row["R"], "H": row["H"], "P": row["P"], "E": row["E"],
        "material": cfg.get("material", "A307-B 鍍鋅"),
    }


def spec_text(sp):
    """BOM 規格欄：4分 M10(3/8"-16UNC) 1/2"管用。"""
    unc = f"({sp['unc']})" if sp["unc"] else ""
    return f"{sp['fen']} {sp['thread']}{unc} {sp['label']}管用"


def order_text(sp):
    """師傅叫料直觀說法。"""
    unc = f"({sp['unc']})" if sp["unc"] else ""
    return (f"叫料：{sp['fen']}({sp['label']})U型螺栓/U型管夾，{sp['thread']}牙{unc}，"
            f"線徑φ{sp['rod_dia']}mm，展開長約{sp['developed_len']}mm"
            f"（腳長H{sp['H']}、內寬P{sp['P']}、牙長E{sp['E']}）；材質{sp['material']}")


def add_ubolt(result, pipe, qty=1, extra_note="", material=None, name="U型螺栓"):
    """加一筆『實際』U型螺栓(含重量＋師傅叫料說法)。查不到管徑→退回參照(不硬錯)，回 False。"""
    sp = lookup(pipe)
    if sp is None:
        ref = "詳 UB1" + (f"-{pipe}\"" if pipe is not None else "")
        add_custom_entry(result, name, ref, material or "A307-B 鍍鋅", qty, 0.0, unit="PC",
                         remark="; ".join(x for x in [extra_note, "管徑不在UB1表(3/8\"~24\")，重量另計"] if x),
                         category="螺栓類")
        return False
    remark = order_text(sp) + (f"；{extra_note}" if extra_note else "")
    add_custom_entry(result, name, spec_text(sp), material or sp["material"], qty,
                     sp["weight"], unit="PC", remark=remark, category="螺栓類")
    return True
