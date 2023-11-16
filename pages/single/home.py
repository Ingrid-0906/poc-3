import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
from st_aggrid import AgGrid, GridUpdateMode
from st_aggrid.grid_options_builder import GridOptionsBuilder
from streamlit_modal import Modal
import streamlit.components.v1 as components

from .table import tableHome

def app():
    
    data = tableHome().statsWallet()
    
    col1, col2 = st.columns([0.7, 0.3])
    
    with col1:
        st.write('## Bem Vindo, Administrador!')
        st.write('Aqui podemos visualizar as carteiras e suas respectivas posições atuais baseadas')
        
        kpi1, kpi2, kpi3 = st.columns(3)
        with kpi1:
            st.metric('# Carteiras Ativas', '3', None)
        with kpi2:
            st.metric('# Interverções', '1', None)
        with kpi3:
            st.metric('# Média IPS Geral', np.mean([82, 82, 91]), None)
        
        data_source = {
            'Code': data['id'],
            'Perfil': data['perfil'],
            'Retorno Acum. 6mo': data['retorno_hj'],
            'Risco Acum. 6mo': data['risco_hj'],
            'Saúde IPS': data['pp_saude'],
            'Status Saúde': data['status_saude']
        }
        
        df = pd.DataFrame(data_source)
        gd = GridOptionsBuilder.from_dataframe(df)
        gd.configure_selection(selection_mode='single', pre_selected_rows=[1], use_checkbox=True)
        gd.configure_grid_options(alwaysShowHorizontalScroll=True)
        gd.configure_column(
            field="Code",
            header_name="Code",
            width=100
        )
        gd.configure_column(
            field="Perfil",
            header_name="Perfil",
            width=110
        )
        
        gd.configure_column(
            field="Retorno Acum. 6mo",
            header_name="Retorno Acum. 6mo (p.p)",
            width=190
        )
        gd.configure_column(
            field="Risco Acum. 6mo",
            header_name="Risco Acum. 6mo (p.p)",
            width=180
        )
        gd.configure_column(
            field="Saúde IPS",
            header_name="Saúde IPS (p.p)",
            width=140
        )
        gd.configure_column(
            field="Status Saúde",
            header_name="Saúde IPS",
            width=120
        )
        gridoptions = gd.build()
        grid_table = AgGrid(df, height=250, gridOptions=gridoptions,
                            update_mode=GridUpdateMode.SELECTION_CHANGED,
                            custom_css={
                                "#gridToolBar": {
                                    "padding-bottom": "0px !important",
                                    },
                                ".ag-root-wrapper": {
                                    "border": "1px solid transparent !important"
                                }
                                }
                            )
        
    with col2:
        if grid_table["selected_rows"]:
            st.write('### Detalhes Adicionais')
            selected_row = grid_table["selected_rows"]
            id_selected = grid_table["selected_rows"][0]['Code']
            
            for key in range(len(data['id'])):
                if data['id'][key] == id_selected:
                    st.write('##### Faixas Carteira vs. IPS')
                    data_chart = pd.DataFrame(data['faixa_hj'][key]).T
                    data_chart.rename(columns={0: 'val'}, inplace=True)
                    
                    data_chart["Color"] = np.where(data_chart["val"]< 0, '#ff6f69', '#50ff7f')
                    
                    fig = px.bar(data_chart, x=data_chart.index, y=data_chart['val'])
                    fig.update_traces(marker_color=data_chart["Color"])
                    st.plotly_chart(fig, use_container_width=True)
                    
                    st.write('##### IPS Allocation')
                    data_alloc = pd.DataFrame(data['ordem_ips'][key])
                    
                    gd2 = GridOptionsBuilder.from_dataframe(data_alloc)
                    gd2.configure_selection(use_checkbox=False)
                    gd2.configure_column(
                        field="ativo",
                        header_name="Target",
                        width=130
                    )
                    gd2.configure_column(
                        field="realocar",
                        header_name="Classe-Fonte",
                        width=130
                    )
                    gd2.configure_column(
                        field="valor_estimado_R$",
                        header_name="Montante Total",
                        width=130
                    )
                    gridoptions2 = gd2.build()
                    grid_table2 = AgGrid(data_alloc, height=250, gridOptions=gridoptions2,
                                        update_mode=GridUpdateMode.SELECTION_CHANGED,
                                        custom_css={
                                            "#gridToolBar": {
                                                "padding-bottom": "0px !important",
                                                },
                                            ".ag-root-wrapper": {
                                                "border": "1px solid transparent !important"
                                            }
                                            }
                                        )
    