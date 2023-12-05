import multipage_streamlit as mt
import pagos, pedidos, estadisticas, envio_pdf#, creacion_pdf
#from connection import establish_conntection_client
import streamlit as st


app = mt.MultiPage()
st.header("Carne Squillo", divider='red')
app.add("Agregar pedido 🥩", pedidos.main_pedidos)
app.add("Agregar pago 💵", pagos.main_pagos)
#app.add("Estadísticas 📈", estadisticas.start)
app.add("Enviar PDF", envio_pdf.main_pdf)
#app.add("Envío de PDF 📈", creacion_pdf.start)
#app.add("Page B", page_a.run)
#app.run_selectbox()
app.run_expander()
#app.run_radio()
# alternatives: app.run_expander() or app.run_radio() if you prefer those 