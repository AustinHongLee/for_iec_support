"""長春業主配管支撐基準 DES-M15172 計算套件。"""

from .dispatch import analyze, can_handle, supported_codes

__all__ = ["analyze", "can_handle", "supported_codes"]
