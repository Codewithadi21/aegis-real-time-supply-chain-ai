"""GCP setup (creates BigQuery tables and a Pub/Sub topic, NOT a subscription)."""
import argparse
from aegis.synthetic import generate
from aegis.gcp import create_resources,load_reference_csv,apply_sql,SCHEMAS

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project-id',required=True)
    p.add_argument('--skip-load',action='store_true')
    args=p.parse_args()
    client,topic=create_resources(args.project_id)
    print('Created dataset and tables, plus Pub/Sub topic:',topic)
    if not args.skip_load:
        generate()
        csv_names={"dim_products":"products","dim_suppliers":"suppliers","dim_warehouses":"warehouses",
                   "opening_inventory":"inventory","purchase_orders":"purchase_orders",
                   "historical_demand":"historical_demand"}
        for filename in SCHEMAS:
            rows=load_reference_csv(client,args.project_id,f'data/generated/{csv_names[filename]}.csv',filename)
            print(f'Loaded {filename}: {rows} rows')
    for sql in ['sql/01_views.sql','sql/02_analytics.sql']:
        print('Applied:',sql,'BigQuery job:',apply_sql(client,args.project_id,sql))
    print('\nNEXT: Create a BigQuery subscription named aegis-to-bigquery on the topic above.')
    print('Destination table:',f'{args.project_id}.aegis_warehouse.raw_sales_events')
    print('Select: Write to BigQuery, Do NOT use a schema, do NOT enable Write metadata.')
    print('Pub/Sub service agent needs BigQuery Data Editor on destination dataset.')

if __name__=='__main__':main()
