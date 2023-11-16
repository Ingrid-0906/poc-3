import streamlit as st
from streamlit_option_menu import option_menu
from pages.single import home
from pages.single import cart
from pages.single import otim_cart

st.set_page_config(layout="wide")

class MultiApp:

    def __init__(self):
        self.apps = []

    def add_app(self, title, func):

        self.apps.append({
            "title": title,
            "function": func
        })

    def run():
        with st.sidebar:
            st.markdown("""
                        <style>
                            div[data-testid="stSidebarUserContent"] {
                                padding: 0 1.5rem !important;
                            }
                        </style>
                        """, unsafe_allow_html=True)
            st.write('## Wallet Safe v.2.1')
            app = option_menu(
                menu_title='',
                options=['POC I - IPS','POC II - Otimização da Classe','POC III - Otimização da Carteira','POC IV - Sugestão de Ativos','POC V - Previsão da Eficiência'],
                icons=['house-fill','person-circle','trophy-fill','chat-fill','info-circle-fill'],
                default_index=0,
                styles={
                    "container": {"padding": "0 !important","background-color":'transparent !important'},
                    "icon": {"font-size": "13px"}, 
                    "nav-link": {"font-size": "13px", "text-align": "left", "margin":"5px 0px"},
                    "nav-link-selected": {"background-color": "#ccc"},}
                )

        
        if app == "POC I - IPS":
            home.app()
        if app == "POC II - Otimização da Classe":
            cart.app()
        if app == "POC III - Otimização da Carteira":
            otim_cart.app()
        
    run()            
