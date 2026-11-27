# Databricks notebook source
# MAGIC %md
# MAGIC # AEGIS inventory migration
# MAGIC Run from a Databricks Git folder on Python compute with Delta Lake.
# MAGIC Set the catalog and schema widgets to a writable scratch schema.

# COMMAND ----------

import csv
from pathlib import Path
from uuid import uuid4

from pyspark.sql import Window, functions as F, types as T

dbutils.widgets.text("catalog", "workspace")
dbutils.widgets.text("schema", "default")
dbutils.widgets.text("sample_csv", "../../data/samples/inventory.csv")

def quote_identifier(value):
    return "`" + value.replace("`", "``") + "`"

catalog = quote_identifier(dbutils.widgets.get("catalog"))
schema = quote_identifier(dbutils.widgets.get("schema"))
table = f"{catalog}.{schema}.aegis_inventory_demo_{uuid4().hex[:12]}"
sample = Path(dbutils.widgets.get("sample_csv"))
keys = ["warehouse_id", "product_id"]
demo_key = ("WH_IND_01", "LAPTOP_001")
late_key = ("WH_IND_01", "PHONE_001")
stockout_threshold = 5
spark.conf.set("spark.sql.session.timeZone", "UTC")

# COMMAND ----------

raw_schema = T.StructType([
    T.StructField("warehouse_id", T.StringType(), False),
    T.StructField("product_id", T.StringType(), False),
    T.StructField("stock_qty", T.LongType(), False),
    T.StructField("updated_at_utc", T.StringType(), False),
])
snapshot_columns = keys + ["stock_qty", "updated_at"]

with sample.open(newline="", encoding="utf-8") as handle:
    reader = csv.DictReader(handle)
    if reader.fieldnames != ["product_id", "warehouse_id", "opening_stock"]:
        raise ValueError("Unexpected AEGIS inventory CSV header")
    opening_rows = [
        (row["warehouse_id"], row["product_id"], int(row["opening_stock"]),
         "2025-01-02T00:00:00Z")
        for row in reader
    ]

opening_stock = {(wh, product): qty for wh, product, qty, _ in opening_rows}
assert len(opening_rows) == len(opening_stock) == 12
assert {demo_key, late_key} <= opening_stock.keys()
batch_one = spark.createDataFrame([*opening_rows, opening_rows[0]], raw_schema)
batch_two = spark.createDataFrame([
    (*demo_key, 4, "2025-01-03T00:00:00Z"),
    (*late_key, 99, "2025-01-01T00:00:00Z"),
], raw_schema)

# COMMAND ----------

def prepare_batch(raw):
    if [(f.name, f.dataType) for f in raw.schema] != [
        (f.name, f.dataType) for f in raw_schema
    ]:
        raise ValueError("Unexpected inventory batch schema")

    batch = raw.select(
        *keys, "stock_qty",
        F.to_timestamp("updated_at_utc", "yyyy-MM-dd'T'HH:mm:ssX").alias("updated_at"),
    )
    invalid = (
        F.col("warehouse_id").isNull() | (F.trim("warehouse_id") == "") |
        F.col("product_id").isNull() | (F.trim("product_id") == "") |
        F.col("stock_qty").isNull() | (F.col("stock_qty") < 0) |
        F.col("updated_at").isNull()
    )
    if batch.filter(invalid).take(1):
        raise ValueError("Invalid inventory key, quantity, or timestamp")

    distinct = batch.dropDuplicates()
    conflicts = distinct.groupBy(*keys, "updated_at").count().filter("count > 1")
    if conflicts.take(1):
        raise ValueError("Conflicting quantities for the same key and timestamp")

    by_latest = Window.partitionBy(*keys).orderBy(F.col("updated_at").desc())
    return (
        distinct.withColumn("rank", F.row_number().over(by_latest))
        .filter("rank = 1")
        .drop("rank")
    )

seed = prepare_batch(batch_one)
updates = prepare_batch(batch_two)
assert batch_one.count() == 13 and seed.count() == 12

spark.sql(f"""
CREATE TABLE {table} (
    warehouse_id STRING, product_id STRING, stock_qty BIGINT, updated_at TIMESTAMP
) USING DELTA
""")
print(f"Demo Delta table: {table}")

def merge(batch):
    batch.createOrReplaceTempView("aegis_demo_batch")
    spark.sql(f"""
        MERGE INTO {table} AS target
        USING aegis_demo_batch AS incoming
        ON target.warehouse_id = incoming.warehouse_id
           AND target.product_id = incoming.product_id
        WHEN MATCHED AND incoming.updated_at > target.updated_at THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

def snapshot_rows():
    return spark.table(table).select(*snapshot_columns).orderBy(*keys).collect()

# COMMAND ----------

merge(seed)
before = snapshot_rows()
merge(updates)
after = snapshot_rows()
merge(updates)
replayed = snapshot_rows()

assert len(before) == len(after) == 12
assert after == replayed, "Batch replay changed the curated snapshot"
changed_keys = [(a.warehouse_id, a.product_id) for a, b in zip(after, before) if a != b]
assert changed_keys == [demo_key]
assert next(r.stock_qty for r in after if (r.warehouse_id, r.product_id) == demo_key) == 4
print("Seed: 13 input rows, 12 distinct keys. Batch 2: 1 changed row. Replay: 0 changed rows.")

# COMMAND ----------

# Format the actual Delta timestamp as an explicit UTC string for BigQuery CSV import.
export = spark.table(table).select(
    *keys, "stock_qty",
    F.concat(F.date_format("updated_at", "yyyy-MM-dd HH:mm:ss"), F.lit("+00:00")).alias("updated_at"),
    (F.col("stock_qty") < stockout_threshold).alias("stockout_flag"),
).orderBy(*keys)
display(export)
