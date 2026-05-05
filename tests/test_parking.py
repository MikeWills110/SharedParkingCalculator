"""Unit and integration tests for SharedParkingCalculator."""
import os, sys
from unittest.mock import patch
import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from LandUse import _compute_parking, _reshape_data, parking_demand, MONTHS, TIMES

HOURS = [str(i) for i in range(24)]
_CUST_TOD = [0.0]*6 + [0.1,0.3,0.6,0.8,0.9,1.0,0.9,0.8,0.7,0.5,0.3,0.1] + [0.0]*6
_EMP_TOD = [0.0]*6 + [0.0,0.2,0.8,0.9,0.95,1.0,0.95,0.9,0.85,0.7,0.4,0.1] + [0.0]*6

@pytest.fixture
def base_demand():
    return pd.DataFrame({"Weekday":[100],"Weekend":[50]}, index=["Office"])

@pytest.fixture
def split():
    return pd.DataFrame({"CustomerWeekday":[0.3],"EmployeeWeekday":[0.7],"CustomerWeekend":[0.5],"EmployeeWeekend":[0.5]}, index=["Office"])

@pytest.fixture
def tod():
    return pd.DataFrame([_CUST_TOD,_EMP_TOD], index=["OfficeCustomer","OfficeEmployee"], columns=HOURS)

@pytest.fixture
def noncaptive():
    return pd.DataFrame([[1.0]*24,[1.0]*24], index=["OfficeCustomer","OfficeEmployee"], columns=HOURS)

@pytest.fixture
def monthly():
    return pd.DataFrame([[1.0]*12,[1.0]*12], index=["OfficeCustomer","OfficeEmployee"], columns=MONTHS)

class TestComputeParking:
    def test_returns_12(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        assert len(r) == 12

    def test_row_length(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        for row in r:
            assert len(row) == 25

    def test_months(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        assert [row[-1] for row in r] == MONTHS

    def test_hour9(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        assert r[0][9] == 87

    def test_peak_hour11(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        assert r[0][11] == 100

    def test_overnight_zero(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        for h in range(6):
            assert r[0][h] == 0

    def test_weekend(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekend",base_demand,split,tod,noncaptive,monthly)
        assert r[0][11] == 50

    def test_flat_months(self, base_demand, split, tod, noncaptive, monthly):
        r = _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)
        jan = r[0][:-1]
        for row in r[1:]:
            assert row[:-1] == jan

class TestReshapeData:
    def _mk(self, base_demand, split, tod, noncaptive, monthly):
        return {"Office": _compute_parking("Office","Weekday",base_demand,split,tod,noncaptive,monthly)}

    def test_288(self, base_demand, split, tod, noncaptive, monthly):
        assert _reshape_data(self._mk(base_demand,split,tod,noncaptive,monthly)).shape[0] == 288

    def test_total(self, base_demand, split, tod, noncaptive, monthly):
        df = _reshape_data(self._mk(base_demand,split,tod,noncaptive,monthly))
        pd.testing.assert_series_equal(df["Total"], df["Office"], check_names=False)

    def test_index(self, base_demand, split, tod, noncaptive, monthly):
        df = _reshape_data(self._mk(base_demand,split,tod,noncaptive,monthly))
        assert list(df.index.names) == ["Month","Time"]

class TestIntegration:
    @pytest.fixture(autouse=True)
    def _reset(self):
        import LandUse; LandUse._data_cache = None
        yield
        import LandUse; LandUse._data_cache = None

    def test_weekday(self):
        with patch("sys.argv",["t","--dir","."]):
            r = parking_demand("Weekday")
        assert r.shape[0] == 288 and "Total" in r.columns

    def test_weekend(self):
        with patch("sys.argv",["t","--dir","."]):
            r = parking_demand("Weekend")
        assert r.shape[0] == 288 and "Total" in r.columns

    def test_no_negative(self):
        with patch("sys.argv",["t","--dir","."]):
            r = parking_demand("Weekday")
        assert (r >= 0).all().all()

    def test_peak_positive(self):
        with patch("sys.argv",["t","--dir","."]):
            r = parking_demand("Weekday")
        assert r["Total"].max() > 0
