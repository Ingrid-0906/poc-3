import pandas as pd
import numpy as np
import math
from scipy.optimize import minimize
from .database import DATABASE
from scripts.analise_wallet import AnaliseCarteira
from scripts.basic_wallet import BasicStat

class tableHome():
    def __init__(self):
        self.DF_CARTEIRA = DATABASE().getCliente(path_data='./BD/PA-14112023.json')
        self.PERSONAS = DATABASE().getIPS(path_ips='./BD/IPS.json')
        self.tipo_investimento_para_coluna = {
            'Aluguel': 'Aluguel', 
            'Ações': 'Ações', 
            'COE': 'COE', 
            'Derivativos de Balção': 'Derivativos de Balção',
            'Fundos Imobiliarios' : 'Fundos Imobiliarios', 
            'Fundos de Investimento': 'Fundos de Investimento',
            'NPS': 'NPS',
            'Previdencia Privada': 'Previdencia Privada', 
            'Produtos Estruturados': 'Produtos Estruturados',
            'Renda Fixa': 'Renda Fixa',
            'Tesouro Direto':'Tesouro Direto'
        }

    def optimize_portfolio(self, e_r, mat_cov, n_ativos):
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
        otim_sharpe = minimize(min_func_sharpe, pesos_i, method='SLSQP', bounds=bnds, constraints=restri)
        peso_otimo = otim_sharpe['x']
        ret_otimo = port_ret(otim_sharpe['x'])
        vol_otimo = port_vol(otim_sharpe['x'])
        return peso_otimo, ret_otimo, vol_otimo

    def optimize_portfolio_min(self, e_r, mat_cov, n_ativos):
        """
            Cria a carteira otimizada escolhendo as posições que mantem ou supera em retorno e miniminiza o risco da carteira toda.
            O ponto de otimização sempre é igual, devido a base ser mutável em fator diário.
                
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
            
        def port_vol(pesos): #Função de cálculo de risco
            return math.sqrt(np.dot(pesos,np.dot(mat_cov, pesos)))
        
        def port_ret(pesos): #Função de cálculo de retorno
            return np.sum(e_r*pesos)
        
        tpl2 = 1 - 0.01
        restri = [{'type': 'eq', 'fun': lambda x: np.sum(x) - 1}]
        bnds = tuple((0.01, tpl2) for _ in range(n_ativos))
        pesos_i = np.array(n_ativos * [1 / n_ativos])

        otim_menor_vol = minimize(port_vol, pesos_i, method='SLSQP', bounds=bnds, constraints=restri)
        peso_otimo = otim_menor_vol['x']
        ret_otimo = port_ret(otim_menor_vol['x'])
        vol_otimo = port_vol(otim_menor_vol['x'])
        return peso_otimo, ret_otimo, vol_otimo

    def statsWallet(self):
        stats_hoje = {
            'id':[],
            'perfil': [],
            'pesos_hj': [],
            'retorno_hj': [],
            'risco_hj':[],
            'faixa_hj': [],
            'pp_saude': [],
            'status_saude': [],
            'ordem_ips':[]
        }
        
        for values in range(len(self.DF_CARTEIRA['id'])):
            # Salvando id e perfil
            stats_hoje['id'].append(self.DF_CARTEIRA['id'][values])
            stats_hoje['perfil'].append(self.DF_CARTEIRA['perfil'][values])
            
            # Gerando pesos
            DATA_PP = pd.DataFrame(self.DF_CARTEIRA['hoje'][values])
            for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
                DATA_PP[coluna] = DATA_PP.apply(
                    lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                    axis=1
                )
            
            # Salvando faixas da carteira vs. IPS faixas
            DATA_PP.insert(1, 'perfil', self.DF_CARTEIRA['perfil'][values].lower())
            DATA_BR = DATA_PP.copy()
            for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
                DATA_BR[coluna] = DATA_BR.apply(
                    lambda row: AnaliseCarteira().bandeira_classe(row, self.PERSONAS, tipo_investimento),
                    axis=1)
            # Salvando pesos hoje
            DATA_PP.drop('perfil', axis=1, inplace=True)
            stats_hoje['pesos_hj'].append(round(DATA_PP*100, 2))
            
            # Gerando saúde IPS e status // remover pl e perfil
            saude_hj = DATA_BR.iloc[:, 2:].apply(AnaliseCarteira().saude_investimentos, axis=1)
            stats_hoje['faixa_hj'].append(round(DATA_BR.iloc[:, 2:], 1))
            stats_hoje['pp_saude'].append(round(saude_hj.apply(lambda x: x[0]).values[0]*100, 0))
            stats_hoje['status_saude'].append(saude_hj.apply(lambda x: x[1]).values[0])
  
            #Salvando retorno e risco
            DATA_HY = pd.DataFrame(self.DF_CARTEIRA['historico'][values])
            _, _, e_r, _, mat_cov = BasicStat().calc_stats(DATA_HY)
            
            weight = DATA_PP.iloc[:, 1:]
            i_ret, i_vol = BasicStat().generate_position(pesos=weight.values[0], e_r=e_r, mat_cov=mat_cov)
            
            stats_hoje['retorno_hj'].append(round(i_ret[0]*100, 2))
            stats_hoje['risco_hj'].append(round(i_vol[0]*100, 2))
            
            # Ordenar segundo o IPS // observando as faixas de pesos
            DATA_REAL = DATA_BR.copy()
            DATA_REAL.drop('perfil', axis=1, inplace=True)
            
            for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
                DATA_REAL[coluna] = DATA_REAL.apply(lambda row: AnaliseCarteira().reais_classe(row, tipo_investimento),axis=1)
            
            DATA_REAL.drop('pl', axis=1, inplace=True)
            ordem = pd.DataFrame(data=[{k: v for k, v in sorted(DATA_REAL.loc[0].items(), key=lambda item: item[1])}])
            sugestao, _ = AnaliseCarteira().alinhamento_classe(ordem)
            stats_hoje['ordem_ips'].append(sugestao.to_dict(orient='records'))
        
        return stats_hoje
    
    def getCarteira(self):
        caderneta = {
            'id': [],
            'rentabil': [],
            'band_hoje': []
        }
        
        for values in range(len(self.DF_CARTEIRA['id'])):
            # Salvando id e perfil
            caderneta['id'].append(self.DF_CARTEIRA['id'][values])
            
            # Gerando pesos
            DATA_PP = pd.DataFrame(self.DF_CARTEIRA['hoje'][values])
            for tipo_investimento, coluna in self.tipo_investimento_para_coluna.items():
                DATA_PP[coluna] = DATA_PP.apply(
                    lambda row: AnaliseCarteira().porcento_classe(row, tipo_investimento),
                    axis=1
                )
            
            weight = DATA_PP.iloc[:, 1:]   

            #Salvando retorno e risco
            DATA_HC = pd.DataFrame(self.DF_CARTEIRA['historico'][values])
            tickers = DATA_HC.columns
            
            _, _, e_r, vol, mat_cov = BasicStat().calc_stats(DATA_HC)

            caderneta['rentabil'].append(
                {
                    'classe' : e_r.index,
                    'ret': e_r.values,
                    'vol': vol.values,
                    'mat_cov': mat_cov
                }
            )
            
            # 3. GENERATING THE UPPER AND LOWER BANDS
            peso_otimo_1, _, _ = self.optimize_portfolio(e_r, mat_cov, len(tickers))
            peso_otimo_2, _, _ = self.optimize_portfolio_min(e_r, mat_cov, len(tickers))

            # 4. CREATE THE LOWER & UPPER BANDS + POSITION
            cart_band_1 = pd.DataFrame(data=peso_otimo_1, index=tickers, columns=['max_sharpe'])
            cart_band_2 = pd.DataFrame(data=peso_otimo_2, index=tickers, columns=['min_risk'])
            cart_position = pd.DataFrame(data=weight.values[0], index=tickers, columns=['position'])

            # 5.2. MERGING ALL BANDS
            lower_uper_bands = pd.concat([cart_band_1, cart_band_2], axis=1, join='inner')
            lower_uper_bands['min'] = lower_uper_bands.min(axis=1)
            lower_uper_bands['max'] = lower_uper_bands.max(axis=1)
            
            caderneta['band_hoje'].append(lower_uper_bands.to_dict(orient='split'))
            
        return caderneta
            