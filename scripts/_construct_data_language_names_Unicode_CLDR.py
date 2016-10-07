# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
import os.path, glob
import json
import requests
import icu # pip install PyICU
import pandas as pd

path_data = u'../data'
## Outpuing Lists
outputfn_tsv_by_locale = os.path.join(path_data, "CLDR_language_name_{locale}.tsv")

URL_CLDR_JSON_LANGUAGES = "https://raw.githubusercontent.com/unicode-cldr/cldr-localenames-full/master/main/{locale}/languages.json"
URL_CLDR_JSON_LOCALES_AVA = "https://raw.githubusercontent.com/unicode-cldr/cldr-core/master/availableLocales.json"
URL_CLDR_JSON_LANGS_AVA = "https://raw.githubusercontent.com/unicode-cldr/cldr-localenames-full/master/main/en/languages.json" # Using English as the baseline

def url_request (url):
    r = requests.get(url)
    if r.status_code == 200:
        return r
    else:
        return None 


def load_json_list_locale (u):
    fn = os.path.join(path_data, os.path.split(u)[1])
    print (fn)
    try:
        with open(fn, 'r', encoding="utf-8") as infile:
            _select = json.load (infile)
            print ("Loaded from local file.")
    except:
        results = url_request (url  = u)
        if results is not None:
            try:
                _select = results.json()['availableLocales']['full']
                with open(fn, 'w', encoding="utf-8") as outfile:
                    outfile.write("{}".format(_select).replace("'",'"'))
                print ("Loaded from designated url.")
            except:
                print ("failed: json parsing")
                _select = None
        else:
            print ("failed: empty")
            _select = None
    return _select

def load_json_list_lang (u):
    fn = os.path.join(path_data, os.path.split(u)[1])
    print (fn)
    try:
        with open(fn, 'r', encoding="utf-8") as infile:
            _select = json.load (infile)
            print ("Loaded from local file.")
    except:
        results = url_request (url  = u)
        if results is not None:
            try:
                _select = results.json()['main']['en']['localeDisplayNames']['languages']
                with open(fn, 'w', encoding="utf-8") as outfile:
                    outfile.write("{}".format(_select).replace("'",'"'))
                print ("Loaded from designated url.")
            except:
                print ("failed: json parsing")
                _select = None
        else:
            print ("failed: empty")
            _select = None
    return _select

# Selected Locale(s) Construction
#locale_select = ['en'] # English is selected. Can be extended in the future  'zh-Hant-HK', 'zh-Hant-MO', 'zh-Hans', 'zh-Hans-SG'
#locale_select = ['zh-Hant'] # debug
#print (load_json_list (URL_CLDR_JSON_LOCALES_AVA))
locale_select = load_json_list_locale (URL_CLDR_JSON_LOCALES_AVA)

lang_select = load_json_list_lang (URL_CLDR_JSON_LOCALES_AVA)

# Note. More see Unicode specification (http://unicode.org/repos/cldr/trunk/common/collation/) and ICU Collation Demo http://demo.icu-project.org/icu-bin/collation.html


## Retrive data directly from unicode-cldr project hosted at github
print ("Retrieve data now ...")
locale_json={}
for l in locale_select:
    results = url_request (url  = URL_CLDR_JSON_LANGUAGES.format(locale=l))
    if results is not None:
        try:
            locale_json [l] = results.json()['main'][l]['localeDisplayNames']['languages']
        except:
            pass

## Preprocessing and Generating lists
print ("Preprocessing data now ...")

outputlist_languages={}
for key, value in locale_json.items():
    c_n=dict()
    r_n=dict()
    for k, v in value.items():
        ### Remove -alt-variant and -alt-short
        if "-alt-variant" in k:
            print ("not using:{}".format([k,v]))
            pass
        if "-alt-short" in k:  ## Using -alt-short if exists
            k=k.replace("-alt-short", "")
            print ("using:{}".format([k,v]))
            c_n.update({k:v})
               
        else:
            if k in c_n.keys():
                print ("not using:{}".format([k,v]))
            else:
                c_n.update({k:v})
   
    ### Sort by IBM's ICU library, which uses the full Unicode Collation Algorithm
    print (key)

    collator = icu.Collator.createInstance(icu.Locale('{lc}.UTF-8'.format(lc=key)))
    ### Make an exception for zh-Hant  --> zh-Hant-TW
    if key=="zh-Hant":
        collator = icu.Collator.createInstance(icu.Locale('{lc}.UTF-8'.format(lc="zh-Hant-TW")))

    #### Sort based on keys/codes
    #c_n_keys_sorted = sorted(list(c_n.keys()), key=collator.getSortKey)
    #outputlist_languages [key]  =  [(x, c_n[x]) for x in c_n_keys_sorted]

    #### Sort based on values/names
    c_n_values_sorted = sorted(list(c_n.values()), key=collator.getSortKey)
    n_c = {v: k for k, v in c_n.items()}
    outputlist_languages [key]  =  [(x, r_n[x]) for x in sorted(r_n.keys())] + [(n_c[x], x) for x in c_n_values_sorted]

    df = pd.DataFrame(outputlist_languages[key])
    df.to_csv(outputfn_tsv_by_locale.format(locale=key), sep='\t', encoding='utf-8',  header = False, index = False)


#df = pd.DataFrame(outputlist_languages['en'])
#df.to_csv(outputfn_tsv_by_locale.format(locale='en'), sep='\t', encoding='utf-8',  header = False, index = False)
