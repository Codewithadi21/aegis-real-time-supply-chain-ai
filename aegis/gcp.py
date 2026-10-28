"""GCP setup helpers. Import only after google-cloud-* libraries are installed."""
from __future__ import annotations
import re
from google.cloud import bigquery
from google.cloud import pubsub_v1

DATASET = 'aegis_warehouse'
TOPIC = 'aegis-sales-events'

SCHEMAS = {
    'dim_products': [('product_id','STRING'),('product_name','STRING'),('category','STRING'),('supplier_id','STRING'),('unit_price_inr','FLOAT64'),('unit_cost_inr','FLOAT64')],
    'dim_suppliers': [('supplier_id','STRING'),('supplier_name','STRING'),('country','STRING'),('nominal_lead_days','INT64')],
    'dim_warehouses': [('warehouse_id','STRING'),('city','STRING'),('country','STRING')],
    'opening_inventory': [('product_id','STRING'),('warehouse_id','STRING'),('opening_stock','INT64')],
    'purchase_orders': [('po_id','STRING'),('product_id','STRING'),('warehouse_id','STRING'),('supplier_id','STRING'),('inbound_qty','INT64'),('arrival_in_days','INT64')],
    'historical_demand': [('sales_date','DATE'),('product_id','STRING'),('day_of_week','INT64'),('promo_flag','INT64'),('unit_price_inr','FLOAT64'),('units_sold','INT64')],
}

def safe_project_id(project_id: str) -> str:
    if not re.fullmatch(r'[a-z][a-z0-9-]{4,61}[a-z0-9]', project_id):
        raise ValueError('Provide your real GCP project ID; it must be a valid project ID, not the display name.')
    return project_id

def create_resources(project_id: str, location: str = 'US'):
    project_id = safe_project_id(project_id)
    client = bigquery.Client(project=project_id)
    dataset = bigquery.Dataset(f'{project_id}.{DATASET}')
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)
    raw = bigquery.Table(f'{project_id}.{DATASET}.raw_sales_events', schema=[bigquery.SchemaField('data','STRING')])
    client.create_table(raw, exists_ok=True)
    for name,fields in SCHEMAS.items():
        table = bigquery.Table(f'{project_id}.{DATASET}.{name}', schema=[bigquery.SchemaField(n,t) for n,t in fields])
        if name == 'historical_demand':
            table.time_partitioning = bigquery.TimePartitioning(field='sales_date',type_=bigquery.TimePartitioningType.DAY)
            table.clustering_fields=['product_id']
        client.create_table(table, exists_ok=True)
    pub=pubsub_v1.PublisherClient()
    topic=pub.topic_path(project_id,TOPIC)
    try:
        pub.create_topic(request={'name':topic})
    except Exception as e:
        from google.api_core.exceptions import AlreadyExists
        if not isinstance(e,AlreadyExists):
            raise
    return client,topic

def load_reference_csv(client, project_id: str, filename: str, table_name: str):
    if table_name not in SCHEMAS: raise ValueError('Unknown reference table')
    cfg=bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=[bigquery.SchemaField(n,t) for n,t in SCHEMAS[table_name]],
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
    )
    table=f'{project_id}.{DATASET}.{table_name}'
    with open(filename,'rb') as fh:
        job=client.load_table_from_file(fh,table,job_config=cfg)
    job.result()
    return client.get_table(table).num_rows

def apply_sql(client, project_id: str, path: str):
    sql=open(path,encoding='utf8').read().replace('{{PROJECT_ID}}',safe_project_id(project_id))
    # Single multi-statement BigQuery query executes sequentially.
    job=client.query(sql,location='US')
    job.result()
    return job.job_id
