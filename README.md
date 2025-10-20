# legacy-order-xml-anon-
A minimal, anonymized reference project that converts **legacy text-based orders** into a structured **XML** format.

- **Input**: legacy `.txt` files with `:TAG:VALUE` lines, header fields like `K1`, `K2`, and repeated order-line blocks between `UB..` and `UE`.
- **Middle**: parse into a **pandas DataFrame** for validation/normalization.
- **Output**: create an XML purchase order using a small `OrderXML` generator class.

> This repo intentionally avoids any company/client names and uses neutral placeholders.

## Project Structure
