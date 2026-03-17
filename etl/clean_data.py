import os
import pandas as pd


# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")

os.makedirs(PROCESSED_DATA_PATH, exist_ok=True)


# =========================
# HELPERS
# =========================
def standardize_channel(value: str) -> str:
    if pd.isna(value):
        return "Desconocido"

    value = str(value).strip().lower()

    mapping = {
        "mercado libre": "Mercado Libre",
        "instagram": "Instagram",
        "web": "Web",
        "facebook": "Facebook",
    }

    return mapping.get(value, "Otro")


def classify_sentiment(text: str) -> str:
    if pd.isna(text):
        return "neutral"

    text = str(text).strip().lower()

    positive_keywords = [
        "excelente",
        "muy buena",
        "impecable",
        "recomendable",
        "volvería",
        "rápida",
        "antes de lo esperado",
    ]

    negative_keywords = [
        "mala",
        "defectuoso",
        "tardó",
        "no respondieron",
        "dañado",
        "mala experiencia",
        "no cumplió",
    ]

    for word in positive_keywords:
        if word in text:
            return "positive"

    for word in negative_keywords:
        if word in text:
            return "negative"

    return "neutral"


# =========================
# LOAD
# =========================
sales = pd.read_csv(os.path.join(RAW_DATA_PATH, "ventas.csv"), encoding="utf-8-sig")
marketing = pd.read_csv(os.path.join(RAW_DATA_PATH, "marketing.csv"), encoding="utf-8-sig")
sellers = pd.read_csv(os.path.join(RAW_DATA_PATH, "sellers.csv"), encoding="utf-8-sig")
comments = pd.read_csv(os.path.join(RAW_DATA_PATH, "comments.csv"), encoding="utf-8-sig")


# =========================
# CLEAN SALES
# =========================
sales["order_date"] = pd.to_datetime(sales["order_date"], errors="coerce")
sales["channel"] = sales["channel"].apply(standardize_channel)
sales["payment_status"] = sales["payment_status"].astype(str).str.strip().str.lower()

numeric_sales_cols = ["quantity", "unit_price", "discount", "total_amount"]
for col in numeric_sales_cols:
    sales[col] = pd.to_numeric(sales[col], errors="coerce")

sales = sales.drop_duplicates(subset=["order_id"])
sales = sales.dropna(subset=["order_id", "order_date", "customer_id", "product_id"])

sales = sales[sales["quantity"] > 0]
sales = sales[sales["unit_price"] > 0]
sales = sales[sales["total_amount"] >= 0]

sales["gross_amount"] = sales["quantity"] * sales["unit_price"]
sales["discount_amount"] = sales["gross_amount"] * sales["discount"]
sales["year"] = sales["order_date"].dt.year
sales["month"] = sales["order_date"].dt.month
sales["year_month"] = sales["order_date"].dt.strftime("%Y-%m")


# =========================
# CLEAN MARKETING
# =========================
marketing["date"] = pd.to_datetime(marketing["date"], errors="coerce")
marketing["channel"] = marketing["channel"].apply(standardize_channel)

numeric_marketing_cols = ["impressions", "clicks", "spend", "conversions"]
for col in numeric_marketing_cols:
    marketing[col] = pd.to_numeric(marketing[col], errors="coerce")

marketing = marketing.dropna(subset=["date", "channel"])
marketing = marketing.drop_duplicates()

marketing = marketing[marketing["impressions"] >= 0]
marketing = marketing[marketing["clicks"] >= 0]
marketing = marketing[marketing["spend"] >= 0]
marketing = marketing[marketing["conversions"] >= 0]

marketing["ctr"] = (marketing["clicks"] / marketing["impressions"]).fillna(0)
marketing["cpc"] = (marketing["spend"] / marketing["clicks"]).fillna(0)
marketing["cpa"] = (marketing["spend"] / marketing["conversions"]).fillna(0)
marketing["year_month"] = marketing["date"].dt.strftime("%Y-%m")


# =========================
# CLEAN SELLERS
# =========================
sellers = sellers.drop_duplicates(subset=["seller_id"])
sellers["target_sales"] = pd.to_numeric(sellers["target_sales"], errors="coerce")
sellers["seller_name"] = sellers["seller_name"].astype(str).str.strip()
sellers["team"] = sellers["team"].astype(str).str.strip()
sellers["region"] = sellers["region"].astype(str).str.strip()

sellers = sellers.dropna(subset=["seller_id", "seller_name"])
sellers = sellers[sellers["target_sales"] > 0]


# =========================
# CLEAN COMMENTS
# =========================
comments["date"] = pd.to_datetime(comments["date"], errors="coerce")
comments["channel"] = comments["channel"].apply(standardize_channel)
comments["comment_text"] = comments["comment_text"].astype(str).str.strip()

comments = comments.drop_duplicates(subset=["comment_id"])
comments = comments.dropna(subset=["comment_id", "date", "comment_text"])

comments["sentiment"] = comments["comment_text"].apply(classify_sentiment)
comments["year_month"] = comments["date"].dt.strftime("%Y-%m")


# =========================
# KPI TABLES
# =========================
sales_by_channel = (
    sales.groupby("channel", as_index=False)
    .agg(
        total_sales=("total_amount", "sum"),
        total_orders=("order_id", "nunique"),
        total_quantity=("quantity", "sum"),
        avg_ticket=("total_amount", "mean"),
    )
)

sales_by_seller = (
    sales.groupby(["seller_id", "seller_name"], as_index=False)
    .agg(
        total_sales=("total_amount", "sum"),
        total_orders=("order_id", "nunique"),
        total_quantity=("quantity", "sum"),
    )
    .merge(sellers[["seller_id", "target_sales", "team", "region"]], on="seller_id", how="left")
)

sales_by_seller["target_achievement_pct"] = (
    sales_by_seller["total_sales"] / sales_by_seller["target_sales"]
).fillna(0)

sales_monthly = (
    sales.groupby("year_month", as_index=False)
    .agg(
        total_sales=("total_amount", "sum"),
        total_orders=("order_id", "nunique"),
        total_quantity=("quantity", "sum"),
    )
)

marketing_by_channel = (
    marketing.groupby("channel", as_index=False)
    .agg(
        total_spend=("spend", "sum"),
        total_clicks=("clicks", "sum"),
        total_conversions=("conversions", "sum"),
        total_impressions=("impressions", "sum"),
    )
)

sentiment_summary = (
    comments.groupby("sentiment", as_index=False)
    .agg(total_comments=("comment_id", "count"))
)

# ROI simple por canal
sales_channel_totals = (
    sales.groupby("channel", as_index=False)
    .agg(total_sales=("total_amount", "sum"))
)

channel_performance = sales_channel_totals.merge(marketing_by_channel, on="channel", how="left")
channel_performance["roi"] = (
    (channel_performance["total_sales"] - channel_performance["total_spend"])
    / channel_performance["total_spend"]
).fillna(0)


# =========================
# SAVE
# =========================
sales.to_csv(os.path.join(PROCESSED_DATA_PATH, "sales_clean.csv"), index=False, encoding="utf-8-sig")
marketing.to_csv(os.path.join(PROCESSED_DATA_PATH, "marketing_clean.csv"), index=False, encoding="utf-8-sig")
sellers.to_csv(os.path.join(PROCESSED_DATA_PATH, "sellers_clean.csv"), index=False, encoding="utf-8-sig")
comments.to_csv(os.path.join(PROCESSED_DATA_PATH, "comments_clean.csv"), index=False, encoding="utf-8-sig")

sales_by_channel.to_csv(os.path.join(PROCESSED_DATA_PATH, "sales_by_channel.csv"), index=False, encoding="utf-8-sig")
sales_by_seller.to_csv(os.path.join(PROCESSED_DATA_PATH, "sales_by_seller.csv"), index=False, encoding="utf-8-sig")
sales_monthly.to_csv(os.path.join(PROCESSED_DATA_PATH, "sales_monthly.csv"), index=False, encoding="utf-8-sig")
marketing_by_channel.to_csv(os.path.join(PROCESSED_DATA_PATH, "marketing_by_channel.csv"), index=False, encoding="utf-8-sig")
sentiment_summary.to_csv(os.path.join(PROCESSED_DATA_PATH, "sentiment_summary.csv"), index=False, encoding="utf-8-sig")
channel_performance.to_csv(os.path.join(PROCESSED_DATA_PATH, "channel_performance.csv"), index=False, encoding="utf-8-sig")

print("✅ ETL completado correctamente")
print(f"Archivos guardados en: {PROCESSED_DATA_PATH}")