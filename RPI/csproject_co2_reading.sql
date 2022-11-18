-- Sequence and defined type
CREATE SEQUENCE IF NOT EXISTS csproject_co2_reading_id_seq;

-- Table Definition
CREATE TABLE "public"."csproject_co2_reading" (
    "id" int4 NOT NULL DEFAULT nextval('csproject_co2_reading_id_seq'::regclass),
    "sensor_id" VARCHAR(12) NOT NULL,
    "session_id" int8 NOT NULL,
    "value" int8 NOT NULL,
    "created_at" timestamp NOT NULL DEFAULT now(),
    PRIMARY KEY ("id")
);
