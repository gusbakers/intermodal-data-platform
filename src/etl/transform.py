"""Shipment-level analytical features with explicit hours, tonnes, kilometres and USD."""

import pandas as pd

from src.utils.logger import log


class DataTransformer:
    def transform(self, frame: pd.DataFrame) -> pd.DataFrame:
        data = frame.copy()
        data["is_on_time"] = data.actual_duration_hours.le(data.planned_duration_hours)
        data["delay_hours"] = (data.actual_duration_hours - data.planned_duration_hours).clip(lower=0)
        data["fuel_cost_per_km"] = data.total_fuel_cost_usd / data.total_distance_km
        data["fuel_cost_per_ton_km"] = data.total_fuel_cost_usd / (data.weight_tons * data.total_distance_km)
        data["processed_at"] = pd.Timestamp.now(tz="UTC")
        log.info("Derived features for %s validated shipments", len(data))
        return data
