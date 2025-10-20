from __future__ import annotations
import xml.etree.ElementTree as ET
import xml.dom.minidom
from typing import List, Dict, Any, Optional

class OrderXML:
    def __init__(self) -> None:
        self.empty_value = ""

    def create_purchase_order(
        self,
        reference1: str,
        shipping_reference: Optional[str],
        bill_to_account: str,
        requested_delivery_date: str,
        ship_to_name: str,
        ship_to_street: str,
        ship_to_zip: str,
        ship_to_city: str,
        ship_to_country: str,
        order_lines: List[Dict[str, Any]],
        extra_address_info: Optional[str] = None,
        region: Optional[str] = None,
        reference2: str = "",
    ) -> str:
        purchase_order = self.create_purchase_order_header(
            reference1=reference1,
            shipping_reference=shipping_reference,
            bill_to_account=bill_to_account,
            requested_delivery_date=requested_delivery_date,
            ship_to_name=ship_to_name,
            ship_to_street=ship_to_street,
            ship_to_zip=ship_to_zip,
            ship_to_city=ship_to_city,
            ship_to_country=ship_to_country,
            extra_address_info=extra_address_info,
            region=region,
            reference2=reference2,
        )

        lines_element = ET.SubElement(purchase_order, "Lines")
        for line_data in order_lines:
            line_xml = self.create_order_line_xml(line_data)
            line_element = ET.fromstring(line_xml)
            lines_element.append(line_element)

        rough_string = ET.tostring(purchase_order, encoding="unicode")
        parsed = xml.dom.minidom.parseString(rough_string)
        return parsed.toprettyxml(indent="  ")

    def create_purchase_order_header(
        self,
        reference1: str,
        shipping_reference: Optional[str],
        bill_to_account: str,
        requested_delivery_date: str,
        ship_to_name: str,
        ship_to_street: str,
        ship_to_zip: str,
        ship_to_city: str,
        ship_to_country: str,
        extra_address_info: Optional[str] = None,
        region: Optional[str] = None,
        reference2: str = "",
    ):
        purchase_order = ET.Element("PurchaseOrder")

        ET.SubElement(purchase_order, "PurchaseOrderNumber").text = reference1
        ET.SubElement(purchase_order, "Reference1").text = reference2
        ET.SubElement(purchase_order, "ShippingReference").text = shipping_reference or ""
        ET.SubElement(purchase_order, "BillToAccount").text = bill_to_account
        ET.SubElement(purchase_order, "RequestedDeliveryDate").text = requested_delivery_date

        ship_to = ET.SubElement(purchase_order, "ShipToAddress")
        ET.SubElement(ship_to, "Name").text = ship_to_name
        ET.SubElement(ship_to, "StreetName").text = ship_to_street
        ET.SubElement(ship_to, "ZipCode").text = ship_to_zip
        ET.SubElement(ship_to, "City").text = ship_to_city
        ET.SubElement(ship_to, "Region").text = region or ""
        ET.SubElement(ship_to, "Country").text = ship_to_country
        ET.SubElement(ship_to, "ExtraAddressInfo1").text = extra_address_info or ""

        return purchase_order

    def create_order_line_xml(self, order_line: Dict[str, Any]) -> str:
        line = ET.Element("Line")
        ET.SubElement(line, "Reference").text = str(order_line.get("OrderLineReference", ""))
        ET.SubElement(line, "Quantity").text = str(order_line.get("Quantity", 1))
        ET.SubElement(line, "ItemId").text = str(order_line.get("ItemId", 1))
        ET.SubElement(line, "Description")

        attributes = ET.SubElement(line, "Attributes")
        for key, value in order_line.items():
            if key not in ["Quantity", "ItemId", "OrderLineReference"]:
                attribute = ET.SubElement(attributes, "Attribute")
                ET.SubElement(attribute, "Key").text = str(key)
                ET.SubElement(attribute, "Value").text = str(value)

        rough_string = ET.tostring(line, encoding="utf-8")
        parsed = xml.dom.minidom.parseString(rough_string)
        return "".join([ln.strip() for ln in parsed.toprettyxml(indent="").splitlines() if ln.strip()])
