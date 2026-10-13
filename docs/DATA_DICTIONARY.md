# Shipment data dictionary

**Grain:** one shipment per `shipment_id`. The source is `data/raw/intermodal_transport_full_dataset.csv`, already included in the repository. Upstream provenance and collection dates are not recorded.

## Source fields

| Field | Type / unit | Meaning and contract |
|---|---|---|
| `shipment_id` | String | Nonempty unique shipment identifier; conflicting IDs are quarantined |
| `origin_city` | String | Shipment origin, required |
| `destination_city` | String | Shipment destination, required |
| `cargo_type` | String | Cargo category, required |
| `weight_tons` | Number, tonnes | Positive shipment weight |
| `declared_value_usd` | Number, USD | Nonnegative declared cargo value; this is not revenue |
| `priority_level` | String | Low, Medium or High |
| `planned_duration_hours` | Positive integer, hours | Planned end-to-end duration |
| `status` | String | On-Time or Delayed; must agree with actual versus planned duration |
| `risk_flag` | Integer | Binary source flag; its upstream definition is not documented |
| `actual_duration_hours` | Positive integer, hours | Actual end-to-end duration |
| `weather_severity_avg` | Nonnegative number | Source weather measure; its scale is not documented |
| `total_legs` | Positive integer | Number of shipment legs; individual leg records are unavailable |
| `total_distance_km` | Positive number, km | Shipment distance |
| `total_fuel_cost_usd` | Nonnegative number, USD | Shipment fuel expense; excludes any undocumented operating costs |
| `avg_leg_delay_minutes` | Nonnegative number, minutes | Source average leg delay measure |
| `dominant_mode` | String | Rail, Ship or Truck in the included snapshot; not the complete leg sequence |
| `vehicle_avg_maintenance_score` | Number in [0, 1] | Source vehicle maintenance score |

All 18 fields are required and numeric fields must be finite. The supplied dataset has 20,000 rows, no duplicate shipment IDs and no missing source values. Field completeness does not establish authenticity or correctness outside the implemented contracts.

## Derived fields

| Field | Definition |
|---|---|
| `is_on_time` | `actual_duration_hours <= planned_duration_hours` |
| `delay_hours` | `max(actual_duration_hours - planned_duration_hours, 0)` |
| `fuel_cost_per_km` | Per shipment: fuel expense / distance |
| `fuel_cost_per_ton_km` | Per shipment: fuel expense / (weight in tonnes × distance in km) |
| `processed_at` | UTC processing timestamp; not a shipment event date |

## Aggregate KPIs

| Metric | Denominator / formula |
|---|---|
| On-time percentage | 100 × on-time accepted shipments / all accepted shipments |
| Average planned / actual duration | Sum of corresponding hours / accepted shipments |
| Average delay among delayed shipments | Sum of positive delay hours / delayed shipments; null if none |
| Average fuel expense | Total fuel expense / accepted shipments |
| Weighted fuel expense per km | Sum of fuel expense / sum of distance |
| Weighted fuel expense per tonne-km | Sum of fuel expense / sum of (weight × distance) |

Aggregate fuel ratios use ratios of totals, not an unweighted average of individual ratios. Python output tables summarize the current input file; PostgreSQL views summarize all retained facts.

## Unavailable analyses

Shipment dates, carrier identities, shipment revenue and individual leg sequences are absent. Time-series analysis, carrier performance, route profitability and complete intermodal reconstruction require additional fields. Post-arrival metrics also require a feature-availability review before any pre-shipment prediction model is developed.
