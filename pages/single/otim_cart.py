import pandas as pd
import numpy as np
import streamlit as st
from plotly import graph_objs as go
from .database import DATABASE
from .table import tableHome
from scripts.basic_wallet import BasicStat

def gerarCenarios(N, E_R, MAT_COV, TICKERS):
    # 3. BUILDING THE SCENARIOS
    p_ret, p_vol, p_pesos = BasicStat().generate_portfolios(n_ativos=N, e_r=E_R, mat_cov=MAT_COV)

    # 3.1. CREATING THE DATAFRAME OF ALL SCENARIOS
    pesos_df = pd.DataFrame(data=p_pesos, columns=TICKERS)
    rv_df = pd.DataFrame(data={'retorno': p_ret, 'volatil': p_vol}, columns=['retorno', 'volatil'])
    cenarios_df = pd.concat([rv_df, pesos_df], axis=1, join='inner')*100
    return cenarios_df

def gen_graph_3d(tx, p_vol, p_ret, e_r, mat_cov):
        rf = ((tx + 1) ** (1 / 252)) - 1
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter3d(
            x=list(p_vol*100),
            y=list(p_ret*100),
            z=list(((p_ret - rf) / p_vol)*100),
            name='Carteiras',
            mode='markers',
            marker=dict(size=6)
        ))

        fig.add_trace(go.Scatter3d(
            x=list(p_vol[:3]*100),
            y=list(p_ret[:3]*100),
            z=list(((p_ret[:3] - rf) / p_vol[:3])*100),
            name='Top Carteira',
            mode='markers',
            marker=dict(size=10, color='yellow')
        ))

        # tight layout
        fig.update_layout(scene=dict(xaxis_title='Risco',
                                    yaxis_title='Retorno',
                                    zaxis_title='índice Sharpe'),
                        margin=dict(l=0, r=0, b=0))
        fig.update_traces(hovertemplate='Risco=%{x}<br>Retorno=%{y}<br>Sharpe=%{z}<extra></extra>', 
                        selector=dict(type='scatter3d'))
        return st.plotly_chart(fig, use_container_width=True) 
      
def range_boundary(title, min, max, show):
    min = round(min*100, 2)
    max = round(max*100, 2)
    
    if show:
        disabled = False
    else:
        disabled = True
    
    if min != max:
        slider = st.slider(title, 
                  min, 
                  max, 
                  min, 
                  disabled=disabled)
    else:
        slider = st.slider(title, 
                  0.1, 
                  max, 
                  0.1, 
                  disabled=disabled)
    return slider


def app():
    data = tableHome().statsWallet()
    base = tableHome().getCarteira()
    
    row1, row2 = st.columns([0.81, 0.19])
    with row1:
        st.write('## Otimizador Carteira')
        st.write('Essa área foi construída usando como referência dados de retorno do portifólio calculado durante 6 meses históricos, para que de uma maneira geral, possamos ter uma otimização da carteira frente as suas classes.')
        st.markdown(''':red[Por Favor, escolha um ativo por vez. Múltipla escolha não suportada na versão de testes.]''')
    with row2:
        option = st.selectbox('Selecione o IDCode', (data['id']))
    
    
    for x in range(len(data['id'])):
        if data['id'][x] == option:
            weight = data['pesos_hj'][x]
            ips = data['faixa_hj'][x]
            bands = pd.DataFrame(data=base['band_hoje'][x]['data'], 
                                 index=base['band_hoje'][x]['index'],
                                 columns=base['band_hoje'][x]['columns'])
            
            tick = list(bands.index.values)
            half = int(np.round(len(tick)/2))
            
            col1 = st.columns(half)
            col2 = st.columns(len(tick)-half)
            
            st.session_state.disabled = True
            
            ids = ['id1', 'id2', 'id3', 'id4', 'id5', 'id6', 'id7', 'id8', 'id9', 'id10', 'id11']
            valor = ['v1', 'v2', 'v3', 'v4', 'v5', 'v6', 'v7', 'v8', 'v9', 'v10', 'v11']
            ticker = str()
            val = float()
            
            for i, _ in enumerate(col1):
                with col1[i]:
                    st.metric(tick[i], weight[tick[i]].values[0], ips[tick[i]].values[0])
                    ids[i] = st.checkbox('Habilitar', key=ids[i])
                    valor[i] = range_boundary(title=tick[i], min=bands['min'].iloc[i], max=bands['max'].iloc[i], show=ids[i])
                    if ids[i]:
                        st.session_state.disabled = False
                        val = valor[i]
                        ticker = tick[i]
                        
            for y, _ in enumerate(col2):
                i  = y + half
                with col2[y]:
                    st.metric(tick[i], weight[tick[i]].values[0], ips[tick[i]].values[0])
                    ids[i] = st.checkbox('habilitar', key=ids[i])
                    valor[i] = range_boundary(title=tick[i], min=bands['min'].iloc[i], max=bands['max'].iloc[i], show=ids[i])
                    if ids[i]:
                        st.session_state.disabled = False
                        val = valor[i]
                        ticker = tick[i]
                        
                        
            btn = st.button('Calcular', type='primary', key='btn', disabled=st.session_state.disabled)
            
            e_r = base['rentabil'][x]['ret']
            mat_cov = base['rentabil'][x]['mat_cov']
            
            cenarios_df = gerarCenarios(N=len(tick), E_R=e_r, MAT_COV=mat_cov, TICKERS=tick)
            
            if btn:
                minRisk, MaxRet = st.tabs(['Menor Risco', 'Maior Retorno'])
                SOURCE = cenarios_df[cenarios_df[ticker]<=val]
                dt_risk = SOURCE[SOURCE['retorno']>0].sort_values(by='volatil', ascending=True)[:10]
                dt_risk['retorno'] = round(dt_risk['retorno'], 2)
                dt_risk['volatil'] = round(dt_risk['volatil'], 2)
                
                dt_ret = SOURCE[SOURCE['retorno']>0].sort_values(by='retorno', ascending=False)[:10]
                dt_ret['retorno'] = round(dt_ret['retorno'], 2)
                dt_ret['volatil'] = round(dt_ret['volatil'], 2)
                
                with minRisk:
                    if len(dt_risk) > 0:
                        st.markdown("### Recomendados")
                        c1, c2, c3 = st.columns(3)
                        dt_chart = np.round(dt_risk.iloc[:,2:12])
                        with c1:
                            st.markdown(f"<h5 style='color: white;'>#1 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_risk['retorno'].iloc[0], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_risk['volatil'].iloc[0], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[0], color="#2727c2", use_container_width=True)

                        with c2:
                            st.markdown(f"<h5 style='color: white;'>#2 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_risk['retorno'].iloc[1], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_risk['volatil'].iloc[1], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[1], color="#ec4563", use_container_width=True)

                        with c3:
                            st.markdown(f"<h5 style='color: white;'>#3 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_risk['retorno'].iloc[2], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_risk['volatil'].iloc[2], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[2], color="#6ded66", use_container_width=True)
                        
                        row_1, row_2 = st.columns([0.4, 0.6])
                        with row_1:
                            gen_graph_3d(0.08, dt_risk['volatil'], dt_risk['retorno'], e_r, mat_cov)
                        with row_2:
                            st.markdown("### Outras Opções")
                            st.dataframe(data=dt_risk.iloc[2:], use_container_width=True, hide_index=True)
                    else:
                        st.write('Não há cenários com retornos positivos para essa carteira no momento.')
                        st.write(data)
                with MaxRet:
                    if len(dt_ret) > 0:
                        st.markdown("### Recomendados")
                        c1, c2, c3 = st.columns(3)
                        dt_chart = np.round(dt_ret.iloc[:,2:12])
                        with c1:
                            st.markdown(f"<h5 style='color: white;'>#1 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_ret['retorno'].iloc[0], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_ret['volatil'].iloc[0], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[0], color="#2727c2", use_container_width=True)

                        with c2:
                            st.markdown(f"<h5 style='color: white;'>#2 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_ret['retorno'].iloc[1], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_ret['volatil'].iloc[1], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[1], color="#ec4563", use_container_width=True)

                        with c3:
                            st.markdown(f"<h5 style='color: white;'>#3 Carteira</h5>", unsafe_allow_html=True)
                            st.markdown(f"<h1 style='color: white;'>{round(dt_ret['retorno'].iloc[2], 5)}</h1>", unsafe_allow_html=True)
                            st.markdown(f"<h5 style='color: gray;'>{round(dt_ret['volatil'].iloc[2], 2)}% volátil</h5>", unsafe_allow_html=True)
                            st.bar_chart(dt_chart.iloc[2], color="#6ded66", use_container_width=True)
                        
                        row_1, row_2 = st.columns([0.4, 0.6])
                        with row_1:
                            gen_graph_3d(0.08, dt_ret['volatil'], dt_ret['retorno'], e_r, mat_cov)
                        with row_2:
                            st.markdown("### Outras Opções")
                            st.dataframe(data=dt_ret.iloc[2:], use_container_width=True, hide_index=True)
                    else:
                        st.write('Não há cenários com retornos positivos para essa carteira no momento.')
                        st.write(data)
            
                
                
                
