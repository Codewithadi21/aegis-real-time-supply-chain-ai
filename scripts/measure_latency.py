"""Observe one synthetic event's Pub/Sub publish-to-BigQuery-query visibility time.

The measurement includes polling interval and BigQuery query execution time,
so it is NOT a server-side Pub/Sub delivery SLA or precise ingestion latency.
"""
import argparse
import json
import time
from google.cloud import bigquery, pubsub_v1
from aegis.events import new_sale
from aegis.gcp_free_utils import render_project_sql


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--project-id',required=True)
    parser.add_argument('--poll-seconds',type=float,default=4)
    parser.add_argument('--max-polls',type=int,default=12)
    args=parser.parse_args()
    render_project_sql('{{PROJECT_ID}}',args.project_id)
    if not 2 <= args.poll_seconds <= 15 or not 1 <= args.max_polls <= 15:
        parser.error('Limits: 2-15 seconds/poll; up to 15 BigQuery queries.')
    event=new_sale()
    topic=pubsub_v1.PublisherClient().topic_path(args.project_id,'aegis-sales-events')
    publisher=pubsub_v1.PublisherClient()
    client=bigquery.Client(project=args.project_id)
    started=time.perf_counter()
    pub_id=publisher.publish(topic,json.dumps(event).encode('utf8')).result(timeout=30)
    print('Published message:',pub_id, 'event_id:',event['event_id'])
    sql=f'SELECT COUNT(*) n FROM `{args.project_id}.aegis_warehouse.raw_sales_events` WHERE JSON_VALUE(SAFE.PARSE_JSON(data), "$.event_id")=@eid'
    job_config=bigquery.QueryJobConfig(query_parameters=[bigquery.ScalarQueryParameter('eid','STRING',event['event_id'])])
    for i in range(args.max_polls):
        time.sleep(args.poll_seconds)
        n=list(client.query(sql,job_config=job_config,location='US').result())[0].n
        if n:
            print(f'Observed in BigQuery after {time.perf_counter()-started:.1f}s '
                  '(includes polling + query time, not a guaranteed ingestion latency).')
            return
        print('Poll',i+1,': event not queryable yet')
    print('Event not observed within polling window. Check subscription status and errors.')

if __name__=='__main__':main()
