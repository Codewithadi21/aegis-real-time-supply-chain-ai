"""Synthetic events and strict validation for the streaming system."""
from __future__ import annotations
from datetime import datetime, timezone
from uuid import uuid4


def new_sale(product_id='LAPTOP_001', warehouse_id='WH_IND_01', quantity=1, unit_price=75000.0):
    return {
        'event_id':str(uuid4()), 'event_type':'SALE',
        'product_id':product_id, 'warehouse_id':warehouse_id,
        'quantity':quantity, 'unit_price_inr':float(unit_price),
        'currency':'INR', 'event_timestamp':datetime.now(timezone.utc).isoformat()
    }


def validate_sale(data: dict):
    """Reject unsafe or malformed input, returning a normalized copy."""
    required={'event_id','event_type','product_id','warehouse_id','quantity','unit_price_inr','currency','event_timestamp'}
    missing=required-set(data)
    if missing:
        raise ValueError(f'Missing fields: {sorted(missing)}')
    if not isinstance(data['event_id'],str) or not data['event_id']:
        raise ValueError('Missing event_id')
    if data['event_type'] != 'SALE' or data['currency'] != 'INR':
        raise ValueError('Unsupported event type or currency')
    if not isinstance(data['quantity'],int) or isinstance(data['quantity'],bool) or data['quantity']<=0:
        raise ValueError('quantity must be a positive integer')
    if not isinstance(data['unit_price_inr'],(int,float)) or isinstance(data['unit_price_inr'],bool) or not (0 < data['unit_price_inr'] < 1e9):
        raise ValueError('Invalid price')
    if not all(isinstance(data[k],str) and data[k] for k in ('product_id','warehouse_id')):
        raise ValueError('Invalid dimension keys')
    datetime.fromisoformat(data['event_timestamp'].replace('Z','+00:00'))
    return dict(data)
