import time
import streamlit as st
import pandas as pd
import datetime
from connection import load_the_spreadsheet, gsheet_conn
from gspread_dataframe import set_with_dataframe
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from datetime import datetime





def display_interface():
   #print('DISPLAY INTERFACE')
    st.title("Enviar Resumen")

    st.image('qip.png')

    # Crear campos de entrada para los datos
    nombre_cliente = st.text_input("Cliente", key='cliente_pdf')
    flag_carniceria = st.checkbox("¿Es el número de una carnicería?", key='flag_carniceria_pdf')
    if flag_carniceria:
        nombre_cliente = 'Carniceria ' + nombre_cliente
    fecha_inicio = st.date_input("¿Desde cuándo?", key='fecha_inicio_pedido')
    fecha_inicio = fecha_inicio.strftime("%Y-%m-%d")
    fecha_fin = st.date_input("Hasta cuándo?", key='fecha_fin_pedido')
    fecha_fin = fecha_fin.strftime("%Y-%m-%d")

    if st.button("Enviar pdf"):
        st.session_state.clicked = True
    
    if st.session_state.clicked:
         if nombre_cliente == '' or fecha_inicio == '' or fecha_fin == '':
            st.text(f'Completá los 3 campos para enviar el pdf')
    
    
    return nombre_cliente, flag_carniceria, fecha_inicio, fecha_fin

def buscar_pedidos(id_cliente, sheet_detalle_pedido, sheet_productos, fecha_inicio, fecha_fin):
    sheet_pedidos_cliente = sheet_detalle_pedido[(sheet_detalle_pedido['id_cliente']==id_cliente)]
    sheet_pedidos_cliente['fecha'] = pd.to_datetime(sheet_pedidos_cliente['fecha'], errors='coerce')
    #print(sheet_detalle_pedido.fecha.values[0], type(sheet_detalle_pedido.fecha.values[0]))

    df_filtrado = sheet_pedidos_cliente[sheet_pedidos_cliente['fecha'].between(fecha_inicio, fecha_fin)]
    df_filtrado['nombre_producto'] = df_filtrado.merge(sheet_productos, left_on='producto', right_on='id_producto')[['descripcion']]

    df_pedidos_pdf = pd.DataFrame(columns=['fecha_pedido', 'kilos', 'producto', 'precio_x_kilo', 'subtotal'])

    df_pedidos_pdf = df_filtrado[['fecha', 'peso', 'nombre_producto', 'precio_por_kilo', 'total_detalle']]

    return df_pedidos_pdf


def buscar_pagos(id_cliente, sheet_pagos, fecha_inicio, fecha_fin):

    sheet_pagos_cliente = sheet_pagos[(sheet_pagos['id_cliente']==id_cliente)]
    sheet_pagos_cliente['fecha'] = pd.to_datetime(sheet_pagos_cliente['fecha_pago'], errors='coerce')
    #print(sheet_detalle_pedido.fecha.values[0], type(sheet_detalle_pedido.fecha.values[0]))

    df_filtrado = sheet_pagos_cliente[sheet_pagos_cliente['fecha_pago'].between(fecha_inicio, fecha_fin)]
    #df_filtrado['nombre_producto'] = df_filtrado.merge(sheet_productos, left_on='producto', right_on='id_producto')[['descripcion']]

    df_pagos_pdf = pd.DataFrame(columns=['fecha_pago', 'monto', 'medio_de_pago'])

    df_pagos_pdf = df_filtrado[['fecha_pago', 'monto', 'medio_de_pago']]

    return df_pagos_pdf


def create_pdf(file_path, customer_name, df):
    # Crear el documento PDF
    pdf = SimpleDocTemplate(file_path, pagesize=letter)

    # Contenido del PDF
    content = []

    # Agregar la fecha actual y el nombre del cliente
    current_date = datetime.now().strftime("%Y-%m-%d")
    content.append(f"Fecha: {current_date}")
    content.append(f"Cliente: {customer_name}")

    # Agregar la tabla con estilo
    table_data = [df.columns.tolist()] + df.values.tolist()
    table = Table(table_data, repeatRows=1)

    # Estilo de la tabla
    style = TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)])

    table.setStyle(style)
    content.append(table)

    # Construir el PDF
    pdf.build(content)




# Título de la aplicación
def enviar_pdf(nombre_cliente, flag_carniceria, fecha_inicio, fecha_fin):
    #print('AGREGAR PEDIDO')

    with st.spinner(text="Validando pedido"):

        error_input_data = False
        sh = gsheet_conn()
        #df_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')

        sheet_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')
        sheet_clientes = load_the_spreadsheet(sh, 'CLIENTE')
        sheet_pagos = load_the_spreadsheet(sh, 'PAGO')
        sheet_productos = load_the_spreadsheet(sh, 'PRODUCTO')
        


        #VALIDACION CLIENTE      
        try:
            id_cliente = sheet_clientes[sheet_clientes['nombre'].str.upper()==nombre_cliente.upper()].id_cliente.values[0]
        except:
            st.error('No existe ese cliente. Intente nuevamente.')
            error_input_data = True

            # Agregar los nuevos datos a la hoja de Google Sheets
        if not error_input_data:
                id_cliente = sheet_clientes[sheet_clientes['nombre'].str.upper()==nombre_cliente.upper()].id_cliente.values[0]
                
                df_pedidos_pdf = buscar_pedidos(id_cliente, sheet_detalle_pedido, sheet_productos, fecha_inicio, fecha_fin)

                df_pagos_pdf = buscar_pagos(id_cliente, sheet_pagos, fecha_inicio, fecha_fin)

                #create_pdf("factura.pdf", "Guillermo", df_pedidos_pdf)

def main_pdf():
    st.session_state.clicked = False
    nombre_cliente, flag_carniceria, fecha_inicio, fecha_fin = display_interface()
    
    if nombre_cliente != '' and fecha_inicio != '' and fecha_fin != '':
        if st.session_state.clicked:
            enviar_pdf(nombre_cliente, flag_carniceria, fecha_inicio, fecha_fin)