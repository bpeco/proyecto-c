import streamlit as st


if 'clicked' not in st.session_state:
    st.session_state.clicked = False

def click_button():
    st.session_state.clicked = True

st.button('Ingresar pago', on_click=click_button)

if st.session_state.clicked:
    # The message and nested widget will remain on the page
    st.success("Pago agregado éxitosamente a GSheet.")