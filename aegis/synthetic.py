"""Reproducible SYNTHETIC consumer-electronics business datasets. No enterprise data."""
from __future__ import annotations
from pathlib import Path
from datetime import date, timedelta
import numpy as np
import pandas as pd


def generate(output_dir: str | Path = 'data/generated', seed: int = 42, days: int = 90):
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    products = pd.DataFrame([
        ('LAPTOP_001', 'Laptop Pro 14', 'Laptop', 'SUP_01', 75000, 52000),
        ('LAPTOP_002', 'Laptop Air 13', 'Laptop', 'SUP_01', 56000, 39000),
        ('PHONE_001', 'Phone Nova X', 'Phone', 'SUP_02', 39000, 24000),
        ('PHONE_002', 'Phone Nova Lite', 'Phone', 'SUP_02', 22000, 13500),
        ('TABLET_001', 'Tablet View 11', 'Tablet', 'SUP_03', 31000, 20500),
        ('TABLET_002', 'Tablet View Mini', 'Tablet', 'SUP_03', 19000, 11700),
    ], columns=['product_id','product_name','category','supplier_id','unit_price_inr','unit_cost_inr'])
    suppliers = pd.DataFrame([
        ('SUP_01','Northstar Components','India',7),
        ('SUP_02','BrightCore Electronics','Singapore',9),
        ('SUP_03','Horizon Devices','United Kingdom',6),
    ], columns=['supplier_id','supplier_name','country','nominal_lead_days'])
    warehouses = pd.DataFrame([
        ('WH_IND_01','Noida','India'),
        ('WH_IND_02','Gurugram','India'),
    ], columns=['warehouse_id','city','country'])
    inventory_rows=[]
    po_rows=[]
    for idx,p in products.iterrows():
        for wh in warehouses['warehouse_id']:
            # one low-stock example per product family
            opening = 35 if idx in (0,2) and wh=='WH_IND_01' else int(rng.integers(110,280))
            inventory_rows.append((p.product_id,wh,opening))
            po_rows.append((f'PO_{len(po_rows)+1:04d}',p.product_id,wh,p.supplier_id,
                            120 if idx in (0,2) else 80,4 if idx in (0,2) else 7))
    inventory=pd.DataFrame(inventory_rows,columns=['product_id','warehouse_id','opening_stock'])
    purchase_orders=pd.DataFrame(po_rows,columns=['po_id','product_id','warehouse_id','supplier_id','inbound_qty','arrival_in_days'])
    history_rows=[]
    start = date.today() - timedelta(days=days)
    for p in products.itertuples():
        for offset in range(days):
            d=start+timedelta(days=offset)
            promo=int(offset%19 in (0,1,2))
            weekend=int(d.weekday()>=5)
            baseline=5 if p.category=='Laptop' else (11 if p.category=='Phone' else 7)
            units=max(0,int(round(baseline+2*weekend+4*promo+rng.normal(0,2))))
            history_rows.append((d.isoformat(),p.product_id,int(d.isoweekday()),promo,p.unit_price_inr,units))
    history=pd.DataFrame(history_rows,columns=['sales_date','product_id','day_of_week','promo_flag','unit_price_inr','units_sold'])
    frames={'products':products,'suppliers':suppliers,'warehouses':warehouses,
            'inventory':inventory,'purchase_orders':purchase_orders,'historical_demand':history}
    for name, frame in frames.items():
        frame.to_csv(out/f'{name}.csv',index=False)
    return frames

if __name__ == '__main__':
    frames=generate()
    for name,frame in frames.items():
        print(f'{name:20s} {len(frame):>5} rows')
