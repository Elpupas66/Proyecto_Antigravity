from __future__ import annotations

import pandas as pd

from utils.indicators import add_basic_indicators


class BVortexBaseStrategy:
    name = "bvortex_base"

    def __init__(
        self,
        atr_period: int = 14,
        threshold_long: float = -17,
        threshold_short: float = 17,
    ) -> None:
        self.atr_period = atr_period
        self.threshold_long = threshold_long
        self.threshold_short = threshold_short

    def prepare_data(self, df: pd.DataFrame) -> pd.DataFrame:
        out = add_basic_indicators(df, self.atr_period)
        return out

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        out = self.prepare_data(df)

        # Lógica provisional de laboratorio
        out["signal_long"] = out["BVortex_raw"] <= self.threshold_long
        out["signal_short"] = out["BVortex_raw"] >= self.threshold_short

        return out