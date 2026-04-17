"""
字串解析工具 - 對應 VBA 中的 B_工具類函數 + Z_97準備被替代的函數
"""
import re
from typing import Optional


def get_part(fullstring: str, index: int, delimiter: str = "-") -> Optional[str]:
    """
    取得字串以 delimiter 分割後的第 index 部分 (1-based)
    對應 VBA: GetPartOfString / GetFirstPartOfString / GetSecondPartOfString 等
    """
    parts = fullstring.split(delimiter)
    if 1 <= index <= len(parts):
        return parts[index - 1]
    return None


def get_type_code(fullstring: str) -> str:
    """取得 Type 編號 (第一段)"""
    return get_part(fullstring, 1) or ""


def count_char(text: str, char: str) -> int:
    """計算字元出現次數"""
    return text.count(char)


def get_lookup_value(value) -> float:
    """
    將管徑字串轉換為數值
    對應 VBA: GetLookupValue
    
    支援格式:
    - "10" -> 10
    - "2B" -> 2
    - "1/2" -> 0.5
    - "3/4" -> 0.75
    - "1 1/2" -> 1.5
    - "1-1/2" -> 1.5
    - "'10" -> 10
    """
    s = str(value).strip()

    # 移除 B 後綴
    s = s.replace("B", "")

    # 移除前導引號
    s = s.lstrip("'")

    # 處理分數 (可能帶整數部分, 用空格或-分隔)
    if "/" in s:
        # 統一分隔符: "1-1/2" -> "1 1/2"
        s = s.replace("-", " ")
        parts = s.split("/")
        if len(parts) == 2:
            numerator_parts = parts[0].split()
            if len(numerator_parts) == 2:
                # "1 1/2" 格式
                whole = float(numerator_parts[0])
                frac = float(numerator_parts[1]) / float(parts[1])
                return whole + frac
            elif len(numerator_parts) == 1:
                # "1/2" 格式
                return float(numerator_parts[0]) / float(parts[1])
    
    # 移除所有非數字和小數點的字元
    numeric = re.sub(r'[^\d.]', '', s)
    if numeric:
        return float(numeric)
    
    return 0.0


def extract_parts(value: str) -> tuple:
    """
    拆分帶括號的字串
    對應 VBA: ExtractParts
    例如: "A(S)" -> ("A", "(S)")
          "2B(P)" -> ("2B", "(P)")
          "ABC" -> ("ABC", "")
    """
    paren_pos = value.find("(")
    if paren_pos > 0:
        return (value[:paren_pos], value[paren_pos:])
    return (value, "")


def clean_pipe_size(pipe_size) -> float:
    """
    清理管徑字串，回傳數值
    對應 VBA: CleanPipeSize
    """
    s = str(pipe_size)
    s = s.replace("B", "")
    s = s.replace("'", "")
    return get_lookup_value(s)


def is_fourth_part_available(fullstring: str) -> bool:
    """檢查是否有第四段"""
    parts = fullstring.split("-")
    return len(parts) >= 4
