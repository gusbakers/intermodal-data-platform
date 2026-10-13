-- Run after: python run_full_pipeline.py --with-database
SELECT * FROM logistics.mv_kpi_dashboard;

-- Mode comparisons: weighted fuel-cost ratios, not averages of per-shipment ratios.
SELECT dominant_mode, total_shipments, ROUND(on_time_pct, 2) AS on_time_pct,
       ROUND(fuel_cost_per_km, 4) AS fuel_usd_per_km,
       ROUND(fuel_cost_per_ton_km, 4) AS fuel_usd_per_ton_km
FROM logistics.mv_mode_performance ORDER BY fuel_cost_per_ton_km;

-- Prioritize routes with enough observations; this is descriptive, not a causal ranking.
SELECT origin_city, destination_city, total_shipments,
       ROUND(100 - on_time_pct, 2) AS delayed_pct,
       ROUND(avg_delay_hours_delayed, 2) AS avg_delay_hours_delayed
FROM logistics.mv_route_performance
WHERE total_shipments >= 100
ORDER BY delayed_pct DESC, total_shipments DESC;

SELECT * FROM logistics.mv_cargo_performance ORDER BY total_shipments DESC;
SELECT * FROM logistics.mv_priority_performance ORDER BY priority_level;
SELECT * FROM logistics.mv_fuel_efficiency ORDER BY dominant_mode;
