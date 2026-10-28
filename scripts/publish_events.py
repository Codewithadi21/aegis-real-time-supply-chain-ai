"""Publish reproducible sample volume; optional replay tests idempotent reporting."""
import argparse
import json
import random
import time
from google.cloud import pubsub_v1
from aegis.events import new_sale
from aegis.gcp import safe_project_id,TOPIC


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--project-id',required=True)
    p.add_argument('--count',type=int,default=20)
    p.add_argument('--interval',type=float,default=0.25)
    p.add_argument('--replay-first',action='store_true')
    a=p.parse_args()
    safe_project_id(a.project_id)
    if not 1 <= a.count <= 1000 or not 0 <= a.interval <= 10:
        p.error('For cost control, count must be 1-1000 and interval 0-10 seconds.')
    publisher=pubsub_v1.PublisherClient()
    topic=publisher.topic_path(a.project_id,TOPIC)
    rng=random.Random(42)
    ids=['LAPTOP_001','LAPTOP_002','PHONE_001','PHONE_002','TABLET_001','TABLET_002']
    prices={'LAPTOP_001':75000,'LAPTOP_002':56000,'PHONE_001':39000,'PHONE_002':22000,'TABLET_001':31000,'TABLET_002':19000}
    first=None
    for i in range(a.count):
        product=rng.choice(ids)
        event=new_sale(product_id=product,warehouse_id=rng.choice(['WH_IND_01','WH_IND_02']),quantity=rng.randint(1,3),unit_price=prices[product])
        if first is None: first=event
        mid=publisher.publish(topic,json.dumps(event).encode('utf8')).result(timeout=30)
        print(f'{i+1}/{a.count}  {event["product_id"]} x{event["quantity"]} -> {mid}')
        if a.interval:time.sleep(a.interval)
    if a.replay_first:
        mid=publisher.publish(topic,json.dumps(first).encode('utf8')).result(timeout=30)
        print('REPLAY same event_id (deduplication test):',mid)

if __name__=='__main__':main()
