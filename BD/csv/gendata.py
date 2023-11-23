import pandas as pd
import json
import io

if __name__ ==  '__main__':
    ips =  pd.read_csv('./IPS_MB.csv', delimiter=';')
    ips.to_json('IPS.json', orient='records')
    hist = pd.read_csv('./PA-08112023.csv', delimiter='|')
    
    carteira = {
        'id': 99,
        'perfil': 'Moderado',
        'hitorico': hist.to_dict()
    }
    
    with io.open('carteira-poc.json', 'w', encoding='utf-8') as outfile:
        json.dump(carteira, outfile)
    
