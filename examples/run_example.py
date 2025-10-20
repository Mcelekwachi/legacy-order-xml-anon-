from pathlib import Path
from legacy_order_to_xml.adapter import build_xml_from_txt

if __name__ == "__main__":
    txt = Path(__file__).with_name("sample_order.txt")
    xml_out = build_xml_from_txt(str(txt))
    out_path = Path(__file__).with_name("purchase_order.xml")
    out_path.write_text(xml_out, encoding="utf-8")
    print(f"Wrote {out_path}")
