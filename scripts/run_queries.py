import argparse
from google.cloud import bigquery
from aegis.gcp import safe_project_id

def main():
    p=argparse.ArgumentParser();p.add_argument('--project-id',required=True);args=p.parse_args()
    client=bigquery.Client(project=safe_project_id(args.project_id))
    for label, view in [('Raw Pub/Sub messages','raw_sales_events'),('Validated unique sales','v_valid_sales'),('Rejected events','v_invalid_sales')]:
        result=list(client.query(f'SELECT COUNT(*) AS n FROM `{args.project_id}.aegis_warehouse.{view}`',location='US').result())
        print(label,':',result[0].n)
    print('\nInventory at risk:')
    sql=(f"SELECT product_id,warehouse_id,remaining_stock,estimated_days_cover "
         f"FROM `{args.project_id}.aegis_warehouse.v_stock_risk` "
         "ORDER BY estimated_days_cover ASC LIMIT 6")
    for row in client.query(sql,location='US').result():print(dict(row))

if __name__=='__main__':main()
