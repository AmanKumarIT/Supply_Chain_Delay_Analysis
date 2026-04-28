CREATE TABLE shipments (
    id          SERIAL PRIMARY KEY,
    origin      VARCHAR(100) NOT NULL,
    destination VARCHAR(100) NOT NULL,
    status      VARCHAR(50)  NOT NULL DEFAULT 'in_transit',
    created_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ  NOT NULL DEFAULT NOW()
);

CREATE TABLE events (
    id           SERIAL PRIMARY KEY,
    shipment_id  INTEGER REFERENCES shipments(id),
    event_type   VARCHAR(100) NOT NULL,
    payload      JSONB,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE alerts (
    id           SERIAL PRIMARY KEY,
    shipment_id  INTEGER REFERENCES shipments(id),
    alert_type   VARCHAR(100) NOT NULL,
    risk_score   FLOAT,
    resolved     BOOLEAN NOT NULL DEFAULT FALSE,
    created_at   TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
