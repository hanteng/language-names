# -*- coding: utf-8 -*-
#歧視無邊，回頭是岸。鍵起鍵落，情真情幻。
import os.path, glob
import requests
import pandas as pd
from lxml import etree
from io import StringIO


path_data = u'../data'
## Outpuing Lists
outputfn = os.path.join(path_data, "XML_language_pop_name_en.tsv")

URL_CLDR_XML = "http://unicode.org/repos/cldr/trunk/common/supplemental/supplementalData.xml"

r = requests.get(URL_CLDR_XML, stream=True)
r.raw.decode_content = True
data_xml = etree.parse(r.raw)



list_langpop_data = data_xml.xpath("//*/languagePopulation")

outcome=dict()
for x in list_langpop_data:
    l_c = x.attrib['type']
    y = x.getnext()
    l_n = y.text
    outcome.update({l_c:l_n})

df = pd.DataFrame.from_dict({"l_name":outcome})
df.index = df.index.rename("l_code")
df.to_csv(outputfn, sep='\t', encoding='utf-8',  header = True, index = True)

'''
    df = pd.DataFrame(outputlist_languages[key])
    df.to_csv(outputfn_tsv_by_locale.format(locale=key), sep='\t', encoding='utf-8',  header = False, index = False)


#df = pd.DataFrame(outputlist_languages['en'])
#df.to_csv(outputfn_tsv_by_locale.format(locale='en'), sep='\t', encoding='utf-8',  header = False, index = False)
'''
