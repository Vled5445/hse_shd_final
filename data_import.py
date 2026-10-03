import datetime
from dotenv import load_dotenv
import os
import hashlib
import pandas as pd
from sqlalchemy import create_engine

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_SCHEMA = os.getenv("DB_SCHEMA")

engine = create_engine(
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}",
    connect_args={'connect_timeout': 10},
    pool_pre_ping=True
)

print(f"Подключение к БД '{DB_NAME}' как {DB_USER}")
df = pd.read_csv("busines_key_data.csv")

for col in ['sale_id', 'customer_id', 'product_id', 'shipment_id']:
    df[col] = df[col].astype(str)

def insert_hub(df, id_col, table_name, hash_col):
    hub = df[[id_col]].drop_duplicates().copy()
    hub[hash_col] = hub[id_col].apply(lambda x: hashlib.md5(x.encode()).hexdigest())
    hub["source_system"] = "busines_key_data.csv"
    hub["load_dttm"] = pd.Timestamp.now()
    hub.to_sql(table_name, con=engine, schema=DB_SCHEMA,
               if_exists="append", index=False, method="multi", chunksize=500)
    print(f"✅ {table_name} — загружено {len(hub)} записей")
    return hub

hub_sales = insert_hub(df, "sale_id", "h_sales", "h_sales_hash")
hub_customer = insert_hub(df, "customer_id", "h_customer", "h_customer_hash")
hub_product = insert_hub(df, "product_id", "h_product", "h_product_hash")
hub_shipment = insert_hub(df, "shipment_id", "h_shipment", "h_shipment_hash")

sales_hash = hub_sales.set_index("sale_id")["h_sales_hash"].to_dict()
customer_hash = hub_customer.set_index("customer_id")["h_customer_hash"].to_dict()
product_hash = hub_product.set_index("product_id")["h_product_hash"].to_dict()
shipment_hash = hub_shipment.set_index("shipment_id")["h_shipment_hash"].to_dict()

df_cust_sale = df[["customer_id", "sale_id"]].drop_duplicates()
df_cust_sale["l_customer_sale_hash"] = df_cust_sale.apply(
    lambda r: hashlib.md5(f"{r['customer_id']}_{r['sale_id']}".encode()).hexdigest(), axis=1)
df_cust_sale["h_customer_hash"] = df_cust_sale["customer_id"].map(customer_hash)
df_cust_sale["h_sales_hash"] = df_cust_sale["sale_id"].map(sales_hash)
df_cust_sale["record_source"] = "busines_key_data.csv"
df_cust_sale["load_dttm"] = pd.Timestamp.now()

df_cust_sale = df_cust_sale[[
    "l_customer_sale_hash",
    "h_customer_hash",
    "h_sales_hash",
    "record_source",
    "load_dttm"
]]

df_cust_sale.to_sql("l_customer_sale", con=engine, schema=DB_SCHEMA,
                    if_exists="append", index=False, method="multi", chunksize=500)
print("✅ l_customer_sale — загружено", len(df_cust_sale), "записей")

# --- LINK: SALE → PRODUCT ---
df_sale_prod = df[["sale_id", "product_id"]].drop_duplicates()
df_sale_prod["l_sales_product_hash"] = df_sale_prod.apply(
    lambda r: hashlib.md5(f"{r['sale_id']}_{r['product_id']}".encode()).hexdigest(), axis=1)
df_sale_prod["h_sales_hash"] = df_sale_prod["sale_id"].map(sales_hash)
df_sale_prod["h_product_hash"] = df_sale_prod["product_id"].map(product_hash)
df_sale_prod["record_source"] = "busines_key_data.csv"
df_sale_prod["load_dttm"] = pd.Timestamp.now()

df_sale_prod = df_sale_prod[[
    "l_sales_product_hash",
    "h_sales_hash",
    "h_product_hash",
    "record_source",
    "load_dttm"
]]

df_sale_prod.to_sql("l_sales_product", con=engine, schema=DB_SCHEMA,
                    if_exists="append", index=False, method="multi", chunksize=500)
print("✅ l_sales_product — загружено", len(df_sale_prod), "записей")

df_sale_ship = df[["sale_id", "shipment_id"]].drop_duplicates()
df_sale_ship["l_sales_shipment_hash"] = df_sale_ship.apply(
    lambda r: hashlib.md5(f"{r['sale_id']}_{r['shipment_id']}".encode()).hexdigest(), axis=1)
df_sale_ship["h_sales_hash"] = df_sale_ship["sale_id"].map(sales_hash)
df_sale_ship["h_shipment_hash"] = df_sale_ship["shipment_id"].map(shipment_hash)
df_sale_ship["record_source"] = "busines_key_data.csv"
df_sale_ship["load_dttm"] = pd.Timestamp.now()

df_sale_ship = df_sale_ship[[
    "l_sales_shipment_hash",
    "h_sales_hash",
    "h_shipment_hash",
    "record_source",
    "load_dttm"
]]

df_sale_ship.to_sql("l_sales_shipment", con=engine, schema=DB_SCHEMA,
                    if_exists="append", index=False, method="multi", chunksize=500)
print("✅ l_sales_shipment — загружено", len(df_sale_ship), "записей")

df_seg = df[["customer_id", "Segment"]].drop_duplicates()
df_seg["h_customer_hash"] = df_seg["customer_id"].map(customer_hash)
df_seg["hash_diff"] = df_seg["Segment"].apply(lambda x: hashlib.md5(x.encode()).hexdigest())
df_seg = df_seg.rename(columns={"Segment": "customer_segment"})
df_seg["record_source"] = "busines_key_data.csv"
df_seg["load_dttm"] = pd.Timestamp.now()

df_seg = df_seg[[
    "h_customer_hash", "load_dttm", "customer_segment", "hash_diff", "record_source"
]]

df_seg.to_sql("s_customer_segment", con=engine, schema=DB_SCHEMA,
              if_exists="append", index=False, method="multi", chunksize=500)
print("✅ s_customer_segment — загружено", len(df_seg), "записей")

df_loc = df[["customer_id", "Postal Code", "Country", "Region", "State", "City"]].drop_duplicates()
df_loc["h_customer_hash"] = df_loc["customer_id"].map(customer_hash)
df_loc["hash_diff"] = df_loc.apply(lambda r: hashlib.md5("|".join(r.astype(str)).encode()).hexdigest(), axis=1)
df_loc = df_loc.rename(columns={
    "Postal Code": "postal_code",
    "Country": "country",
    "Region": "region",
    "State": "state",
    "City": "city"
})
df_loc["record_source"] = "busines_key_data.csv"
df_loc["load_dttm"] = pd.Timestamp.now()

df_loc = df_loc[[
    "h_customer_hash", "load_dttm", "postal_code", "country", "region",
    "state", "city", "hash_diff", "record_source"
]]

df_loc.to_sql("s_customer_address", con=engine, schema=DB_SCHEMA,
              if_exists="append", index=False, method="multi", chunksize=500)
print("✅ s_customer_address — загружено", len(df_loc), "записей")

df_prod = df[["product_id", "Category", "Sub-Category"]].drop_duplicates()
df_prod["h_product_hash"] = df_prod["product_id"].map(product_hash)
df_prod["hash_diff"] = df_prod.apply(lambda r: hashlib.md5("|".join(r.astype(str)).encode()).hexdigest(), axis=1)
df_prod = df_prod.rename(columns={"Category": "category", "Sub-Category": "sub_category"})
df_prod["record_source"] = "busines_key_data.csv"
df_prod["load_dttm"] = pd.Timestamp.now()

df_prod = df_prod[[
    "h_product_hash", "load_dttm", "category", "sub_category", "hash_diff", "record_source"
]]

df_prod.to_sql("s_product_info", con=engine, schema=DB_SCHEMA,
               if_exists="append", index=False, method="multi", chunksize=500)
print("✅ s_product_info — загружено", len(df_prod), "записей")

df_metrics = df[["sale_id", "product_id", "Quantity", "Sales", "Discount", "Profit"]].drop_duplicates()
df_metrics["l_sales_product_hash"] = df_metrics.apply(
    lambda r: hashlib.md5(f"{r['sale_id']}_{r['product_id']}".encode()).hexdigest(), axis=1)
df_metrics["hash_diff"] = df_metrics[["Quantity", "Sales", "Discount", "Profit"]].apply(
    lambda r: hashlib.md5("|".join(r.astype(str)).encode()).hexdigest(), axis=1)
df_metrics = df_metrics.rename(columns={"Quantity": "quantity", "Sales": "sales",
                                        "Discount": "discount", "Profit": "profit"})
df_metrics["record_source"] = "busines_key_data.csv"
df_metrics["load_dttm"] = [datetime.datetime.now() + datetime.timedelta(microseconds=i) for i in range(len(df_metrics))]

df_metrics = df_metrics[[
    "l_sales_product_hash", "load_dttm", "quantity", "sales", "discount", "profit", "hash_diff", "record_source"
]]

existing_hashes = pd.read_sql(
    f"SELECT l_sales_product_hash FROM {DB_SCHEMA}.s_sales_metrics",
    con=engine
)
df_metrics = df_metrics[~df_metrics["l_sales_product_hash"].isin(existing_hashes["l_sales_product_hash"])]

if not df_metrics.empty:
    df_metrics.to_sql("s_sales_metrics", con=engine, schema=DB_SCHEMA,
                      if_exists="append", index=False, method="multi", chunksize=500)
    print("✅ s_sales_metrics — добавлено", len(df_metrics), "новых записей")
else:
    print("⚠️ s_sales_metrics — все записи уже есть, пропускаем")


print("\n🎯 Все таблицы успешно загружены в хранилище Data Vault.")
