import pandas as pd
import numpy as np
import streamlit as st
from .database import DATABASE
from .table import tableHome

def gerarTAB(index, metrica, x, TB, RT, RK, DT):
    col1, col2 = st.columns([0.7, 0.3])
    dtframe = pd.DataFrame(DT['data'][x][index][TB]).T

    dtframe.insert(0, 'Peso Atual', DT['peso'][x][index])
    dtframe.rename(columns={0: 'Produtos', 
                        1: 'Retorno Acum. 6mo', 
                        2: 'Volatilidade Acum. 6mo'}, inplace=True)
    dtframe['Status Ativo 6mo'] = ['Sem Movimento' if r == 0.0 else 'Movimento' for r in dtframe['Retorno Acum. 6mo']]
    dtframe['Performance Atual'] = ['Boa' if u > 0 else 'Ruim' for u in dtframe['Retorno Acum. 6mo']]
    dtframe['Retorno Acum. 6mo'] = dtframe['Retorno Acum. 6mo']*100

    with col1:
        k1, k2, k3, k4 = st.columns(4)
        with k1:
            st.metric('# Produtos', len(dtframe['Produtos']), None)
        with k2:
            st.metric(f'Retorno em {TB}', RT, None)
        with k3:
            st.metric(f'Risco em {TB}', RK, None)
        with k4:
            st.metric('Faixa IPS', metrica, None)
        
        kfc = dtframe[dtframe['Peso Atual'] > 0.1]  
        st.data_editor(kfc, hide_index=True)

    with col2:
        st.markdown(f'### Otimização em {TB}')
        if sum(dtframe['Retorno Acum. 6mo']) == 0:
            st.write('Não é possível calcular uma re-alocação devido ao ativo estar sem movimentação ou a carteira possuir apenas um único produto')
        else:
            st.write('Baseado na performance durante 6 meses históricos e visando a otimização da classe temos:')  
            
            x1, x2 = st.columns(2)
            
            with x1:
                st.metric('Retorno Otimizado', round(DT['sugestao'][x][index]['ret_otimo'], 2), None)
            with x2:    
                st.metric('Risco Otimizado', round(DT['sugestao'][x][index]['vol_otimo'], 2), None)
            
            if np.nan in DT['sugestao'][x][index]['peso_otimo']:
                st.write('Não foi possível determinar algum produto com retorno e risco acima da média. Pesos distibuidos igualmente.')
            else:
                # Chart do reposicionamento da carteira
                peso_chart = pd.DataFrame(DT['sugestao'][x][index]['peso_otimo'][0])
                peso_chart.loc[len(peso_chart)] = ['Soma Outros', 1-sum(peso_chart['pesos'])]
                st.bar_chart(data=peso_chart, x='ativos', y='pesos', use_container_width=True)


def app():
    
    DATA = DATABASE().getAtivos(path_data='./BD/PA-14112023.json')
    data = tableHome().statsWallet()
    base = tableHome().getCarteira()
    
    row1, row2 = st.columns([0.81, 0.19])
    with row1:
        st.write('## Área das Carteiras')
        st.write('Aqui podemos observar as carteiras de forma individual e simular uma realocação baseando-se somente em ativos')

    with row2:
        option = st.selectbox('Selecione o IDCode', (DATA['id']))
        
    tabs = list()
    for x in range(len(DATA['id'])):
        if DATA['id'][x] == option:
            R = pd.DataFrame({'classe': base['rentabil'][x]['classe'],
                              'ret': base['rentabil'][x]['ret']*100,
                              'vol': base['rentabil'][x]['vol']*100})
            
            for y in range(len(DATA['data'][x])):
                lb = list(DATA['data'][x][y].keys())[0]
                tabs.append(lb)
               
            tab0, tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10 = st.tabs(tabs)
            with tab0:
                index = 0
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    
            with tab1:
                index = 1
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    
            with tab2:
                index = 2
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)

            with tab3:
                index = 3
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    
            with tab4:
                index = 4
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                                      
            with tab5:
                index = 5
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                           
            with tab6:
                index = 6
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                         
            with tab7:
                index = 7
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                          
            with tab8:
                index = 8
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    
            with tab9:
                index = 9
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    
            with tab10:
                index = 10
                
                if (len(DATA['data'][x][index][tabs[index]]) == 1) and (np.nan in DATA['data'][x][index][tabs[index]]):
                    st.write(f'Não foi encontrado nenhum produto associato com a classe de {tabs[index]} nos últimos 6 meses históricos. Por favor, verifique com o setor de dados para mas detalhes.')
                    pass
                else:
                    TB = tabs[index]
                    DT = DATA
                    metrica = data['faixa_hj'][x][TB][0]
                    RT = round(R[R['classe'] == TB]['ret'].values[0], 2)
                    RK = round(R[R['classe'] == TB]['vol'].values[0], 2)
                    gerarTAB(index, metrica, x, TB, RT, RK, DT)
                    