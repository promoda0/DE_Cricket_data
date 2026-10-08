# Silver Data Model

## 1. Purpose

The Silver layer converts the nested Cricket JSON preserved in the
Bronze layer into structured datasets suitable for downstream
processing and analytics.

Initial Silver datasets:

1. matches
2. innings
3. deliveries

This ticket defines the Silver data model. Transformation
implementation is handled separately by IPL-260006.

---

## 2. Source

Bronze source:

output/bronze/cricket/matches/<match_id>.json

Example:

output/bronze/cricket/matches/1082591.json

---

## 3. Silver Data Model

```text
silver_matches
      |
      | 1:N
      v
silver_innings
      |
      | 1:N
      v
silver_deliveries