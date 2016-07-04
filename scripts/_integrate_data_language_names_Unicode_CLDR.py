# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
import os.path, glob
import json
import icu # pip install PyICU
import pandas as pd

path_data = u'../data'
## Inputing Lists
inputfn_json_available_locales = os.path.join(path_data, "availableLocales.json")
inputfn_tsv_by_locale = os.path.join(path_data, "CLDR_language_name_{locale}.tsv")

## Outputing Lists
outputfn1 = os.path.join(path_data, "_all.tsv")
outputfn2 = os.path.join(path_data, "_all_in_its_language.tsv")


with open(inputfn_json_available_locales) as data_file:    
    available_locales = json.load(data_file)

df=pd.DataFrame()
for l in available_locales:
    df_= pd.read_csv(inputfn_tsv_by_locale.format(locale=l),
                    sep = '\t', encoding = 'utf-8',
                    header = None,
                    names = ['lang', 'name'],
                    keep_default_na = False, na_values = [])
    df_['locale'] = l
    if "-" in l:
        ll, lv = l.split("-", 1)
        df_['locale_l'] = l
        df_['locale_v'] = lv
    else:
        df_['locale_l'] = l
        df_['locale_v'] = ""
        
    df = pd.concat([df, df_])

df = df[['locale', 'locale_v', 'locale_l', 'lang', 'name']]

df.to_csv(outputfn1, sep='\t', encoding='utf-8',  header = False, index = False)
df.query('lang==locale').to_csv(outputfn2, sep='\t', encoding='utf-8',  header = False, index = False)

