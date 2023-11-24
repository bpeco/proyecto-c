import time
import streamlit as st
import pandas as pd
import datetime
from connection import load_the_spreadsheet, gsheet_conn
from gspread_dataframe import set_with_dataframe




def display_interface():
   #print('DISPLAY INTERFACE')
    st.title("Agregar pedido")

    # Crear campos de entrada para los datos
    nombre_cliente = st.text_input("Cliente")
    flag_carniceria = st.checkbox("¿Es el número de una carnicería?", key='flag_carniceria_pedido')
    if flag_carniceria:
        nombre_cliente = 'Carniceria ' + nombre_cliente
    fecha = st.date_input("Fecha", key='fecha_pedido')
    fecha = fecha.strftime("%Y-%m-%d")
    #producto = st.text_input("Producto")
    producto = st.selectbox('Producto', ('Media Res', 'Lomo', 'Bola de lomo', 'Asado', 'Paleta', 'Peceto', 'Cuadrada'))
    peso = st.text_input("Peso")
    precio, costo = st.columns(2)
    precio = st.text_input("Precio (kg)")

    if st.button("Agregar pedido"):
        st.session_state.clicked = True
    
    if len(precio) > 0 and producto == 'Media Res' and not st.session_state.clicked:
         with st.spinner(text="Buscando costo..."):
            costo = buscar_costo(int(peso))
            st.text(f'El costo de {producto} con un peso de {peso}kg a la fecha de hoy es: $ {costo}')
    
    
    return nombre_cliente, flag_carniceria, fecha, producto, peso, precio

 
def buscar_costo(peso):
    #print('BUSCANDO COSTO')
    sh = gsheet_conn()
    sheet_costos = load_the_spreadsheet(sh, 'COSTO')

    costo = sheet_costos[(sheet_costos['fecha_vigencia_hasta']=='') & (peso >= sheet_costos['peso_desde']) & (peso <= sheet_costos['peso_hasta'])].precio.values[0]

    return int(costo)

# Título de la aplicación
def agregar_pedido(nombre_cliente, flag_carniceria, fecha, producto, peso, precio):
    #print('AGREGAR PEDIDO')

    with st.spinner(text="Validando pedido"):

        error_input_data = False
        sh = gsheet_conn()
        #df_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')

        sheet_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')
        sheet_clientes = load_the_spreadsheet(sh, 'CLIENTE')
        sheet_productos = load_the_spreadsheet(sh, 'PRODUCTO')
        


        #VALIDACION CLIENTE      
        try:
            id_cliente = sheet_clientes[sheet_clientes['nombre'].str.upper()==nombre_cliente.upper()].id_cliente.values[0]
        except:
            st.error('No existe ese cliente. Intente nuevamente.')
            error_input_data = True

        #VALIDACION PRODUCTO
        try:
            id_producto = sheet_productos[(sheet_productos['descripcion'].str.upper()==producto.upper())].id_producto.values[0]
        except:
            st.error('No existe dicho producto con ese peso. Intente nuevamente.')
            error_input_data = True

            # Agregar los nuevos datos a la hoja de Google Sheets
        if not error_input_data:
                num_filas = len(sheet_detalle_pedido)
                num_det_pedido = sheet_detalle_pedido['id_detalle_pedido'].values[-1] + 1
                
                costo = buscar_costo(int(peso))
                nuevo_detalle = [num_det_pedido, int(id_cliente), fecha, int(str(id_producto)), float(peso), int(precio), float(peso)*int(precio), costo, "$"+str(float(peso)*int(precio)-costo*float(peso))]
                sheet_detalle_pedido.loc[len(sheet_detalle_pedido)] = nuevo_detalle
                set_with_dataframe(sh.worksheet('DETALLE_PEDIDO'), sheet_detalle_pedido)


                #sheet_detalle_pedido.append_row(nuevo_detalle)
                # sheet_detalle_pedido.update_cell('D'+str(num_filas+1) ,fecha)#.strftime('%Y/%m/%d'))
            
                # Mostrar un mensaje de confirmación
                st.success("Pedido agregado exitosamente.")

                # Puedes mostrar los datos ingresados en una tabla
                st.subheader("Detalle del pedido agregado:")
                st.table([nuevo_detalle])


def main_pedidos():
    st.session_state.clicked = False
    nombre_cliente, flag_carniceria, fecha, producto, peso, precio = display_interface()
    
    if nombre_cliente != '' and fecha != '' and producto != '' and peso != '' and precio != '':
        if st.session_state.clicked:
            agregar_pedido(nombre_cliente, flag_carniceria, fecha, producto, peso, precio)