import json
import pytest
from aegis.events import new_sale,validate_sale
from aegis.risk import scenario
from aegis.gcp_free_utils import render_project_sql

def test_currency_rejection():
    d=new_sale();d['currency']='USD'
    with pytest.raises(ValueError):validate_sale(d)

def test_missing_key_rejected():
    d=new_sale();del d['product_id']
    with pytest.raises(ValueError):validate_sale(d)

def test_scenario_no_shipment_before_horizon():
    result=scenario(opening_stock=0,daily_demand=2,inbound_qty=20,arrival_day=50,horizon=5,unit_price_inr=10)
    assert result['unfulfilled_units']==10
    assert result['potential_revenue_exposure_inr']==100

def test_sql_project_safety():
    assert render_project_sql('SELECT "{{PROJECT_ID}}"','aegis-cloud-123') == 'SELECT "aegis-cloud-123"'
    with pytest.raises(ValueError):render_project_sql('{{PROJECT_ID}}','bad`project')
