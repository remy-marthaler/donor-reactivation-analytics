import pandas as pd
import streamlit as st

from src.core.state import get_api_client

st.caption("This page will segment donors into clusters once implemented.")

st.info("TODO: Implement things that segments donors into interesting groups/charts and visualize them.")


#chatgpt test
import streamlit as st
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

from src.core.state import get_api_client
from src.core.layout import sidebar_footer

# ----- Layout -----
sidebar_footer()
st.title("🧩 Segmentation")
st.caption("Segmentiert Spender in Cluster, um Outreach zu priorisieren.")

api = get_api_client()

# =========================================================
# Schritt A: Daten laden
# =========================================================
# Passe diese Calls an eure API an
donations = api.get_donations()  # erwartet Liste von Dicts
# donors = api.get_donors()      # optional, falls ihr Kontaktdaten getrennt habt

df = pd.DataFrame(donations)

# =========================================================
# Schritt B: Validieren + Cleanen
# =========================================================
required_cols = {"donor_id", "donation_date", "amount"}
if not required_cols.issubset(df.columns):
    st.error(f"Fehlende Spalten. Benötigt: {required_cols}")
    st.stop()

df["donation_date"] = pd.to_datetime(df["donation_date"], errors="coerce")
df["amount"] = pd.to_numeric(df["amount"], errors="coerce")

df = df.dropna(subset=["donor_id", "donation_date", "amount"])
df = df[df["amount"] > 0]

if df.empty:
    st.warning("Keine gültigen Spenden gefunden.")
    st.stop()

# =========================================================
# Schritt C: RFM Features pro Spender
# =========================================================
ref_date = df["donation_date"].max()  # Referenz = letzter Spendenzeitpunkt im Datensatz

rfm = (
    df.groupby("donor_id")
    .agg(
        recency_days=("donation_date", lambda x: (ref_date - x.max()).days),
        frequency=("donation_date", "count"),
        monetary_total=("amount", "sum"),
        monetary_avg=("amount", "mean"),
        first_date=("donation_date", "min"),
        last_date=("donation_date", "max"),
    )
    .reset_index()
)

rfm["span_days"] = (rfm["last_date"] - rfm["first_date"]).dt.days.clip(lower=0)

# =========================================================
# Schritt D: Transform + Scaling
# =========================================================
features = rfm[["recency_days", "frequency", "monetary_total"]].copy()
features["frequency"] = np.log1p(features["frequency"])
features["monetary_total"] = np.log1p(features["monetary_total"])

scaler = StandardScaler()
X = scaler.fit_transform(features)

# =========================================================
# Schritt E: K wählen + KMeans fitten
# =========================================================
k = st.sidebar.slider("Anzahl Cluster (k)", 2, 8, 4)

if len(rfm) < k:
    st.warning(f"Zu wenige Spender ({len(rfm)}) für k={k}. Bitte k reduzieren.")
    st.stop()

km = KMeans(n_clusters=k, random_state=42, n_init="auto")
rfm["cluster"] = km.fit_predict(X)

# =========================================================
# Schritt F: Cluster Summary + Segmentnamen
# =========================================================
summary = (
    rfm.groupby("cluster")
    .agg(
        donors=("donor_id", "count"),
        recency_mean=("recency_days", "mean"),
        frequency_mean=("frequency", "mean"),
        monetary_mean=("monetary_total", "mean"),
    )
    .reset_index()
)

# Original-Skala approx zurückrechnen (für bessere Lesbarkeit)
summary["frequency_mean"] = np.expm1(summary["frequency_mean"])
summary["monetary_mean"] = np.expm1(summary["monetary_mean"])

rec_q  = summary["recency_mean"].quantile([0.33, 0.67])
freq_q = summary["frequency_mean"].quantile([0.33, 0.67])
mon_q  = summary["monetary_mean"].quantile([0.33, 0.67])

def label_cluster(row):
    # Champions: sehr kürzlich, sehr häufig, sehr viel
    if (row["recency_mean"] <= rec_q.loc[0.33] and
        row["frequency_mean"] >= freq_q.loc[0.67] and
        row["monetary_mean"] >= mon_q.loc[0.67]):
        return "Champions / Core Supporters"

    # Recent one-timers: kürzlich, aber selten + wenig
    if (row["recency_mean"] <= rec_q.loc[0.33] and
        row["frequency_mean"] <= freq_q.loc[0.33]):
        return "Recent One-Timers"

    # Lapsed big donors: lange her, aber hoher Betrag
    if (row["recency_mean"] >= rec_q.loc[0.67] and
        row["monetary_mean"] >= mon_q.loc[0.67]):
        return "Lapsed Big Donors"

    # Lost donors: lange her, selten
    if (row["recency_mean"] >= rec_q.loc[0.67] and
        row["frequency_mean"] <= freq_q.loc[0.33]):
        return "Lost Donors"

    return "Potential Loyalists"

summary["segment"] = summary.apply(label_cluster, axis=1)
rfm = rfm.merge(summary[["cluster", "segment"]], on="cluster", how="left")

# =========================================================
# Schritt G: Anzeigen + Visualisieren
# =========================================================
st.subheader("Cluster-Übersicht")
st.dataframe(summary.sort_values("segment"))

pca = PCA(n_components=2, random_state=42)
X2 = pca.fit_transform(X)

plot_df = pd.DataFrame(X2, columns=["PC1", "PC2"])
plot_df["cluster"] = rfm["cluster"]
plot_df["segment"] = rfm["segment"]

st.subheader("Cluster-Map (PCA)")
st.scatter_chart(plot_df, x="PC1", y="PC2", color="cluster")

st.subheader("Clustergrößen")
cluster_sizes = rfm["segment"].value_counts().reset_index()
cluster_sizes.columns = ["segment", "count"]
st.bar_chart(cluster_sizes, x="segment", y="count")

# =========================================================
# Schritt H: Target List (Business Output)
# =========================================================
st.subheader("Target-Liste für Outreach")

default_targets = [s for s in ["Champions / Core Supporters", "Potential Loyalists"]
                   if s in rfm["segment"].unique()]

target_segments = st.multiselect(
    "Welche Segmente sollen angezeigt werden?",
    options=sorted(rfm["segment"].unique()),
    default=default_targets
)

targets = rfm[rfm["segment"].isin(target_segments)].copy()
targets = targets.sort_values(
    ["recency_days", "frequency", "monetary_total"],
    ascending=[True, False, False]
)

st.dataframe(
    targets[[
        "donor_id", "segment", "recency_days",
        "frequency", "monetary_total", "monetary_avg", "span_days"
    ]]
)

st.info(
    "Interpretation: kleine Recency + hohe Frequency = sehr wahrscheinlich wieder spendebereit. "
    "Diese Personen priorisieren (Danke-Mail, Karte, persönlicher Kontakt)."
)