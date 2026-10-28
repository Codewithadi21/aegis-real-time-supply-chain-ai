"""Deterministic scenario simulator. Exposure means hypothetical missed sales, not realized loss."""
from __future__ import annotations


def scenario(opening_stock: int, daily_demand: float, inbound_qty: int,
             arrival_day: int, horizon: int = 14, unit_price_inr: float = 75000.):
    if opening_stock < 0 or daily_demand < 0 or inbound_qty < 0 or horizon <= 0 or arrival_day < 1 or unit_price_inr < 0:
        raise ValueError('invalid scenario input')
    stock=float(opening_stock)
    missed=0.0
    first_stockout=None
    for day in range(1,horizon+1):
        if day==arrival_day:
            stock += inbound_qty
        short=max(0.0,daily_demand-stock)
        if short and first_stockout is None:
            first_stockout=day
        missed += short
        stock=max(0.0,stock-daily_demand)
    return {'arrival_day':arrival_day,'horizon_days':horizon,'first_stockout_day':first_stockout,
            'unfulfilled_units':round(missed,2),'potential_revenue_exposure_inr':round(missed*unit_price_inr,2),
            'ending_stock':round(stock,2)}


def decision_replay(opening_stock=35,daily_demand=6,inbound_qty=120,arrival_day=4,
                    delays=(0,3,7,14),horizon=21,unit_price_inr=75000):
    baseline=scenario(opening_stock,daily_demand,inbound_qty,arrival_day,horizon,unit_price_inr)
    results=[]
    for delay in delays:
        s=scenario(opening_stock,daily_demand,inbound_qty,arrival_day+delay,horizon,unit_price_inr)
        s['delay_days']=delay
        s['incremental_exposure_inr']=round(max(0,s['potential_revenue_exposure_inr']-baseline['potential_revenue_exposure_inr']),2)
        results.append(s)
    return results
