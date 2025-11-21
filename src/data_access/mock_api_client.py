import pandas as pd
from typing import Optional, Union
from datetime import date, datetime

from src.data_access.columns import ALL_COLUMNS

class MockApiClient:
    def __init__(self, csv_path: str = "transactions_faked.csv") -> None:
        # Load the already anonymized CSV
        self._df = pd.read_csv(csv_path, encoding="cp1252", sep=";")

        # Sanity check: all required columns present
        missing = [c for c in ALL_COLUMNS if c not in self._df.columns]
        if missing:
            raise ValueError(f"Missing columns in CSV: {missing}")

        # Keep only the relevant columns, in the right order
        self._df = self._df[ALL_COLUMNS].copy()

        # Prepare a parsed date column for filtering
        self._df["_date"] = pd.to_datetime(
            self._df["Getätigt am Datum"], errors="coerce", dayfirst=True
        )

    # ------------------------------------------------------------------ #
    # 1) Donors: one row per Kontakt-ID, with ALL columns kept
    #    (values taken from the first transaction chronologically)
    # ------------------------------------------------------------------ #
    def get_donors(self) -> pd.DataFrame:
        """
        Return one row per donor (Kontakt-ID).

        All original columns are included. If a donor has multiple
        transactions, the values from the earliest transaction
        (Getätigt am Datum) are used.
        """
        # Sort so "first" is the earliest donation
        df_sorted = self._df.sort_values("_date")

        donors = df_sorted.drop_duplicates(subset=["Kontakt-ID"], keep="first")

        # Return without helper column
        return donors[ALL_COLUMNS].reset_index(drop=True)

    # ------------------------------------------------------------------ #
    # 2) Donations: one row per transaction, optional date filtering
    # ------------------------------------------------------------------ #
    def get_donations(
        self,
        since: Optional[Union[str, date, datetime]] = None,
        until: Optional[Union[str, date, datetime]] = None,
    ) -> pd.DataFrame:
        """
        Return all donations (one row per transaction), optionally filtered
        by Getätigt am Datum.

        since / until can be:
        - string (e.g. "2022-01-01")
        - datetime.date
        - datetime.datetime
        """
        df = self._df.copy()

        # Convert since/until to pandas timestamps if provided
        if since is not None:
            since_ts = pd.to_datetime(since)
            df = df[df["_date"] >= since_ts]

        if until is not None:
            until_ts = pd.to_datetime(until)
            df = df[df["_date"] <= until_ts]

        # Return with all original columns (no helper column)
        return df[ALL_COLUMNS].reset_index(drop=True)
