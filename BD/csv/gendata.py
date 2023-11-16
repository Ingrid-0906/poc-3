import pandas as pd
import json
import io

if __name__ ==  '__main__':
    ips =  pd.read_csv('./IPS_MB.csv', delimiter=';')
    ips.to_json('IPS.json', orient='records')
    hist = pd.read_csv('./PA-08112023.csv', delimiter='|')
    
    carteira_1 = {
        'id': 99,
        'perfil': 'Moderado',
        'hitorico': hist.to_dict()
    }

    carteira_2 = {
        'id': 134,
        'perfil': 'Conservador',
        'hitorico': hist.to_dict()
    }
    
    carteira_3 = {
        'id': 99,
        'perfil': 'Arrojado',
        'hitorico': hist.to_dict()
    }
    
    carteira = {
        '_id01': carteira_1,
        '_id02': carteira_2,
        '_id03': carteira_3
    }
    
    with io.open('14_11_2023-carteira-poc-2-1.json', 'w', encoding='utf-8') as outfile:
        json.dump(carteira, outfile)
    
