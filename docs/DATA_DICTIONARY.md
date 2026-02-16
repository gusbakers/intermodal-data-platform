# Data Dictionary

## Overview
Field definitions for intermodal transportation dataset.

## Core Fields

| Field | Type | Description |
|-------|------|-------------|
| shipment_id | String | Unique identifier |
| origin | String | Departure location |
| destination | String | Arrival location |
| transport_mode | String | Mode (maritime/air/rail/road) |
| cost | Float | Cost in USD |
| weight | Integer | Weight in kg |
| shipment_date | Date | Departure date |
| arrival_date | Date | Arrival date |

## Derived Fields

| Field | Formula | Purpose |
|-------|---------|---------|
| transit_days | arrival_date - shipment_date | Performance metric |
| cost_per_kg | cost / weight | Efficiency metric |
