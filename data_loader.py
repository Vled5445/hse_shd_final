import kagglehub
import pandas as pd
import uuid

path = kagglehub.dataset_download("roopacalistus/superstore")
print(f"Датасет загружен по пути: {path}")

data = pd.read_csv(f"{path}/SampleSuperstore.csv")
pd.set_option('display.max_columns', None)
print("\nПервые строки набора данных:\n", data.head())
print("\nИнформация о столбцах:\n")
print(data.info())

data['Postal Code'] = data['Postal Code'].fillna(0).astype(int).astype(str)
data['sale_key'] = data['City'] + '_' + data['State'] + '_' + data['Postal Code'] + '_' + data['Category'] + '_' + data['Sub-Category']
data['customer_key'] = data['Segment'] + '_' + data['City'] + '_' + data['State'] + '_' + data['Postal Code']
data['product_key'] = data['Category'] + '_' + data['Sub-Category']
data['shipment_key'] = data['sale_key'] + '_' + data['Ship Mode']

def make_id(series):
    return {k: str(uuid.uuid4()) for k in series.unique()}

sale_ids = make_id(data['sale_key'])
customer_ids = make_id(data['customer_key'])
product_ids = make_id(data['product_key'])
shipment_ids = make_id(data['shipment_key'])

data['sale_id'] = data['sale_key'].map(sale_ids)
data['customer_id'] = data['customer_key'].map(customer_ids)
data['product_id'] = data['product_key'].map(product_ids)
data['shipment_id'] = data['shipment_key'].map(shipment_ids)

data = data.drop(['sale_key', 'customer_key', 'product_key', 'shipment_key'], axis=1)
data.to_csv("busines_key_data.csv", index=False)
print("\n✅ Файл 'busines_key_data.csv' успешно сохранён.\nВсего строк: {len(data)}\nПример данных:\n", data.head())