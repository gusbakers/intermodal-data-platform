-- Grain: one record per shipment_id. Dimensions describe the provided shipment snapshot.
CREATE SCHEMA IF NOT EXISTS logistics;

CREATE TABLE IF NOT EXISTS logistics.dim_transport_modes (
    mode_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    dominant_mode TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS logistics.dim_routes (
    route_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    origin_city TEXT NOT NULL,
    destination_city TEXT NOT NULL,
    UNIQUE (origin_city, destination_city)
);
CREATE TABLE IF NOT EXISTS logistics.dim_cargo_types (
    cargo_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    cargo_type TEXT NOT NULL UNIQUE
);
CREATE TABLE IF NOT EXISTS logistics.dim_priorities (
    priority_id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    priority_level TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS logistics.fact_shipments (
    shipment_id TEXT PRIMARY KEY,
    mode_id INTEGER NOT NULL REFERENCES logistics.dim_transport_modes(mode_id),
    route_id INTEGER NOT NULL REFERENCES logistics.dim_routes(route_id),
    cargo_id INTEGER NOT NULL REFERENCES logistics.dim_cargo_types(cargo_id),
    priority_id INTEGER NOT NULL REFERENCES logistics.dim_priorities(priority_id),
    weight_tons NUMERIC(12, 2) NOT NULL CHECK (weight_tons > 0),
    declared_value_usd NUMERIC(18, 2) NOT NULL CHECK (declared_value_usd >= 0),
    planned_duration_hours INTEGER NOT NULL CHECK (planned_duration_hours > 0),
    status TEXT NOT NULL CHECK (status IN ('On-Time', 'Delayed')),
    risk_flag SMALLINT NOT NULL CHECK (risk_flag IN (0, 1)),
    actual_duration_hours INTEGER NOT NULL CHECK (actual_duration_hours > 0),
    weather_severity_avg DOUBLE PRECISION NOT NULL CHECK (weather_severity_avg >= 0),
    total_legs INTEGER NOT NULL CHECK (total_legs > 0),
    total_distance_km NUMERIC(14, 2) NOT NULL CHECK (total_distance_km > 0),
    total_fuel_cost_usd NUMERIC(18, 2) NOT NULL CHECK (total_fuel_cost_usd >= 0),
    avg_leg_delay_minutes DOUBLE PRECISION NOT NULL CHECK (avg_leg_delay_minutes >= 0),
    vehicle_avg_maintenance_score DOUBLE PRECISION NOT NULL CHECK (vehicle_avg_maintenance_score BETWEEN 0 AND 1),
    source_hash CHAR(64) NOT NULL,
    loaded_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CHECK ((status = 'On-Time') = (actual_duration_hours <= planned_duration_hours))
);

CREATE INDEX IF NOT EXISTS ix_shipments_mode ON logistics.fact_shipments(mode_id);
CREATE INDEX IF NOT EXISTS ix_shipments_route ON logistics.fact_shipments(route_id);
CREATE INDEX IF NOT EXISTS ix_shipments_cargo ON logistics.fact_shipments(cargo_id);
CREATE INDEX IF NOT EXISTS ix_shipments_priority ON logistics.fact_shipments(priority_id);
