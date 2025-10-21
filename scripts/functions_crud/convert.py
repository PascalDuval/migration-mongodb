from typing import Any, Optional, List, Dict
from datetime import datetime
import pandas as pd


def _safe_int(value: Any) -> Optional[int]:
    try:
        if pd.isna(value):
            return None
        return int(float(value))
    except Exception:
        return None


def _to_datetime(value: Any) -> Optional[datetime]:
    if value is None:
        return None
    try:
        import pandas as _pd

        if isinstance(value, _pd.Timestamp):
            if pd.isna(value):
                return None
            return value.to_pydatetime()
    except Exception:
        pass

    try:
        ts = pd.to_datetime(value, errors="coerce", dayfirst=False)
        if pd.isna(ts):
            return None
        return ts.to_pydatetime()
    except Exception:
        return None


def convert_dataframe_types(df: pd.DataFrame) -> List[Dict[str, Any]]:
    df2 = df.copy()

    if "Age" in df2.columns:
        df2["Age"] = pd.to_numeric(df2["Age"], errors="coerce").astype(pd.Int64Dtype())

    if "Date of Admission" in df2.columns:
        df2["Date of Admission"] = pd.to_datetime(df2["Date of Admission"], errors="coerce")

    records: List[Dict[str, Any]] = []
    for _, row in df2.iterrows():
        doc: Dict[str, Any] = {}
        for k, v in row.items():
            if pd.isna(v):
                doc[k] = None
                continue

            if k == "Age":
                doc[k] = _safe_int(v)
            elif k == "Date of Admission":
                doc[k] = _to_datetime(v)
            else:
                doc[k] = v

        records.append(doc)
    return records
