from __future__ import annotations
from typing import Dict, Any, List, Tuple
import re
import pandas as pd
from .xml_generator import OrderXML
from .legacy_txt_parser import parse_legacy_txt_to_df

NL_ZIP_RE = re.compile(r"\b\d{4}\s?[A-Z]{2}\b")

def extract_ship_to_from_o4(df: pd.DataFrame, header: Dict[str, Any] | None = None) -> Tuple[str,str,str,str,str]:
    """Return (name, street, zip, city, country) parsed from O4 if present."""
    o4_val = None
    if "O4" in df.columns:
        series = df["O4"].dropna().astype(str)
        if not series.empty:
            o4_val = series.iloc[0]
    if not o4_val and header and "O4" in header:
        o4_val = str(header["O4"])

    name = street = zip_code = city = ""
    country = "NL"

    if not o4_val:
        return name, street, zip_code, city, country

    parts = [p.strip() for p in str(o4_val).splitlines() if p.strip()]
    for part in parts:
        m = NL_ZIP_RE.search(part.replace(" ", ""))
        if m and not zip_code:
            zip_code = m.group(0).replace(" ", "")
            rest = part.replace(m.group(0), "").strip(" ,")
            if rest and not city:
                city = rest
            continue
        if not name and not part.isdigit():
            name = part

    return name, street, zip_code, city, country

def df_to_order_lines(df: pd.DataFrame) -> List[Dict[str, Any]]:
    if df.empty:
        return []
    core_qty  = df.get("O72").fillna(df.get("P1")).fillna(1)  # prefer O72 → P1
    core_item = df.get("P2").fillna("UNKNOWN")
    core_ref  = df.get("P4")
    order_lines: List[Dict[str, Any]] = []
    for i, row in df.iterrows():
        d = row.dropna().astype(str).to_dict()
        line = {
            "OrderLineReference": (core_ref.iloc[i] if pd.notna(core_ref.iloc[i]) else f"LINE-{i+1}"),
            "Quantity": int(core_qty.iloc[i]) if str(core_qty.iloc[i]).isdigit() else str(core_qty.iloc[i]),
            "ItemId": str(core_item.iloc[i]),
        }
        for k in ["O72","P1","P2","P4"]:
            d.pop(k, None)
        line.update(d)
        order_lines.append(line)
    return order_lines

def build_xml_from_txt(txt_path: str) -> str:
    header, df = parse_legacy_txt_to_df(txt_path)
    order_lines = df_to_order_lines(df)

    reference1              = str(header.get("K1", ""))
    bill_to_account         = str(header.get("K2", ""))
    shipping_reference      = str(header.get("K3", "")) if header.get("K3") else ""
    requested_delivery_date = str(header.get("K4", "")) if header.get("K4") else ""

    ship_to_name, ship_to_street, ship_to_zip, ship_to_city, ship_to_country = \
        extract_ship_to_from_o4(df, header)

    xml = OrderXML().create_purchase_order(
        reference1=reference1,
        shipping_reference=shipping_reference,
        bill_to_account=bill_to_account,
        requested_delivery_date=requested_delivery_date,
        ship_to_name=ship_to_name,
        ship_to_street=ship_to_street,
        ship_to_zip=ship_to_zip,
        ship_to_city=ship_to_city,
        ship_to_country=ship_to_country,
        order_lines=order_lines,
        extra_address_info="",
        region="",
    )
    return xml
