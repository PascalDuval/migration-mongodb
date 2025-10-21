import pandas as pd
from scripts.migration_crud import _safe_int, _to_datetime, convert_dataframe_types
from datetime import datetime


def test_safe_int():
    assert _safe_int('42') == 42
    assert _safe_int(42.0) == 42
    assert _safe_int('42.9') == 42
    assert _safe_int(None) is None
    assert _safe_int('abc') is None


def test_to_datetime():
    d = _to_datetime('2020-01-02')
    assert isinstance(d, datetime)
    assert d.year == 2020 and d.month == 1 and d.day == 2

    d2 = _to_datetime('02/01/2020')
    assert d2 is not None

    assert _to_datetime(None) is None
    assert _to_datetime('not a date') is None


def test_convert_dataframe_types():
    df = pd.DataFrame([
        {'Name': 'A', 'Age': '30', 'Date of Admission': '2020-01-01'},
        {'Name': 'B', 'Age': '', 'Date of Admission': ''},
    ])

    records = convert_dataframe_types(df)
    assert len(records) == 2
    assert records[0]['Age'] == 30
    assert records[0]['Date of Admission'].year == 2020
    assert records[1]['Age'] is None
    assert records[1]['Date of Admission'] is None
