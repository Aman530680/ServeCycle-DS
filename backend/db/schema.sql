-- ServeCycle database schema
-- Idempotent: safe to run multiple times against the same database.
-- MySQL 8+

CREATE DATABASE IF NOT EXISTS servecycle
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE servecycle;

-- ---------------------------------------------------------------
-- food_categories
-- Lookup table for the five food types in the dataset.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS food_categories (
    id   TINYINT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(50)      NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_food_category_name (name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------
-- event_records
-- One row per catering event. This is the core fact table.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS event_records (
    id                           INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    food_category_id             TINYINT UNSIGNED NOT NULL,
    num_guests                   SMALLINT UNSIGNED NOT NULL,
    event_type                   VARCHAR(30)      NOT NULL,
    qty_prepared                 SMALLINT UNSIGNED NOT NULL,
    storage_conditions           VARCHAR(20)      NOT NULL,
    purchase_history             VARCHAR(15)      NOT NULL,
    seasonality                  VARCHAR(15)      NOT NULL,
    preparation_method           VARCHAR(20)      NOT NULL,
    geographical_location        VARCHAR(15)      NOT NULL,
    pricing                      VARCHAR(10)      NOT NULL,
    wastage_amount               SMALLINT UNSIGNED NOT NULL,
    -- flag columns: 0 = clean, 1 = flagged
    flag_missing                 TINYINT(1)       NOT NULL DEFAULT 0,
    flag_duplicate               TINYINT(1)       NOT NULL DEFAULT 0,
    flag_negative_qty            TINYINT(1)       NOT NULL DEFAULT 0,
    flag_zero_prepared           TINYINT(1)       NOT NULL DEFAULT 0,
    flag_wastage_exceeds_prepared TINYINT(1)      NOT NULL DEFAULT 0,
    flag_outlier_guests          TINYINT(1)       NOT NULL DEFAULT 0,
    flag_outlier_qty_food        TINYINT(1)       NOT NULL DEFAULT 0,
    flag_outlier_wastage         TINYINT(1)       NOT NULL DEFAULT 0,
    flag_unknown_category        TINYINT(1)       NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    CONSTRAINT fk_event_food_category
        FOREIGN KEY (food_category_id) REFERENCES food_categories (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    INDEX idx_event_food_category  (food_category_id),
    INDEX idx_event_type           (event_type),
    INDEX idx_geographical_location (geographical_location),
    INDEX idx_pricing              (pricing),
    INDEX idx_seasonality          (seasonality),
    INDEX idx_preparation_method   (preparation_method)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------
-- model_runs
-- One row per training run. Populated by src/model.py.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS model_runs (
    id                    INT UNSIGNED NOT NULL AUTO_INCREMENT,
    run_timestamp         TIMESTAMP    NOT NULL DEFAULT CURRENT_TIMESTAMP,
    features_json         JSON         NOT NULL,
    train_rows            INT UNSIGNED NOT NULL,
    test_rows             INT UNSIGNED NOT NULL,
    mae                   DECIMAL(8,4) NOT NULL,
    rmse                  DECIMAL(8,4) NOT NULL,
    r2                    DECIMAL(6,4) NOT NULL,
    wape                  DECIMAL(6,4) NOT NULL,
    library_versions_json JSON         NOT NULL,
    PRIMARY KEY (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------
-- predictions
-- Model output for a given event context. Populated by the API.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS predictions (
    id                 INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    model_run_id       INT UNSIGNED    NOT NULL,
    event_record_id    INT UNSIGNED    NULL,
    predicted_wastage  DECIMAL(8,2)    NOT NULL,
    created_at         TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_pred_model_run
        FOREIGN KEY (model_run_id) REFERENCES model_runs (id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_pred_event_record
        FOREIGN KEY (event_record_id) REFERENCES event_records (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------
-- recommendations
-- Suggested preparation quantities. Populated by the recommendation engine.
-- ---------------------------------------------------------------
CREATE TABLE IF NOT EXISTS recommendations (
    id                INT UNSIGNED    NOT NULL AUTO_INCREMENT,
    event_record_id   INT UNSIGNED    NULL,
    predicted_wastage DECIMAL(8,2)    NOT NULL,
    recommended_qty   SMALLINT UNSIGNED NOT NULL,
    service_level     DECIMAL(4,3)    NOT NULL,
    created_at        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    CONSTRAINT fk_rec_event_record
        FOREIGN KEY (event_record_id) REFERENCES event_records (id)
        ON UPDATE CASCADE ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ---------------------------------------------------------------
-- v_wastage_pct
-- Derived view — wastage % is never stored as a column.
-- Returns NULL where qty_prepared is zero to avoid division by zero.
-- ---------------------------------------------------------------
CREATE OR REPLACE VIEW v_wastage_pct AS
SELECT
    id,
    food_category_id,
    event_type,
    num_guests,
    qty_prepared,
    wastage_amount,
    CASE
        WHEN qty_prepared > 0
        THEN wastage_amount / qty_prepared * 100.0
        ELSE NULL
    END AS wastage_pct,
    flag_duplicate,
    flag_negative_qty,
    flag_zero_prepared,
    flag_wastage_exceeds_prepared,
    flag_outlier_guests,
    flag_outlier_qty_food,
    flag_outlier_wastage,
    flag_unknown_category
FROM event_records;
