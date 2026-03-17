import os
import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# =========================
# CONFIG
# =========================
N_ORDERS = 2000
N_COMMENTS = 300
N_CUSTOMERS = 500
N_PRODUCTS = 20
N_SELLERS = 10
DAYS_BACK_SALES = 180
DAYS_BACK_COMMENTS = 90

CHANNELS = ["Mercado Libre", "Instagram", "Web", "Facebook"]
PAYMENT_STATUS = ["paid", "pending"]

PRODUCT_CATALOG = [
    {"product_id": 1, "product_name": "Zapatillas Urban", "category": "Calzado"},
    {"product_id": 2, "product_name": "Zapatillas Running", "category": "Calzado"},
    {"product_id": 3, "product_name": "Remera Básica", "category": "Ropa"},
    {"product_id": 4, "product_name": "Remera Oversize", "category": "Ropa"},
    {"product_id": 5, "product_name": "Pantalón Chino", "category": "Ropa"},
    {"product_id": 6, "product_name": "Pantalón Cargo", "category": "Ropa"},
    {"product_id": 7, "product_name": "Campera Rompeviento", "category": "Ropa"},
    {"product_id": 8, "product_name": "Campera Denim", "category": "Ropa"},
    {"product_id": 9, "product_name": "Gorra Classic", "category": "Accesorios"},
    {"product_id": 10, "product_name": "Mochila City", "category": "Accesorios"},
    {"product_id": 11, "product_name": "Buzo Hoodie", "category": "Ropa"},
    {"product_id": 12, "product_name": "Short Deportivo", "category": "Ropa"},
    {"product_id": 13, "product_name": "Medias Training", "category": "Accesorios"},
    {"product_id": 14, "product_name": "Cinturón Casual", "category": "Accesorios"},
    {"product_id": 15, "product_name": "Botas Trekking", "category": "Calzado"},
    {"product_id": 16, "product_name": "Sandalias Beach", "category": "Calzado"},
    {"product_id": 17, "product_name": "Camisa Oxford", "category": "Ropa"},
    {"product_id": 18, "product_name": "Camisa Lino", "category": "Ropa"},
    {"product_id": 19, "product_name": "Riñonera Sport", "category": "Accesorios"},
    {"product_id": 20, "product_name": "Piluso Trend", "category": "Accesorios"},
]

POSITIVE_COMMENTS = [
    "Excelente servicio",
    "Muy buena calidad",
    "Entrega rápida",
    "La atención fue impecable",
    "Muy recomendable",
    "Volvería a comprar",
    "Llegó antes de lo esperado",
]

NEGATIVE_COMMENTS = [
    "Mala atención",
    "Producto defectuoso",
    "Tardó mucho",
    "No respondieron mis mensajes",
    "Llegó dañado",
    "La experiencia fue mala",
    "No cumplió mis expectativas",
]

NEUTRAL_COMMENTS = [
    "Todo ok",
    "Normal",
    "Sin comentarios",
    "Recibido correctamente",
    "Producto estándar",
    "Cumple con lo esperado",
]


# =========================
# PATHS
# =========================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

os.makedirs(RAW_DATA_PATH, exist_ok=True)


# =========================
# HELPERS
# =========================
def random_date_within_days(days_back: int) -> datetime:
    return datetime.now() - timedelta(days=random.randint(0, days_back))


def get_unit_price_by_category(category: str) -> int:
    if category == "Calzado":
        return random.randint(60, 180)
    if category == "Ropa":
        return random.randint(20, 90)
    return random.randint(10, 60)


# =========================
# GENERATE SALES
# =========================
def generate_sales() -> pd.DataFrame:
    sales = []

    for order_id in range(1, N_ORDERS + 1):
        product = random.choice(PRODUCT_CATALOG)
        order_date = random_date_within_days(DAYS_BACK_SALES)
        seller_id = random.randint(1, N_SELLERS)
        quantity = random.randint(1, 5)
        unit_price = get_unit_price_by_category(product["category"])
        discount = random.choice([0.00, 0.05, 0.10, 0.15, 0.20])
        total_amount = round(quantity * unit_price * (1 - discount), 2)

        sales.append(
            {
                "order_id": order_id,
                "order_date": order_date.strftime("%Y-%m-%d %H:%M:%S"),
                "customer_id": random.randint(1, N_CUSTOMERS),
                "product_id": product["product_id"],
                "product_name": product["product_name"],
                "category": product["category"],
                "channel": random.choice(CHANNELS),
                "seller_id": seller_id,
                "seller_name": f"Vendedor_{seller_id}",
                "quantity": quantity,
                "unit_price": unit_price,
                "discount": discount,
                "total_amount": total_amount,
                "payment_status": random.choice(PAYMENT_STATUS),
            }
        )

    return pd.DataFrame(sales)


# =========================
# GENERATE MARKETING
# =========================
def generate_marketing() -> pd.DataFrame:
    marketing = []

    for day_offset in range(DAYS_BACK_SALES):
        current_date = datetime.now() - timedelta(days=day_offset)

        for channel in CHANNELS:
            impressions = random.randint(1000, 10000)
            clicks = random.randint(100, min(1000, impressions))
            spend = round(random.uniform(50, 500), 2)
            conversions = random.randint(10, min(100, clicks))

            marketing.append(
                {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "channel": channel,
                    "campaign_name": f"{channel.lower().replace(' ', '_')}_campaign",
                    "impressions": impressions,
                    "clicks": clicks,
                    "spend": spend,
                    "conversions": conversions,
                }
            )

    return pd.DataFrame(marketing)


# =========================
# GENERATE SELLERS
# =========================
def generate_sellers() -> pd.DataFrame:
    sellers_data = []

    for seller_id in range(1, N_SELLERS + 1):
        sellers_data.append(
            {
                "seller_id": seller_id,
                "seller_name": f"Vendedor_{seller_id}",
                "team": random.choice(["A", "B"]),
                "region": random.choice(["Norte", "Sur", "Centro"]),
                "target_sales": random.randint(1000, 5000),
            }
        )

    return pd.DataFrame(sellers_data)


# =========================
# GENERATE COMMENTS
# =========================
def generate_comments() -> pd.DataFrame:
    comments = []
    all_comments = POSITIVE_COMMENTS + NEGATIVE_COMMENTS + NEUTRAL_COMMENTS

    for comment_id in range(1, N_COMMENTS + 1):
        comment_date = random_date_within_days(DAYS_BACK_COMMENTS)

        comments.append(
            {
                "comment_id": comment_id,
                "date": comment_date.strftime("%Y-%m-%d %H:%M:%S"),
                "channel": random.choice(CHANNELS),
                "customer_id": random.randint(1, N_CUSTOMERS),
                "comment_text": random.choice(all_comments),
            }
        )

    return pd.DataFrame(comments)


# =========================
# MAIN
# =========================
def main() -> None:
    random.seed(42)
    np.random.seed(42)

    df_sales = generate_sales()
    df_marketing = generate_marketing()
    df_sellers = generate_sellers()
    df_comments = generate_comments()

    df_sales.to_csv(os.path.join(RAW_DATA_PATH, "ventas.csv"), index=False, encoding="utf-8-sig")
    df_marketing.to_csv(os.path.join(RAW_DATA_PATH, "marketing.csv"), index=False, encoding="utf-8-sig")
    df_sellers.to_csv(os.path.join(RAW_DATA_PATH, "sellers.csv"), index=False, encoding="utf-8-sig")
    df_comments.to_csv(os.path.join(RAW_DATA_PATH, "comments.csv"), index=False, encoding="utf-8-sig")

    print("✅ Datos generados correctamente en:")
    print(RAW_DATA_PATH)
    print(f"- ventas.csv: {len(df_sales)} filas")
    print(f"- marketing.csv: {len(df_marketing)} filas")
    print(f"- sellers.csv: {len(df_sellers)} filas")
    print(f"- comments.csv: {len(df_comments)} filas")


if __name__ == "__main__":
    main()