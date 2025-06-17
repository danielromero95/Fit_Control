# src/gui/gui_utils.py

import pandas as pd
from typing import Optional

METRICS_MAP = {
    'frame_index':      ['frame_idx', 'frame'],
    'left_knee_angle':  ['rodilla_izq'],
    'right_knee_angle': ['rodilla_der'],
}

def get_first_available_series(df: pd.DataFrame, logical_name: str) -> Optional[pd.Series]:
    for column_name in METRICS_MAP.get(logical_name, []):
        if column_name in df.columns:
            return df[column_name]
    return None