"""
Type 64 — Pipe-to-Pipe Rod Hanger
圖號: D-78
Supported line E: 1/2"~12"
H: 500~3000mm

E → rod size G
FIG-A~D → upper/lower clamp 組合
"""
from .component_size_utils import normalize_fractional_size

# E (supported line size) → rod size G
TYPE64_ROD_TABLE = {
    '1/2"':   {"g": '3/8"', "fig_bc_only": False},
    '3/4"':   {"g": '3/8"', "fig_bc_only": False},
    '1"':     {"g": '1/2"', "fig_bc_only": False},
    '1 1/4"': {"g": '1/2"', "fig_bc_only": False},
    '1 1/2"': {"g": '1/2"', "fig_bc_only": False},
    '2"':     {"g": '5/8"', "fig_bc_only": False},
    '2 1/2"': {"g": '5/8"', "fig_bc_only": False},
    '3"':     {"g": '5/8"', "fig_bc_only": False},
    '4"':     {"g": '3/4"', "fig_bc_only": False},
    '5"':     {"g": '3/4"', "fig_bc_only": True},
    '6"':     {"g": '3/4"', "fig_bc_only": True},
    '8"':     {"g": '7/8"', "fig_bc_only": True},
    '10"':    {"g": '1"', "fig_bc_only": True},
    '12"':    {"g": '1"', "fig_bc_only": True},
}

# FIG → upper/lower clamp type
# M-4 = TYPE-A Pipe Clamp (welded), M-6 = TYPE-C Pipe Clamp (bolted)
TYPE64_FIGURE_MAP = {
    "A": {"upper_clamp": "M-6 TYPE-C", "lower_clamp": "M-6 TYPE-C"},
    "B": {"upper_clamp": "M-6 TYPE-C", "lower_clamp": "M-4 TYPE-A"},
    "C": {"upper_clamp": "M-4 TYPE-A", "lower_clamp": "M-6 TYPE-C"},
    "D": {"upper_clamp": "M-4 TYPE-A", "lower_clamp": "M-4 TYPE-A"},
}

def get_type64_rod(supported_size: str) -> dict | None:
    """依 supported line size 查 rod size"""
    return TYPE64_ROD_TABLE.get(normalize_fractional_size(supported_size))


def get_type64_figure(fig: str) -> dict | None:
    """依 FIG 查 clamp 組合"""
    return TYPE64_FIGURE_MAP.get(fig.upper())


if __name__ == "__main__":
    print("Type 64 Rod Table:")
    for k, v in TYPE64_ROD_TABLE.items():
        bc = " (FIG-B/C only)" if v['fig_bc_only'] else ""
        print(f"  E={k:>7} → G={v['g']}{bc}")
    print("\nFigure Map:")
    for f, c in TYPE64_FIGURE_MAP.items():
        print(f"  FIG-{f}: upper={c['upper_clamp']}, lower={c['lower_clamp']}")
