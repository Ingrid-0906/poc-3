import pandas as pd
import numpy as np
import math
import scipy.optimize as sco
from scripts.analise_wallet import AnaliseCarteira
from scripts.basic_wallet import BasicStat

def optimize_portfolio(e_r, mat_cov, n_ativos):
    """
        Cria a carteira otimizada escolhendo as posições que mantem ou supera em retorno e miniminiza o risco da carteira toda.
        
        pars:
            - e_r: media dos retornos
            - mat_cov: matriz de covariancia da carteira
            - n_ativos: # de ativos da carteira
        
        vars:
            - tpl2: máximo disponivel para ser alocado
            - restri: é do tipo igualdade que informa que a volatilidade deve ter como valor maximo 1
            - bnds: limites para cada ativo
            - pesos_i: pesos iguais para todos começarem
    """
        
    rf = ((0.8 + 1)**(1/252))-1 #Calcular taxa livre de risco

    def port_vol(pesos): #Função de cálculo de risco
        return math.sqrt(np.dot(pesos,np.dot(mat_cov, pesos)))
    
    def port_ret(pesos): #Função de cálculo de retorno
        return np.sum(e_r*pesos)
    
    # Estimar carteira de Sharpe Ratio máximo
    def min_func_sharpe(pesos):
        """
            Medida de performance que procura por segurança or uma carteira livre de risco.
            (retorno_esperado[portifolio] - free-risk[selic] / std[portifolio])
        """
        return -(port_ret(pesos)-rf) / port_vol(pesos)
    
    tpl2 = 1 - 0.01
    restri = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
    bnds = tuple((0.01, tpl2) for _ in range(n_ativos))
    pesos_i = np.array(n_ativos * [1 / n_ativos])

    # Otimização do Sharpe
    otim_sharpe = sco.minimize(min_func_sharpe, pesos_i, method='SLSQP', bounds=bnds, constraints=restri)
    peso_otimo = otim_sharpe['x']
    ret_otimo = port_ret(otim_sharpe['x'])
    vol_otimo = port_vol(otim_sharpe['x'])
    return peso_otimo, ret_otimo, vol_otimo
    

class DATABASE():
    def getIPS(self, path_ips):
        data = pd.read_json(path_ips)
        return data

    def getCliente(self, path_data):
        source = pd.read_json(path_data)
        
        posicao_hoje = {
                'id': [],
                'perfil': [],
                'hoje': [],
                'historico':[]
            }
        
        for key, values in source.items():
            posicao_hoje['id'].append(values['id'])
            posicao_hoje['perfil'].append(values['perfil'])
            
            ### Transformando os dados históricos em possição atual para tabela
            HY = pd.DataFrame(values['historico'])
            # Sum porque estamos somando todos os ativos // levando em consideração que um mesmo ativo não é atualizado duas vezes ou mais no dia
            df_pivot = HY.pivot_table(index='data_posicao', columns='categoria', values='valor_total', aggfunc='sum', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
        
            # Remover dados que nao fazem parte das classes no IPS
            HY_Clean = df_pivot.drop(columns=['data_posicao','Custodia Remunerada','Proventos','Saldo Projetado'])
            posicao_hoje['historico'].append(HY_Clean)
            
            # Get a ultima posicao atual
            HY_current = HY_Clean.tail(1)
            pl_actual = HY.groupby(['data_posicao'])['pl_total_mes_atual'].max().to_frame().iloc[-1]
            
            # Criando a carteira do administrador
            HY_current.insert(0, 'pl', pl_actual.values[0])
            posicao_hoje['hoje'].append(HY_current.reset_index(drop='index'))
            
        print(posicao_hoje)
        return posicao_hoje

    def getAtivos(self, path_data):
        source = pd.read_json(path_data)
        
        position_ativos = {
            'id': [],
            'perfil': [],
            'data': [],
            'peso': [],
            'sugestao': []
        }
        
        for _, values in source.items():
            position_ativos['id'].append(values['id'])
            position_ativos['perfil'].append(values['perfil'])
            
            HY = pd.DataFrame(values['historico'])
            # Máxima efetuada por dia de lançamento, se houve duas operações no mesmo produto
            df_pivot = HY.pivot_table(index='data_posicao', columns='categoria', values='valor_total', aggfunc='sum', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()
            
            # Remover dados que nao fazem parte das classes no IPS
            HY_Clean = df_pivot.drop(columns=['data_posicao','Custodia Remunerada','Proventos','Saldo Projetado'])
            
            # Separando os produtos e gerando histórico
            dts = pd.DataFrame(values['historico'])
            cats = list(HY_Clean.columns)
            
            W = list()
            M = list()
            O = list()
            for x in cats:
                dtb = dts[dts['categoria'] == x]
                dtb_pivot = dtb.pivot_table(index='data_posicao', columns='descricao', values='valor_total', aggfunc='max', fill_value=None).reset_index().rename_axis(None, axis=1).ffill()

                #
                n_ativo = len(dtb_pivot.iloc[:,1:].columns)
                if n_ativo > 1:     
                    _, _, e_r, vol, mat_cov = BasicStat().calc_stats(dtb_pivot.iloc[:,1:])
                    peso_otimo, ret_otimo, vol_otimo = optimize_portfolio(e_r=e_r, mat_cov=mat_cov, n_ativos=n_ativo)

                    otimo = pd.DataFrame([e_r.index, peso_otimo]).T
                    otimo[1] = np.around(otimo[1].astype(np.double), 2)
                    buck  = list()
                    if len(otimo[otimo[1] > (otimo[1].mean()+0.01)]) > 0:
                        fetch = otimo[otimo[1] > (otimo[1].mean()+0.01)]
                        buck.append({'ativos': fetch[0].to_list(), 'pesos': fetch[1].to_list()})
                    else:
                        buck.append(np.nan)
                    
                    #Salvando retorno e risco
                    W.append({x : [e_r.index, e_r.values, vol.values]})
                    M.append({'peso_otimo': buck, 'ret_otimo': ret_otimo*100, 'vol_otimo': vol_otimo*100})

                    pl = sum(dtb_pivot.iloc[:,1:].tail(1).values[0])
                    O.append((dtb_pivot.iloc[:,1:].tail(1).values[0] / pl)*100)
                else:
                    W.append({x : [np.nan]})
                    M.append({'peso_otimo': np.nan, 'ret_otimo': np.nan, 'vol_otimo': np.nan})
                    O.append(np.nan)
            
            position_ativos['data'].append(W)  
            position_ativos['sugestao'].append(M)
            position_ativos['peso'].append(O)
            
        return position_ativos
        
 