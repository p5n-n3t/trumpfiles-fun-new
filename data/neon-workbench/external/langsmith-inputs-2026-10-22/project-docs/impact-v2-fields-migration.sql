-- Offline-prepared additive schema only. No legacy score/severity/title/synopsis
-- or historical ranking field is changed by this migration.
ALTER TABLE public.trump_entries
    ADD COLUMN IF NOT EXISTS impact_score_v2 NUMERIC(4,2),
    ADD COLUMN IF NOT EXISTS impact_rank_v2 INTEGER,
    ADD COLUMN IF NOT EXISTS impact_dimensions_v2 JSONB,
    ADD COLUMN IF NOT EXISTS impact_confidence_v2 TEXT;
