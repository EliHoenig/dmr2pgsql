DROP TABLE IF EXISTS dmr;

CREATE TABLE dmr (npdes_id text, permit_name text, permit_feature_id text, limit_set_name text, parameter text, monitoring_location text, period_end_date date, dmr_qualifier text, dmr_value decimal, dmr_unit text, statistical_base text, nodi_text text, limit_qualifier text, limit_value decimal, limit_unit text);

CREATE INDEX ON dmr (npdes_id, period_end_date);
