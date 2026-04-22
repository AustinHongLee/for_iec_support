"""Default hardware material specification scaffold.

This table is inert in Phase 0B. It is not imported by existing Type
calculators and should be treated as review-required until the migration phase.
"""

from __future__ import annotations

from core.hardware_material import HardwareKind, ServiceClass


DEFAULT_HARDWARE_MATERIAL: dict[HardwareKind, dict[ServiceClass | str, str]] = {
    HardwareKind.THREADED_ROD: {
        ServiceClass.AMBIENT: "A193 B7",
        ServiceClass.HOT: "A193 B7",
        ServiceClass.HIGH_TEMP: "A193 B16",
        ServiceClass.COLD: "A193 B7",
        ServiceClass.CRYO: "A320 L7",
    },
    HardwareKind.HEAVY_HEX_NUT: {
        ServiceClass.AMBIENT: "A194 2H",
        ServiceClass.HOT: "A194 2H",
        ServiceClass.HIGH_TEMP: "A194 4",
        ServiceClass.COLD: "A194 2H",
        ServiceClass.CRYO: "A194 4 / S3",
    },
    HardwareKind.WELDLESS_EYE_NUT: {
        "*": "A36 / SS400",
    },
    HardwareKind.CLAMP_BODY: {
        "*": "A36 / SS400",
    },
    HardwareKind.U_BOLT: {
        ServiceClass.COLD: "SUS304",
        ServiceClass.CRYO: "SUS304",
        "*": "A36 / SS400",
    },
    HardwareKind.CLEVIS: {
        "*": "A36 / SS400",
    },
    HardwareKind.TURNBUCKLE: {
        "*": "A36 / SS400",
    },
    HardwareKind.UPPER_BRACKET: {
        ServiceClass.HIGH_TEMP: "SA-240",
        "*": "A36 / SS400",
    },
    HardwareKind.SUPPORT_PIPE: {
        ServiceClass.HIGH_TEMP: "SA-106 Gr.B",
        "*": "A36 / SS400",
    },
    HardwareKind.SUPPORT_PLATE: {
        "*": "A36 / SS400",
    },
    HardwareKind.PLATE_LUG: {
        "*": "A36 / SS400",
    },
    HardwareKind.BEAM_ATTACHMENT: {
        "*": "A36 / SS400",
    },
    HardwareKind.STRUCTURAL_STRUT: {
        "*": "A36 / SS400",
    },
    HardwareKind.SPRING_CAN: {
        "*": "A36 / SS400",
    },
    HardwareKind.COLD_SHOE_INSULATION_CLAMP: {
        "*": "SUS304",
    },
    HardwareKind.EXPANSION_BOLT: {
        "*": "A36 / SS400",
    },
    HardwareKind.ANCHOR_BOLT: {
        "*": "A36 / SS400",
    },
    HardwareKind.PIPE_SHOE: {
        "*": "A36 / SS400",
    },
    HardwareKind.GUSSET_PLATE: {
        "*": "A36 / SS400",
    },
}
