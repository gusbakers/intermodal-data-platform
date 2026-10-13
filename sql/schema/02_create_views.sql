-- Six materialized views; all metrics describe the stored shipment snapshot.
CREATE OR REPLACE VIEW logistics.vw_shipment_analytics AS
SELECT f.*, m.dominant_mode, r.origin_city, r.destination_city,
       c.cargo_type, p.priority_level,
       f.actual_duration_hours <= f.planned_duration_hours AS is_on_time,
       GREATEST(f.actual_duration_hours - f.planned_duration_hours, 0) AS delay_hours,
       f.total_fuel_cost_usd / f.total_distance_km AS fuel_cost_per_km,
       f.total_fuel_cost_usd / (f.weight_tons * f.total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.fact_shipments f
JOIN logistics.dim_transport_modes m USING (mode_id)
JOIN logistics.dim_routes r USING (route_id)
JOIN logistics.dim_cargo_types c USING (cargo_id)
JOIN logistics.dim_priorities p USING (priority_id);

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_kpi_dashboard AS
SELECT COUNT(*) AS total_shipments,
       COUNT(*) FILTER (WHERE is_on_time) AS on_time_shipments,
       COUNT(*) FILTER (WHERE NOT is_on_time) AS delayed_shipments,
       100.0 * COUNT(*) FILTER (WHERE is_on_time) / NULLIF(COUNT(*), 0) AS on_time_pct,
       AVG(planned_duration_hours) AS avg_planned_duration_hours,
       AVG(actual_duration_hours) AS avg_actual_duration_hours,
       AVG(delay_hours) FILTER (WHERE NOT is_on_time) AS avg_delay_hours_delayed,
       SUM(total_fuel_cost_usd) AS total_fuel_cost_usd,
       AVG(total_fuel_cost_usd) AS avg_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / NULLIF(SUM(total_distance_km), 0) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / NULLIF(SUM(weight_tons * total_distance_km), 0) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_mode_performance AS
SELECT dominant_mode, COUNT(*) AS total_shipments,
       COUNT(*) FILTER (WHERE is_on_time) AS on_time_shipments,
       COUNT(*) FILTER (WHERE NOT is_on_time) AS delayed_shipments,
       100.0 * COUNT(*) FILTER (WHERE is_on_time) / COUNT(*) AS on_time_pct,
       AVG(planned_duration_hours) AS avg_planned_duration_hours,
       AVG(actual_duration_hours) AS avg_actual_duration_hours,
       AVG(delay_hours) FILTER (WHERE NOT is_on_time) AS avg_delay_hours_delayed,
       SUM(total_fuel_cost_usd) AS total_fuel_cost_usd, AVG(total_fuel_cost_usd) AS avg_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / SUM(total_distance_km) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / SUM(weight_tons * total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics GROUP BY dominant_mode WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_route_performance AS
SELECT origin_city, destination_city, COUNT(*) AS total_shipments,
       COUNT(*) FILTER (WHERE is_on_time) AS on_time_shipments,
       COUNT(*) FILTER (WHERE NOT is_on_time) AS delayed_shipments,
       100.0 * COUNT(*) FILTER (WHERE is_on_time) / COUNT(*) AS on_time_pct,
       AVG(planned_duration_hours) AS avg_planned_duration_hours,
       AVG(actual_duration_hours) AS avg_actual_duration_hours,
       AVG(delay_hours) FILTER (WHERE NOT is_on_time) AS avg_delay_hours_delayed,
       SUM(total_fuel_cost_usd) AS total_fuel_cost_usd, AVG(total_fuel_cost_usd) AS avg_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / SUM(total_distance_km) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / SUM(weight_tons * total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics GROUP BY origin_city, destination_city WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_cargo_performance AS
SELECT cargo_type, COUNT(*) AS total_shipments,
       COUNT(*) FILTER (WHERE is_on_time) AS on_time_shipments,
       COUNT(*) FILTER (WHERE NOT is_on_time) AS delayed_shipments,
       100.0 * COUNT(*) FILTER (WHERE is_on_time) / COUNT(*) AS on_time_pct,
       AVG(planned_duration_hours) AS avg_planned_duration_hours,
       AVG(actual_duration_hours) AS avg_actual_duration_hours,
       AVG(delay_hours) FILTER (WHERE NOT is_on_time) AS avg_delay_hours_delayed,
       SUM(total_fuel_cost_usd) AS total_fuel_cost_usd, AVG(total_fuel_cost_usd) AS avg_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / SUM(total_distance_km) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / SUM(weight_tons * total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics GROUP BY cargo_type WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_priority_performance AS
SELECT priority_level, COUNT(*) AS total_shipments,
       COUNT(*) FILTER (WHERE is_on_time) AS on_time_shipments,
       COUNT(*) FILTER (WHERE NOT is_on_time) AS delayed_shipments,
       100.0 * COUNT(*) FILTER (WHERE is_on_time) / COUNT(*) AS on_time_pct,
       AVG(planned_duration_hours) AS avg_planned_duration_hours,
       AVG(actual_duration_hours) AS avg_actual_duration_hours,
       AVG(delay_hours) FILTER (WHERE NOT is_on_time) AS avg_delay_hours_delayed,
       SUM(total_fuel_cost_usd) AS total_fuel_cost_usd, AVG(total_fuel_cost_usd) AS avg_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / SUM(total_distance_km) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / SUM(weight_tons * total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics GROUP BY priority_level WITH NO DATA;

CREATE MATERIALIZED VIEW IF NOT EXISTS logistics.mv_fuel_efficiency AS
SELECT dominant_mode, COUNT(*) AS total_shipments, SUM(total_fuel_cost_usd) AS total_fuel_cost_usd,
       SUM(total_fuel_cost_usd) / SUM(total_distance_km) AS fuel_cost_per_km,
       SUM(total_fuel_cost_usd) / SUM(weight_tons * total_distance_km) AS fuel_cost_per_ton_km
FROM logistics.vw_shipment_analytics GROUP BY dominant_mode WITH NO DATA;
