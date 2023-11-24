import pandas as pd
import streamlit as st
#from connection import establish_conntection_client
from connection import load_the_spreadsheet, gsheet_conn
from gspread_dataframe import set_with_dataframe



def display_interface():
    st.title("Agregar pago")

    # Crear campos de entrada para los datos
    nombre_cliente = st.text_input("Cliente que pagó")
    flag_carniceria = st.checkbox("¿Es el número de una carnicería?", key='flag_carniceria_pago')
    if flag_carniceria:
        nombre_cliente = 'Carniceria ' + nombre_cliente
    monto = st.text_input("Monto")
    fecha = st.date_input("Fecha", key='fecha_pago')
    fecha = fecha.strftime("%Y-%m-%d")
    
    medio_pago = st.radio("Medio de pago", ['Transferencia', 'Efectivo', 'Otra'])
    descripcion = st.text_input("Descripción")

    if st.button("Agregar pago"):
        st.session_state.clicked = True

    return nombre_cliente, flag_carniceria, monto, fecha, medio_pago, descripcion



def agregar_pago(nombre_cliente, flag_carniceria, monto, fecha, medio_pago, descripcion):

    with st.spinner(text="Validando pago"):

        error_input_data = False
        sh = gsheet_conn()
        #df_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')

        sheet_pago = load_the_spreadsheet(sh, 'PAGO')
        sheet_clientes = load_the_spreadsheet(sh, 'CLIENTE')

        #VALIDACION CLIENTE      
        try:
            id_cliente = sheet_clientes[sheet_clientes['nombre'].str.upper()==nombre_cliente.upper()].id_cliente.values[0]
        except:
            st.error('No existe ese cliente. Intente nuevamente.')
            error_input_data = True


        # Agregar los nuevos datos a la hoja de Google Sheets
        if not error_input_data:
            num_filas = len(sheet_pago)
            num_pago = sheet_pago['id_pago'].values[-1] + 1
            
        
                
            #print(id_producto)
            nuevo_pago = [num_pago, int(id_cliente), monto, fecha, medio_pago, descripcion]
            sheet_pago.loc[len(sheet_pago)] = nuevo_pago
            set_with_dataframe(sh.worksheet('PAGO'), sheet_pago)

            st.subheader("Detalle del pago")
            st.table([nuevo_pago])
            # Mostrar un mensaje de confirmación
            #if 'clicked' not in st.session_state:
            #    st.session_state.clicked = False


            #if st.session_state.clicked:
            st.success("Pago agregado exitosamente.")
            st.session_state.clicked = False




def main_pagos():
    st.session_state.clicked = False
    nombre_cliente, flag_carniceria, monto, fecha, medio_pago, descripcion = display_interface()
    
    if nombre_cliente != '' and flag_carniceria != '' and monto != '' and medio_pago != '' and descripcion != '':
        if st.session_state.clicked:
            agregar_pago(nombre_cliente, flag_carniceria, monto, fecha, medio_pago, descripcion)