import streamlit as st
import  streamlit_toggle as tog
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from connection import load_the_spreadsheet, gsheet_conn
import matplotlib.pyplot as plt
import locale
import seaborn as sns
import re

# Establecer el idioma local en español
locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')

def limpiar_monto(monto):
    # Utilizar expresiones regulares para extraer solo los dígitos
    monto_limpio = re.sub(r'[^0-9.]', '', monto)
    monto_limpio = monto_limpio.split('.')[0]
    return int(monto_limpio)


def start():
    #table_on, chart_on = display_toggles()
    

    #print(chart_on)

    sh = gsheet_conn()
    df_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')
    df_producto = load_the_spreadsheet(sh, 'PRODUCTO')
    df_cliente = load_the_spreadsheet(sh, 'CLIENTE')
    df_pagos = load_the_spreadsheet(sh, 'PAGO')
    
    df_detalle_pedido['total_detalle'] = df_detalle_pedido['total_detalle'].apply(lambda x: int(x[2:-3].replace(',', '')))
    #print(df_pagos['monto'].iloc[0], limpiar_monto(df_pagos['monto'].iloc[0]), int(limpiar_monto(df_pagos['monto'].iloc[0])))
    df_pagos['monto'] = df_pagos['monto'].apply(lambda x: limpiar_monto(x))
    #(lambda x: int(x[5:-7].replace(',', '')))
    

    df_facturacion_extended = df_detalle_pedido.merge(df_cliente, on='id_cliente')
    #st.write(df_facturacion_extended[['nombre', 'total_detalle']].iloc[0]['total_detalle'])
    df_facturacion = df_facturacion_extended[['nombre', 'total_detalle']].groupby('nombre').sum().reset_index()
    df_facturacion.rename(columns={'nombre': 'Cliente', 'total_detalle': 'Monto Facturado'}, inplace=True)


    df_kilos = df_facturacion_extended[['nombre', 'peso']].groupby('nombre').sum().reset_index()
    
    df_kilos.rename(columns={'nombre': 'Cliente', 'peso': 'Kilos Pedidos'}, inplace=True)

    df_pagos_extended = df_pagos.merge(df_cliente, on='id_cliente')
    df_deuda = df_pagos_extended[['nombre', 'monto']].groupby('nombre').sum().reset_index()
    df_deuda.rename(columns={'nombre': 'Cliente', 'monto': 'Monto Pagado'}, inplace=True)
    df_deuda = df_deuda.merge(df_facturacion, on='Cliente')
    df_deuda['Monto Deuda'] = df_deuda['Monto Facturado'] - df_deuda['Monto Pagado']
    df_deuda = df_deuda[['Cliente', 'Monto Deuda']]

    df_resumen = df_facturacion.merge(df_kilos, on='Cliente').merge(df_deuda, on='Cliente')

    #if chart_on:
    data_facturacion = df_resumen.set_index('Cliente')[['Monto Facturado']]#, 'Kilos Pedidos', 'Monto Deuda']]
    data_deuda = df_resumen.set_index('Cliente')[['Monto Deuda']]#, 'Kilos Pedidos', 'Monto Deuda']]
    data_kilos = df_resumen.set_index('Cliente')[['Kilos Pedidos']]#, 'Kilos Pedidos', 'Monto Deuda']]
    
    tabla_facturacion, tabla_deuda = st.columns(2)
    tabla_kilos, _ = st.columns(2)

    #tabla_facturacion.write('Total Amount Earned by Client')
    #tabla_facturacion.bar_chart(data_facturacion, color='#ABFFB4')
    #tabla_deuda.write('Total Debt by Cliente')
    #tabla_deuda.bar_chart(data_deuda, color='#FF876D')
    #tabla_kilos.write('Total Kilos Ordered by Cliente')
    #tabla_kilos.bar_chart(data_kilos, color='#99BDFF')

    #table_on = display_toggles()
    #if table_on:
    

    st.write('Total Earned (\$), Kilos Ordered (Kg) y Debt (\$)')
    st.write(df_resumen)

    st.write('')
    st.write('')
    
    df_detalle_pedido['utilidad'] = df_detalle_pedido['utilidad'].apply(lambda x: int(x[2:-3].replace(',', '')) if x != '' else 0)

    df_utilidad = df_detalle_pedido.merge(df_producto, left_on='producto', right_on='id_producto')[['fecha', 'descripcion', 'utilidad']]
    df_utilidad['fecha'] = pd.to_datetime(df_utilidad['fecha'])
    df_utilidad = df_utilidad.sort_values(['fecha', 'utilidad'], ascending=[False, False])
    df_utilidad['semana'] = df_utilidad['fecha'].dt.strftime('%b %W')
    df_utilidad['semana'] = df_utilidad['semana'].apply(lambda x: ' '.join([mes.capitalize() if mes.isalpha() else mes for mes in x.split()]))

    df_plot = df_utilidad.groupby(['descripcion', 'fecha', 'semana']).sum().reset_index().sort_values(by='fecha', ascending=False)[['semana', 'descripcion', 'utilidad']]
    #st.write(df_plot)
    st.write(df_plot)#.set_index('semana'))
    #st.line_chart(df_plot, x='semana', y='utilidad', color='descripcion')

    #print(df_plot)#



       
    
