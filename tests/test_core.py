from aegis.synthetic import generate
from aegis.events import validate_sale,new_sale
from aegis.risk import scenario,decision_replay
from aegis.retrieval import search_policies
import pytest


def test_generator_keys_and_relations(tmp_path):
    x=generate(tmp_path)
    assert len(x['products'])==6
    assert x['products']['product_id'].is_unique
    assert x['suppliers']['supplier_id'].is_unique
    assert set(x['inventory']['product_id']).issubset(set(x['products']['product_id']))
    assert len(x['historical_demand'])==6*90


def test_event_validation():
    event=new_sale()
    assert validate_sale(event)['event_type']=='SALE'
    event['quantity']=-1
    with pytest.raises(ValueError):validate_sale(event)


def test_scenario_delay_increases_or_preserves_exposure():
    cases=decision_replay()
    assert len(cases)==4
    assert cases[0]['incremental_exposure_inr']==0
    assert all(x['incremental_exposure_inr']>=0 for x in cases)
    assert [x['potential_revenue_exposure_inr'] for x in cases] == sorted(x['potential_revenue_exposure_inr'] for x in cases)


def test_delivered_before_demand():
    a=scenario(opening_stock=0,daily_demand=5,inbound_qty=10,arrival_day=1,horizon=2,unit_price_inr=2)
    assert a['potential_revenue_exposure_inr']==0


def test_policies():
    r=search_policies('supplier seven days late escalation approval')
    assert r and all('source' in x for x in r)
