import pandas as pd
import numpy as np
import os

_cache = {}

def load_jordan_data():
    if "jordan" in _cache:
        return _cache["jordan"]


    local_path = os.path.join(os.path.dirname(__file__), "data", "cars.csv")
    if os.path.exists(local_path):
        df = pd.read_csv(local_path)
    else:

        try:
            import kagglehub
            path = kagglehub.dataset_download("alzyood95/jordan-cars-market-2026")
            df = pd.read_csv(os.path.join(path, "cars.csv"))
        except Exception:
            df = _synthetic_jordan()

    df = _clean_jordan(df)
    _cache["jordan"] = df
    return df


def _clean_jordan(df):
    df = df.copy()
    df["Price_JOD"] = (
        df["Price"]
        .str.replace(" JOD", "", regex=False)
        .str.replace(",", "", regex=False)
        .astype(float, errors="ignore")
    )
    df["Price_JOD"] = pd.to_numeric(df["Price_JOD"], errors="coerce")
    df["Price_USD"] = df["Price_JOD"] * 1.41

    df["Mileage_clean"] = df["Mileage"].str.replace(r"[^\d\-]", "", regex=True)
    df.loc[df["Mileage_clean"] == "", "Mileage_clean"] = "0"
    split_vals = df["Mileage_clean"].str.split("-", expand=True)
    df["Mileage_From"] = pd.to_numeric(split_vals[0], errors="coerce")
    df["Mileage_To"] = pd.to_numeric(split_vals[1], errors="coerce")
    df["Mileage_To"] = df["Mileage_To"].fillna(df["Mileage_From"])
    df["Mileage_Avg"] = (df["Mileage_From"] + df["Mileage_To"]) / 2

    df.drop(columns=["Price", "Mileage", "Mileage_clean"], inplace=True, errors="ignore")
    df = df[df["Year"] != df["Year"].min()]

    df["Brand"] = df["Model"].str.split().str[0]
    df["City"] = df["Location"].str.split(",").str[0].str.strip()

    fuel_map = {
        "gasoline": "Gasoline", "Hybrid": "Hybrid", "hybrid": "Hybrid",
        "electricity": "Electric", "diesel": "Diesel",
        "undefined": "Other", "Diesel": "Diesel"
    }
    df["Fuel_Type"] = df["Fuel Type"].map(fuel_map).fillna("Other")

    # Filling in missing prices
    for idx in df[df["Price_USD"].isna()].index:
        row = df.loc[idx]
        similar = df[
            (df["Model"] == row["Model"]) & (df["Year"] == row["Year"]) &
            (df["Condition"] == row["Condition"]) & (df["Price_USD"].notna())
        ]
        df.loc[idx, "Price_USD"] = similar["Price_USD"].median() if not similar.empty else df["Price_USD"].median()

    df["Price_USD"] = pd.to_numeric(df["Price_USD"], errors="coerce")
    return df.dropna(subset=["Price_USD"])


def _synthetic_jordan():
    """Minimal fallback dataset."""
    np.random.seed(42)
    n = 500
    brands = ["Toyota", "Hyundai", "Kia", "Mercedes-Benz", "BMW", "Ford", "Nissan", "BYD"]
    cities = ["Amman", "Zarqa", "Irbid", "Salt", "Madaba"]
    fuels = ["Hybrid", "gasoline", "electricity", "diesel"]
    weights_city = [0.71, 0.12, 0.10, 0.04, 0.03]
    weights_fuel = [0.34, 0.44, 0.15, 0.05]
    rows = []
    for i in range(n):
        brand = np.random.choice(brands)
        yr = np.random.randint(2005, 2026)
        price_jod = np.random.lognormal(9.5, 0.8)
        miles = np.random.choice(["10,000 - 19,999 km", "50,000 - 59,999 km", "100,000 - 109,999 km", "0 km"])
        city = np.random.choice(cities, p=weights_city)
        fuel = np.random.choice(fuels, p=weights_fuel)
        rows.append({
            "ID": i + 1,
            "Model": f"{brand} Model{i}",
            "Year": yr,
            "Condition": np.random.choice(["used", "New (Zero)"]),
            "Fuel Type": fuel,
            "Mileage": miles,
            "Seller Type": "undefined",
            "Location": f"{city}, District",
            "Price": f"{price_jod:,.0f} JOD",
            "Insurance": "No insurance",
            "Transmission": "Automatic",
            "Color": np.random.choice(["white", "black", "beige", "silver"])
        })
    return pd.DataFrame(rows)


def get_kpis(df):
    return {
        "total_listings": len(df),
        "median_price_usd": df["Price_USD"].median(),
        "mean_price_usd": df["Price_USD"].mean(),
        "median_mileage": df["Mileage_Avg"].median() if "Mileage_Avg" in df.columns else 0,
        "top_brand": df["Brand"].value_counts().idxmax(),
        "top_city": df["City"].value_counts().idxmax(),
    }
