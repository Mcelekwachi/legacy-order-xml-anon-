from __future__ import annotations
from pathlib import Path
from typing import Dict, Tuple, List
import re
import pandas as pd

# :UBxx: starts a new line; :UE: ends it
LINE_START = re.compile(r"^:UB\d+:")
KV_LINE    = re.compile(r"^:([^:]+):(.*)$")  # :TAG:VALUE

def parse_legacy_txt_to_df(txt_path: str) -> Tuple[Dict[str, str], pd.DataFrame]:
    """
    Parse a legacy .txt order file into (header_dict, lines_df).
    - Header keys (e.g., K1, K2, K3...) appear outside any UB.. block.
    - Each UB.. to UE block becomes one row (one order line).
    Unknown tags are preserved in the resulting DataFrame columns.
    """
    lines = Path(txt_path).read_text(encoding="utf-8", errors="ignore").splitlines()

    header: Dict[str, str] = {}
    rows: List[Dict[str, str]] = []
    cur: Dict[str, str] | None = None

    for raw in lines:
        m = KV_LINE.match(raw.strip())
        if not m:
            continue
        tag, val = m.group(1).strip(), m.group(2).strip()

        if LINE_START.match(raw):
            cur = {}
            continue
        if tag == "UE":
            if cur:
                rows.append(cur)
            cur = None
            continue

        if cur is not None:
            cur[tag] = val
        else:
            header[tag] = val

    df = pd.DataFrame(rows) if rows else pd.DataFrame()
    return header, df
