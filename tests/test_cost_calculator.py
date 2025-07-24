import pytest
from utils.cost_calculator import calc_material_cost, calc_energy_cost, calc_total_cost
from utils.business_logic import calc_depreciation, calc_labour, apply_fail_rate, calc_final_business_price

def test_calc_material_cost():
    # 10 cm³, density 1.24 g/cm³, $20/kg
    assert abs(calc_material_cost(10, 1.24, 20) - 0.248) < 1e-3

def test_calc_energy_cost():
    # 4 hr, 120W, $0.15/kWh
    assert abs(calc_energy_cost(4, 120, 0.15) - 0.072) < 1e-3

def test_calc_total_cost():
    # $0.25 material, $0.07 energy, 20% markup
    assert abs(calc_total_cost(0.25, 0.07, 20) - 0.384) < 1e-3 

def test_calc_depreciation():
    assert calc_depreciation(400, 2000, 10) == 2.0
    assert calc_depreciation(0, 2000, 10) == 0.0
    assert calc_depreciation(400, 0, 10) == 0.0  # zero lifespan

def test_calc_labour():
    assert calc_labour(0.5, 0.5, 10) == 10.0
    assert calc_labour(0, 0, 10) == 0.0
    assert calc_labour(1, 2, 0) == 0.0

def test_apply_fail_rate():
    assert apply_fail_rate(100, 10) == pytest.approx(111.1111, rel=1e-4)
    assert apply_fail_rate(100, 0) == 100.0
    assert apply_fail_rate(100, 100) == float('inf')  # 100% fail rate

def test_calc_final_business_price():
    # base_cost=100, fail_rate=10%, shipping=10, markup=20%
    base = 100
    fail = 10
    shipping = 10
    markup = 20
    adj = apply_fail_rate(base, fail) + shipping
    expected = adj * 1.2
    assert calc_final_business_price(base, fail, shipping, markup) == pytest.approx(expected, rel=1e-4) 