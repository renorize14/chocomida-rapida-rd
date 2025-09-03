import tkinter as tk
from tkinter import messagebox
from DataBaseController import read_database, edit_data, save_database
import ProductClass
import ActualClass
import VentaClass
from datetime import datetime
import os
import pandas as pd
import win32print
import win32ui

hoy = datetime.now()
carpeta = f"{hoy.year}-{hoy.month:02d}-{hoy.day:02d}"
ruta_carpeta = os.path.join(".", carpeta)
ruta_excel = os.path.join(ruta_carpeta, "daily.xlsx")
ruta_actual = os.path.join(".", "actual.txt")
ruta_actual_xlsx = os.path.join(".", "actual.xlsx")

root = tk.Tk()

pantalla_ancho = root.winfo_screenwidth()
pantalla_alto = root.winfo_screenheight()

ancho = int(pantalla_ancho * 0.8)
alto = int(pantalla_alto * 0.8)

root.geometry(f"{ancho}x{alto}")
root.resizable(False, False)
root.title("Donde Alonso RD")
root.config(bg="#2a3b5c")

left_frame = tk.Frame(root, width=ancho * 0.7, height=alto, bg="#2a3b5c")
left_frame.grid(row=0, column=0, padx=0, pady=20, sticky="nsew")

right_frame = tk.Frame(root, width=ancho * 0.3, height=alto, bg="#2a3b5c")
right_frame.grid(row=0, column=1, padx=0, pady=20, sticky="nsew")

# Dividir el frame derecho en dos secciones: lista de productos y sección de información
list_frame = tk.Frame(right_frame, bg="#2a3b5c")
list_frame.grid(row=0, column=0, sticky="nsew")

info_frame = tk.Frame(right_frame, bg="#2a3b5c")
info_frame.grid(row=1, column=0, sticky="nsew")

filas = 20
columnas = 5

venta_diaria = []
boleta_actual = []
venta_actual = []
boleta_header = ''
total_diario = 0
total_actual = 0
client_name = ''

def make_header():
	num = len(venta_actual) + 1
	boleta_header='Donde Alonso RD \n'
	boleta_header= boleta_header + 'Venta Nro: ' + str(num) + '\n'
	boleta_header= boleta_header + '------------------'
	return boleta_header

def initilalize_data():
    global total_diario
    global venta_diaria
    global boleta_actual
    global venta_actual
    global total_actual
    global boleta_header

    if not os.path.exists(ruta_carpeta):
        os.makedirs(ruta_carpeta)
        print(f"✔ Carpeta creada: {ruta_carpeta}")

    if not os.path.exists(ruta_excel):
        df = pd.DataFrame(columns=["id", "fecha", "hora", "venta", "total"])
        df.to_excel(ruta_excel, index=False, engine="openpyxl")
        print(f"✔ Archivo daily.xlsx creado en {ruta_excel}")
    else:
        df = pd.read_excel(ruta_excel, engine="openpyxl")
        total = 0
        for _, fila in df.iterrows():
            venta = VentaClass.Venta(
                id=fila["id"],
                fecha=fila["fecha"],
                hora=fila["hora"],
                venta=fila["venta"],
                total=fila["total"]
            )
            total = total + int(fila["total"])
            venta_diaria.append(venta)
        total_diario = total
        print(f"📥 Se cargaron {len(venta_diaria)} ventas desde daily.xlsx")

    if not os.path.exists(ruta_actual):
        with open(ruta_actual, "w", encoding="utf-8") as f:
            print(boleta_header)
            f.write(boleta_header)
            f.write('\n\nTotal: $' + str(total_actual))
            print("✔ Archivo actual.txt creado.")
    else:
        with open(ruta_actual, "r", encoding="utf-8") as f:
            boleta_actual = f.read().strip()
        print(f"📄 Contenido de actual.txt: '{boleta_actual}'")

    if not os.path.exists(ruta_actual_xlsx):
        df = pd.DataFrame(columns=["id_", "cantidad", "producto","comentario", "valor_un","total"])
        df.to_excel(ruta_actual_xlsx, index=False, engine="openpyxl")
        print(f"✔ Archivo actual.xlsx creado en {ruta_actual_xlsx}")
    else:
        df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
        total = 0
        if not df.empty:
            for _, fila in df.iterrows():
                actual = ActualClass.ActualClass(
                    id_=fila["id_"],
                    cantidad=fila["cantidad"],
                    producto=fila["producto"],
                    comentario=fila["comentario"],
                    valor_un=fila["valor_un"],
                    total=fila["total"]
                )
                total = total + int(fila["total"])
                venta_actual.append(actual)
        total_actual = total
        print(f"📥 Se cargaron {len(venta_actual)} ventas desde daily.xlsx")    
   
def format_price(price):
	formateado = f"{price:,.0f}".replace(',', '.')
	return formateado

def show_dual_entry_prompt(articulo):
    def on_ok():
        dato1 = entry1.get()
        dato2 = entry2.get("1.0", tk.END)
        if not dato1 or not dato2:
            messagebox.showwarning("Faltan datos", "Por favor ingresa ambos campos.")
            return
        id_ = len(venta_actual) + 1
        total = int(articulo.valor) * int(dato1)
        nuevo_ingreso = ActualClass.ActualClass(
            id_=id_,
            cantidad=dato1,
            producto=articulo.producto,
            comentario=dato2,
            valor_un=articulo.valor,
            total=total
        )

        agregar_a_actual(ruta_actual_xlsx, nuevo_ingreso)

        prompt.destroy()

    def on_cancel():
        prompt.destroy()

    prompt = tk.Toplevel(root)
    prompt.title("Agregar productos")
    prompt.geometry("300x350")
    prompt.grab_set()  # Bloquea la ventana principal

    tk.Label(prompt, text="Artículo: " + articulo.producto).pack(pady=5)
    tk.Label(prompt, text="Valor individual: $" + format_price(articulo.valor)).pack(pady=5)
    tk.Label(prompt, text="------------------------").pack(pady=5)
    tk.Label(prompt, text="Cantidad:").pack(pady=5)
    entry1 = tk.Entry(prompt)
    entry1.pack(pady=5)
    entry1.insert(0, "1")

    tk.Label(prompt, text="Comentarios:").pack(pady=5)
    entry2 = tk.Text(prompt, height=5, width=30)
    entry2.pack(pady=5)

    btn_frame = tk.Frame(prompt)
    btn_frame.pack(pady=10)

    ok_btn = tk.Button(btn_frame, text="Aceptar", command=on_ok)
    ok_btn.pack(side="left", padx=5)

    cancel_btn = tk.Button(btn_frame, text="Cancelar", command=on_cancel)
    cancel_btn.pack(side="left", padx=5)

def agregar_venta(ruta_excel, venta):
    df = pd.read_excel(ruta_excel, engine="openpyxl")
    
    nueva_fila = {
        "id_": venta.id_,
        "fecha": venta.fecha,
        "hora": venta.hora,
        "venta": venta.venta,
        "total": venta.total
    }

    df = df.append(nueva_fila, ignore_index=True)
    df.to_excel(ruta_excel, index=False, engine="openpyxl")
    print("✔ Venta agregada al archivo.")

def editar_venta_por_id(ruta_excel, id_venta, nuevos_datos):
    df = pd.read_excel(ruta_excel, engine="openpyxl")
    
    if id_venta in df["id"].values:
        index = df[df["id"] == id_venta].index[0]
        df.at[index, "fecha"] = nuevos_datos.fecha
        df.at[index, "hora"] = nuevos_datos.hora
        df.at[index, "venta"] = nuevos_datos.venta
        df.at[index, "total"] = nuevos_datos.total

        df.to_excel(ruta_excel, index=False, engine="openpyxl")
        print(f"✏️ Venta con ID {id_venta} actualizada.")
    else:
        print(f"⚠️ Venta con ID {id_venta} no encontrada.")

def add_info_to_bol(extra_info):
	with open(ruta_actual, "a", encoding="utf-8") as f:
		f.write(extra_info + '\n')

def agregar_a_actual(ruta_actual_xlsx, nueva_venta):
	global total_actual
	df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
	nueva_fila = {
	    "id_": nueva_venta.id_,
	    "cantidad": nueva_venta.cantidad,
	    "producto": nueva_venta.producto,
	    "comentario": nueva_venta.comentario,
	    "valor_un": nueva_venta.valor_un,
	    "total": nueva_venta.total
	}

	df = df._append(nueva_fila, ignore_index=True)
	df.to_excel(ruta_actual_xlsx, index=False, engine="openpyxl")
	actualizar_listbox(product_listbox)
	print(f"✔ Venta agregada a {ruta_actual_xlsx}")
	update_values()

def borrar_de_actual_por_id(ruta_actual_xlsx, id_venta):
    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")

    # Conversión segura a int
    id_venta = int(id_venta)

    # Verificar si existe el ID
    if id_venta in df["id_"].values:
        df = df[df["id_"] != id_venta]
        df.to_excel(ruta_actual_xlsx, index=False, engine="openpyxl")
        print(f"🗑 Venta con ID {id_venta} eliminada de {ruta_actual_xlsx}")

        # Asegurarse de que estas funciones estén definidas
        actualizar_listbox(product_listbox)
        update_values()
    else:
        print(f"⚠ No se encontró una venta con ID {id_venta}")

def borrar_todo_actual(ruta_actual_xlsx):
    df_vacio = pd.DataFrame(columns=["id", "cantidad", "producto", "valor_un", "total"])
    df_vacio.to_excel(ruta_actual_xlsx, index=False, engine="openpyxl")
    print(f"🧹 Se eliminaron todos los registros de {ruta_actual_xlsx}")

def actualizar_listbox(product_listbox):
    global total_diario
    global venta_diaria
    global boleta_actual
    global venta_actual
    global total_actual
    global boleta_header
    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
    total = 0
    venta_actual = []
    for _, fila in df.iterrows():
        actual = ActualClass.ActualClass(
            id_=fila["id_"],
            cantidad=fila["cantidad"],
            producto=fila["producto"],
            comentario=fila["comentario"],
            valor_un=fila["valor_un"],
            total=fila["total"]
        )
        total = total + int(fila["total"])
        venta_actual.append(actual)
    total_actual = total

    product_listbox.delete(0, tk.END)
    for venta in venta_actual:
        texto = f"[{venta.id_}] - {venta.cantidad} x {venta.producto} (${venta.total})"
        product_listbox.insert(tk.END, texto)

def update_values():
    global total_actual
    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
    total = 0
    for _, fila in df.iterrows():
        total = total + int(fila["total"])
    total_actual = total
    act_total.config(text=f"Total Venta: ${format_price(total_actual)}")

    num = len(venta_actual) + 1
    act_bol.config(text=f"Boleta N°{determinate_sell_number()}")

def on_listbox_double_click(event):
    seleccion = product_listbox.curselection()
    if not seleccion:
        return

    index = seleccion[0]
    texto = product_listbox.get(index)

    # Extraer ID desde el texto del Listbox (formato: [ID] - ...)
    try:
        id_extraido = texto.split("]")[0].replace("[", "").strip()
    except:
        messagebox.showerror("Error", "No se pudo interpretar el ID.")
        return

    confirmar = messagebox.askokcancel("Eliminar artículo", "¿Realmente desea eliminar este artículo?")

    if confirmar:
        borrar_de_actual_por_id(ruta_actual_xlsx, id_extraido)
        actualizar_listbox(product_listbox)
        update_values()

def show_add_discount():
    def on_ok():
        dato1 = entry1.get()
        if not dato1:
            messagebox.showwarning("Faltan datos", "Por favor ingresa ambos campos.")
            return
        id_ = len(venta_actual) + 1
        total = int(dato1) * -1
        nuevo_ingreso = ActualClass.ActualClass(
            id_=id_,
            cantidad='1',
            producto='Desc',
            comentario='--',
            valor_un=total,
            total=total
        )

        agregar_a_actual(ruta_actual_xlsx, nuevo_ingreso)

        prompt.destroy()

    def on_cancel():
        prompt.destroy()

    prompt = tk.Toplevel(root)
    prompt.title("Agregar descuento")
    prompt.geometry("300x350")
    prompt.grab_set()  # Bloquea la ventana principal

    tk.Label(prompt, text="Valor del descuento").pack(pady=5)
    entry1 = tk.Entry(prompt)
    entry1.pack(pady=5)
    entry1.insert(0, "1")

    btn_frame = tk.Frame(prompt)
    btn_frame.pack(pady=10)

    ok_btn = tk.Button(btn_frame, text="Aceptar", command=on_ok)
    ok_btn.pack(side="left", padx=5)

    cancel_btn = tk.Button(btn_frame, text="Cancelar", command=on_cancel)
    cancel_btn.pack(side="left", padx=5)

def make_table_recipe():
    global client_name
    content = '' + make_header() + '\n'
    content += '\nNombre cliente: ' + client_name + '\n'
    content += 'COPIA MESON\n'

    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
    total = 0
    for _, fila in df.iterrows():
        total = total + int(fila["total"])

        content += str(fila["cantidad"]) + 'x ' + str(fila["producto"]) + ' ($' + str(format_price(fila["total"])) + ')\n'

    content += '------------------\nTotal: ' + str(format_price(total))

    return content

def make_kitchen_recipe():
    global client_name
    content = '' + make_header() + '\n'
    content += '\nNombre cliente: ' + client_name + '\n'
    content += 'COPIA COCINA\n'

    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
    total = 0
    for _, fila in df.iterrows():
        total = total + int(fila["total"])

        content += str(fila["cantidad"]) + 'x ' + str(fila["producto"])
        if ( str(fila["comentario"]) != '' ):
            content += str(fila["comentario"]) 
        content += '\n'

    return content

def print_in_pos_80(content: str):

    printer_name = win32print.GetDefaultPrinter()
    print(f"Usando impresora predeterminada: {printer_name}")

    hPrinter = win32print.OpenPrinter(printer_name)
    try:
        hJob = win32print.StartDocPrinter(hPrinter, 1, ("Ticket", None, "RAW"))
        win32print.StartPagePrinter(hPrinter)

        data = content.encode('utf-8')
        print(data)

        # Añadir saltos de línea + comando de corte ESC/POS
        data += b"\n\n\n\n\n\n\n\n\n"            # Espacio antes de cortar
        data += b"\x1D\x56\x00"      # Corte total

        # Enviar a la impresora
        win32print.WritePrinter(hPrinter, data)

        # Finalizar página y documento
        win32print.EndPagePrinter(hPrinter)
        win32print.EndDocPrinter(hPrinter)

        print("Ticket enviado a la impresora correctamente.")

    except Exception as e:
        print(f"Error al imprimir: {e}")

    finally:
        win32print.ClosePrinter(hPrinter)

def set_client_name():
    global client_name
    def on_ok():
        dato1 = entry1.get()
        if not dato1:
            messagebox.showwarning("Faltan datos", "Por favor ingresa los campos.")
            return
        client_name = dato1
        conclude_sell()
        prompt.destroy()

    def on_cancel():
        prompt.destroy()

    prompt = tk.Toplevel(root)
    prompt.title("")
    prompt.geometry("300x200")
    prompt.grab_set()  # Bloquea la ventana principal

    tk.Label(prompt, text="Nombre del cliente").pack(pady=5)
    entry1 = tk.Entry(prompt)
    entry1.pack(pady=5)
    entry1.insert(0, "")

    btn_frame = tk.Frame(prompt)
    btn_frame.pack(pady=10)

    ok_btn = tk.Button(btn_frame, text="Aceptar", command=on_ok)
    ok_btn.pack(side="left", padx=5)

    cancel_btn = tk.Button(btn_frame, text="Cancelar", command=on_cancel)
    cancel_btn.pack(side="left", padx=5)

def copy_sell_to_daily():
    global ruta_actual_xlsx
    global total_actual
    global ruta_excel
    df = pd.read_excel(ruta_actual_xlsx, engine="openpyxl")
    total = 0
    last_sell = []
    for _, fila in df.iterrows():
        actual = ActualClass.ActualClass(
            id_=fila["id_"],
            cantidad=fila["cantidad"],
            producto=fila["producto"],
            comentario=fila["comentario"],
            valor_un=fila["valor_un"],
            total=fila["total"]
        )
        total = total + int(fila["total"])
        last_sell.append(actual)

    borrar_todo_actual(ruta_actual_xlsx)

    hora = datetime.now().strftime("%H:%M")

    df2 = pd.read_excel(ruta_excel, engine="openpyxl")
    for sell in last_sell:
        nueva_fila = {
            "id_": sell.id_,
            "fecha": f"{hoy.year}-{hoy.month:02d}-{hoy.day:02d}",
            "hora": hora,
            "venta": sell.producto,
            "total": sell.total
        }

        df2 = df2._append(nueva_fila, ignore_index=True)

    df2.to_excel(ruta_excel, index=False, engine="openpyxl")
    actualizar_listbox(product_listbox)
    total_actual = 0
    update_values()

def determinate_sell_number():
    global ruta_excel
    df = pd.read_excel(ruta_excel, engine="openpyxl")
    different_times = []
    for _, fila in df.iterrows():
        different_times.append(fila["hora"])

    different_times = list(set(different_times))

    return len(different_times)


def conclude_sell():
    respuesta = messagebox.askokcancel("Confirmación", "¿Seguro que quieres concluír esta venta?")

    if respuesta:
        print("OK → el usuario aceptó")
        print('Concluyendo venta')
        kitchen = make_kitchen_recipe()
        table = make_table_recipe()

        #print_in_pos_80(kitchen)
        #print_in_pos_80(table)

        copy_sell_to_daily()

initilalize_data()

database = read_database('database.xlsx')

for i in range(filas):
    left_frame.grid_rowconfigure(i, weight=1, uniform="equal")
for i in range(columnas):
    left_frame.grid_columnconfigure(i, weight=1, uniform="equal")

i = 0

for data in database:
    fila = i // columnas
    columna = i % columnas
    boton = tk.Button(left_frame, text=data.producto,command=lambda d=data: show_dual_entry_prompt(d))
    boton.grid(row=fila, column=columna, padx=5, pady=10, sticky="nsew")
    i += 1

descFila = i // columnas
descSolumna = i % columnas
boton = tk.Button(left_frame, text='Agregar descuento', bg='#3A6DD7', fg="black", font=("Arial", 10, "bold"), command=show_add_discount)
boton.grid(row=descFila, column=descSolumna, padx=5, pady=5, sticky="nsew")

venta_label = tk.Label(list_frame, text="Venta Actual", bg="#2a3b5c", fg="white", font=("Arial", 14, "bold"))
venta_label.grid(row=0, column=0, padx=5, pady=(10, 0), sticky="w")

product_listbox = tk.Listbox(list_frame, selectmode=tk.SINGLE, height=12, width=int(ancho * 0.03), bg="#3a4e6b", fg="white", font=("Arial", 12))
product_listbox.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
product_listbox.bind("<Double-Button-1>", on_listbox_double_click)
scrollbar = tk.Scrollbar(list_frame, orient="vertical", command=product_listbox.yview)
product_listbox.config(yscrollcommand=scrollbar.set)
scrollbar.grid(row=1, column=1, sticky="ns")

act_bol = tk.Label(list_frame, text=f"Boleta N°:", bg="#2a3b5c", fg="white", font=("Arial", 14, "bold"))
act_bol.grid(row=2, column=0, padx=5, pady=(10, 0), sticky="w")

act_total = tk.Label(list_frame, text=f"Total venta: ${format_price(total_actual)}", bg="#2a3b5c", fg="white", font=("Arial", 14, "bold"))
act_total.grid(row=3, column=0, padx=5, pady=(10, 0), sticky="w")

conclude_button = tk.Button(list_frame, text='Concluir Venta', bg='#92FD70', fg="black", font=("Arial", 10, "bold"), command=conclude_sell)
conclude_button.grid(row=4, column=0, padx=5, pady=(10, 0), sticky="nsew")

selected_products = []

actualizar_listbox(product_listbox)
update_values()
# Iniciar el bucle principal de la aplicación
root.mainloop()