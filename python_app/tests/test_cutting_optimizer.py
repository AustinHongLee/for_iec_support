from core.cutting_optimizer import CutPiece, optimize_cutting, optimize_from_summary
from core.material_summary import SummaryLine
from data.stock_lengths import KERF_WIDTH, LENGTH_TOLERANCE, STOCK_END_TRIM


def test_optimize_cutting_packs_valid_pieces_first_fit_decreasing():
    plan = optimize_cutting(
        [
            CutPiece(1000, source="A"),
            CutPiece(2500, source="B"),
            CutPiece(0, source="ignored"),
            CutPiece(2400, source="C"),
        ],
        stock_type="pipe",
    )

    assert plan.total_bars == 1
    assert plan.total_pieces == 3
    assert [piece.demand_length for piece in plan.bars[0].pieces] == [2500, 2400, 1000]
    assert plan.total_demand_length == 5900
    assert plan.bars[0].used_length == 5900 + 3 * (KERF_WIDTH + LENGTH_TOLERANCE)


def test_optimize_cutting_marks_overlength_piece_as_dedicated_bar():
    plan = optimize_cutting([CutPiece(7000, source="LONG")], stock_type="steel")

    assert plan.total_bars == 1
    assert plan.total_pieces == 1
    assert plan.bars[0].stock_length == 7000 + 2 * STOCK_END_TRIM + KERF_WIDTH
    assert plan.bars[0].effective_length == 7000 + KERF_WIDTH
    assert plan.bars[0].remnant == -LENGTH_TOLERANCE


def test_optimize_from_summary_keeps_material_identity_and_sources():
    line = SummaryLine(
        name="角鋼",
        spec="75*75*9",
        material="A36/SS400",
        aggregate_type="linear",
        piece_lengths=[(230, "DL-001 / S-001 03-4B-05 × 1組"), (130, "DL-001 / S-001 03-4B-05 × 1組")],
    )

    plan = optimize_from_summary(line)

    assert plan is not None
    assert plan.name == "角鋼"
    assert plan.spec == "75*75*9"
    assert plan.material == "A36/SS400"
    assert plan.total_pieces == 2
    assert [piece.source for piece in plan.bars[0].pieces] == [
        "DL-001 / S-001 03-4B-05 × 1組",
        "DL-001 / S-001 03-4B-05 × 1組",
    ]
