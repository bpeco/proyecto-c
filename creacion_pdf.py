import streamlit as st
import  streamlit_toggle as tog
from streamlit_gsheets import GSheetsConnection
from gspread_pandas import Spread, Client
import numpy as np
import pandas as pd
from google.oauth2 import service_account
from st_aggrid import AgGrid




def load_the_spreadsheet(sh, spreadsheetname):
    
    worksheet = sh.worksheet(spreadsheetname)
    df = pd.DataFrame(worksheet.get_all_records())
    
    return df



def gsheet_conn():
    #conn = st.experimental_connection("gsheets", type=GSheetsConnection)
    #df = conn.read(worksheet="CLIENTE", spreadsheet='https://docs.google.com/spreadsheets/d/1ZYE380SOilw4aG9K61xIc6W23411yhmIAqyA9YKJiO8/')
    #st.dataframe(df)

    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']

    credentials = service_account.Credentials.from_service_account_info(
                    st.secrets["gcp_service_account"], scopes = scope)

    client = Client(scope=scope,creds=credentials)
    spreadsheetname = "datos"
    spread = Spread(spreadsheetname,client = client)

    sh = client.open(spreadsheetname)
    
    return sh

    # Check the connection
    #st.write(spread.url)



def start():
    sh = gsheet_conn()
    df_detalle_pedido = load_the_spreadsheet(sh, 'DETALLE_PEDIDO')
    df_cliente = load_the_spreadsheet(sh, 'CLIENTE')
    df_pagos = load_the_spreadsheet(sh, 'PAGO')

    df_detalle_pedido['costo_detalle'] = df_detalle_pedido['costo_detalle'].apply(lambda x: int(x[2:-3].replace(',', '')))
    df_pagos['monto'] = df_pagos['monto'].apply(lambda x: int(x[2:-4].replace(',', '')))
    

    df_facturacion_extended = df_detalle_pedido.merge(df_cliente, on='id_cliente')
    #st.write(df_facturacion_extended[['nombre', 'costo_detalle']].iloc[0]['costo_detalle'])
    df_facturacion = df_facturacion_extended[['nombre', 'costo_detalle']].groupby('nombre').sum().reset_index()
    df_facturacion.rename(columns={'nombre': 'Cliente', 'costo_detalle': 'Monto Facturado'}, inplace=True)


    AgGrid(df_facturacion_extended, )