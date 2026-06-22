"""External designation alias registry.

This module only resolves explicitly configured aliases. It does not change the
standard parser or calculator entry points; callers must opt in.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re


APP_DIR = Path(__file__).resolve().parents[1]
DEFAULT_ALIAS_PATH = APP_DIR / "configs" / "code_aliases.json"


@dataclass(frozen=True)
class AliasResolution:
    original: str
    designation: str
    alias_ref: str
    maps_to_base: str
    pattern: str


def load_code_aliases(path: str | Path | None = None) -> dict:
    alias_path = Path(path) if path else DEFAULT_ALIAS_PATH
    if not alias_path.exists():
        return {"version": None, "aliases": {}}
    with alias_path.open("r", encoding="utf-8") as f:
        return json.load(f)


def validate_code_aliases(config: dict) -> list[str]:
    issues: list[str] = []
    if not isinstance(config, dict):
        return ["alias config must be a JSON object"]

    aliases = config.get("aliases")
    if not isinstance(aliases, dict):
        return ["aliases must be an object"]

    for alias_ref, alias in aliases.items():
        if not isinstance(alias, dict):
            issues.append(f"{alias_ref}: alias entry must be an object")
            continue
        if not isinstance(alias.get("maps_to_base"), str) or not alias.get("maps_to_base"):
            issues.append(f"{alias_ref}: maps_to_base must be a non-empty string")
        patterns = alias.get("patterns")
        if not isinstance(patterns, list) or not patterns:
            issues.append(f"{alias_ref}: patterns must be a non-empty list")
            continue
        for index, pattern in enumerate(patterns, 1):
            if not isinstance(pattern, dict):
                issues.append(f"{alias_ref}: pattern {index} must be an object")
                continue
            match_expr = pattern.get("match")
            if not isinstance(match_expr, str) or not match_expr:
                issues.append(f"{alias_ref}: pattern {index} match must be a non-empty string")
            else:
                try:
                    re.compile(match_expr)
                except re.error as exc:
                    issues.append(f"{alias_ref}: pattern {index} regex error: {exc}")
            if not isinstance(pattern.get("designation"), str) or not pattern.get("designation"):
                issues.append(f"{alias_ref}: pattern {index} designation template is required")
    return issues


def resolve_designation_alias(
    value: str,
    *,
    alias_ref: str | None = None,
    config: dict | None = None,
) -> AliasResolution | None:
    alias_config = config if config is not None else load_code_aliases()
    aliases = alias_config.get("aliases", {}) if isinstance(alias_config, dict) else {}
    candidates = (
        [(alias_ref, aliases.get(alias_ref))]
        if alias_ref
        else list(aliases.items())
    )

    text = str(value or "").strip()
    for ref, alias in candidates:
        if not ref or not isinstance(alias, dict):
            continue
        for pattern in alias.get("patterns", []):
            if not isinstance(pattern, dict):
                continue
            match_expr = pattern.get("match")
            template = pattern.get("designation")
            if not match_expr or not template:
                continue
            matched = re.fullmatch(match_expr, text)
            if not matched:
                continue
            groups = {key: (val or "") for key, val in matched.groupdict().items()}
            try:
                designation = template.format(**groups)
            except KeyError:
                continue
            return AliasResolution(
                original=text,
                designation=designation,
                alias_ref=ref,
                maps_to_base=str(alias.get("maps_to_base", "")),
                pattern=match_expr,
            )
    return None
