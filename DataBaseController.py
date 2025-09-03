import pandas as pd
import ProductClass

def read_database(ruta):
    products = []
    df = pd.read_excel(ruta, engine='openpyxl') 
    for _, fila in df.iterrows():
        product = ProductClass.ProductClass(
            id=str(fila['id']),
            producto=str(fila['producto']),
            valor=str(fila['valor']),
            cantidad=str(fila['cantidad'])
        )
        products.append(product)
    return products

def edit_data(ruta, productos):
    data = {
        'id': [p.id for p in productos],
        'producto': [p.producto for p in productos],
        'valor': [p.valor for p in productos],
        'cantidad': [p.cantidad for p in productos],
    }
    df = pd.DataFrame(data)
    df.to_excel(ruta, index=False, engine='openpyxl')  # Guarda en .xlsx

def save_database(ruta, datos):
    df = pd.DataFrame(datos)
    df.to_excel(ruta, index=False, engine='openpyxl')
