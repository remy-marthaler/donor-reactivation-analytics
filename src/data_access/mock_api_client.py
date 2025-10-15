
import pandas as pd
from datetime import datetime, timedelta
import numpy as np

class MockApiClient:
    """Lightweight mock returning synthetic data for local development."""
    def __init__(self, n_donors: int = 200):
        self.n = n_donors
        self._rng = np.random.default_rng(42)

    def get_donors(self) -> pd.DataFrame:
        ids = [f"D{str(i).zfill(5)}" for i in range(self.n)]
        return pd.DataFrame({ "Kontakt-ID": ids })

    def get_donations(self, since=None, until=None) -> pd.DataFrame:
        # Generate synthetic transactions for the last 3 years
        now = datetime.utcnow().date()
        start = now - timedelta(days=3*365)
        dates = pd.date_range(start, now, freq="D")

        rows = []
        for i in range(self.n):
            donor = f"D{str(i).zfill(5)}"
            # Poisson number of donations
            k = self._rng.poisson(8)
            sample_dates = self._rng.choice(dates, size=k, replace=False)
            for d in sample_dates:
                amt = float(self._rng.choice([20,30,50,80,100,150,200]))
                rows.append((donor, d.date(), amt))

        df = pd.DataFrame(rows, columns=["Kontakt-ID","Getätigt am Datum","Betrag"])
        if since:
            df = df[pd.to_datetime(df["Getätigt am Datum"]) >= pd.to_datetime(since)]
        if until:
            df = df[pd.to_datetime(df["Getätigt am Datum"]) < pd.to_datetime(until)]
        return df
