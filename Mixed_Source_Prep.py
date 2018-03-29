import pandas as pd
import numpy as np
import pprint as pp
import ast
import re

def reg_ex(stryng):

    """ A regular expression check to see if the first character in a string is whitespace """
    pattern = re.compile("^\s.*$")

    if pattern.match(stryng):
        return stryng[1:]
    else:

        return stryng

def oneFile():

    """ Merges two specified excel sheets (Academia.xlsm and Industry.xlsm) into a single dataframe. Exports this dataframe to 'DataPrep/merged.xlsx' """

    academia = pd.read_excel('DataPrep/Academia.xlsm', sheet_name = 'Universities - projects')
    academia = academia[["University Name", "Project Name", "Partners", "Funding", "Classification", "Source"]]
    academia["Project Name"].replace('', np.nan, inplace=True)
    academia.dropna(subset=["Project Name"], inplace=True)
    academia["Project Name"].replace(np.nan, '', inplace=True)
    academia.columns = ["projLead", "projName", "projCollab", "projFunding", "projGrouping", "Source"]

    industry = pd.read_excel('DataPrep/Industry.xlsm')
    industry = industry[["Company Name", "Project Name", "UK Partners", "Classification", "Source"]]
    industry["Project Name"].replace('', np.nan, inplace=True)
    industry.dropna(subset=["Project Name"], inplace=True)
    industry["Project Name"].replace(np.nan, '', inplace=True)
    industry.columns = ["projLead", "projName", "projCollab", "projGrouping", "Source"]
    industry["projFunding"] = ""

    frames = [academia, industry]

    df = academia.append(industry, ignore_index=True)
    df.to_pickle('Pickles/excel_merged.pickle')
    df.to_excel('DataPrep/merged.xlsx')

def standardize():

    """ An extremely ugly and inefficient effort to correct typos and inconsistencies in the base data-set. A dictionary of corrections (badDict) is hard coded and every value in projCollab and projLead has the
    badDict passed over it. """

    df = pd.read_pickle('Pickles/excel_merged.pickle')

    badDict = {
    'Alcatel-Lucent':'Alcatel Lucent',
    'Alcatel-lucnet':'Alcatel Lucent',
    'Alcatel-lucent':'Alcatel Lucent',
    'Alcatel-Lucent':'Alcatel Lucent',
    'Alcatel-Lucent Technologies':'Alcatel Lucent',
    'Alcatel-lucent':'Alcatel Lucent',
    'ATOS': 'Atos',
    'Athens Information Technology AIT':'Athens Information Technology',
    'BlueWireless':'Blu Wireless',
    'BAE Systems':'BAE',
    'BT Group':'BT',
    'British Telecommunications Plc':'BT',
    'Blu Wireless Technology Limited':'Blu Wireless',
    'BlueWireless': 'Blu Wireless',
    'Blue Wireless': 'Blu Wireless',
    'Blu Wireless Technology':'Blu Wireless',
    'Brisol': 'Bristol',
    'CORSA Technology':'CORSA',
    'CREAT-NET':'CREATE-NET',
    'Cabridge':'Cambridge',
    'Cambidge':'Cambridge',
    'Cardiff ':'Cardiff',
    'China Mobile Limited':'China Mobile',
    'Cisco Systems UK':'Cisco',
    'CISCO': 'Cisco',
    'Cobham Wireless': 'Cobham',
    'Deutche Telekom':'Deutsche Telekom',
    'Deutsce Telecom':'Deutsche Telekom',
    'Deutsche Telecom':'Deutsche Telekom',
    'Deutsche telecom':'Deutsche Telekom',
    'Deutsce Telecom':'Deutsche Telekom',
    'Deutsche Telecom':'Deutsche Telekom',
    'Deutsche telecom':'Deutsche Telekom',
    'Eurecom':'Eurescom',
    'EURESCOM':'Eurescom',
    'Geant (UK)':'Geant',
    'Hewlett-Packard Company Inc':'HP',
    'Herriot-Wat':'Heriot-Watt',
    'Herrior-Wattt': 'Heriot-Watt',
    'Huawei ...':'Huawei',
    'Huawei Technologies (UK) Co. Ltd':'Huawei',
    'Huawei Technologies Co Limited':'Huawei',
    'Huawei …':'Huawei',
    'IPAccess':'IP.Access',
    'Interdigital':'InterDigital',
    'Intrasoft ...':'Intrasoft',
    'IPACCESS': 'IPAccess',
    'Keisight':'Keysight',
    'Kingston University London': 'Kingston',
    'KCL': 'Kings College',
    'Kings College London': 'Kings College',
    'Colleage': 'College',
    'Lancaster University':'Lancaster',
    'London Internet Exchange Ltd':'London Internet Exchange',
    'Ltd': '',
    'LTD':'',
    'Limited': '',
    'LIMITED':'',
    'Liverpool John Moores ':'Liverpool John Moores',
    'NEC Telecom MODUS Ltd':'NEC',
    'NOKIA': 'Nokia',
    'O2 (UK) Ltd':'O2',
    'MobileVCE':'Mobile VCE',
    'Oxford ..':'Oxford',
    'Orange Corporate services': 'Orange',
    'Qinetiq':'QinetiQ',
    'Quinetiq':'QinetiQ',
    'QinetiQ Ltd':'QinetiQ',
    'Roke Manor Research':'Roke',
    'Real Wireless Limited': 'Real Wireless',
    'SONY' : 'Sony',
    'Samsung Electronics Research Institute':'Samsung',
    'Sterlite Technologies Limited':'Sterlite Technologies',
    'Queen Marry (London)':'Queen Mary',
    'Queen Mary (London)':'Queen Mary',
    #'Queen Mary': 'Queen Mary (London)',
    'Queen Mary, London':'Queen Mary',
    'Queen Marry London':'Queen Mary',
    'Queen Mary London':'Queen Mary',
    'Queen\'s Univ (Belfast)':'Queen\'s Univ. (Belfast)',
    'Quenn\'s (Belfast)':'Queen\'s Univ. (Belfast)',
    'Queenz\'s Belfast':'Queen\'s Univ. (Belfast)',
    'Queens\'s Belfast':'Queen\'s Univ. (Belfast)',
    'Queens Belfast': 'Queen\'s Univ. (Belfast)',
    'Queens Univ (Belfast)': 'Queen\'s Univ. (Belfast)',
    'QuinetiQ': 'QinetiQ',
    'Quenns (Belfast)': 'Queen\'s Univ. (Belfast)',
    'Thales Research and Technology UK Ltd':'Thales',
    'Toshiba Research Europe Ltd':'Toshiba',
    'University College London':'UCL',
    'University of ':'',
    ' University': '',
    'University': '',
    'Uni. of ':'',
    'Uni ':'',
    'UNIVERSITY OF SURREY': 'Surrey',
    'Rohde Schwarz':'Rohde & Schwarz',
    'Rohde & Swarz':'Rohde & Schwarz',
    'Zeetta Net.':'Zeetta',
    'Zeetta Networks':'Zeetta',
    'Zeeta Networks': 'Zeettaa',
    'ZTE Wistron Telecom AB':'ZTE',
    'Zinwave Ltd':'Zinwave',
    '…':'',
    '...': '',
    '..': '',
    '. . .': '',
    '...': '',
    '... .':'',
    '.':''
    }

    df.reset_index(inplace=True, drop=True)
    # this could be more efficiently split into a call-able function, I ran out of time

    df['projLead'] = df['projLead'].apply(lambda x: reg_ex(x))

    for row in range(len(df['projCollab'])):

        s = (df.at[row,'projCollab'])

        if type(s) == str:

            s = s.replace("'","")
            s = reg_ex(s)

            for key in badDict:

                s = s.replace(key, badDict[key])
                s = s.strip()

            df.at[row,'projCollab'] = s

        elif type(s) == list:

            newList = []
            for sub in s:

                xyz = sub.replace("'","")
                xyz = xyz.strip()
                xyz = reg_ex(xyz)
                for key in badDict:
                    xyz = xyz.replace(key, badDict[key])
                xyz = xyz.strip()
                newList.append(xyz)

            df.at[row,'projCollab'] = newList

    for row in range(len(df['projLead'])):

        s = (df.at[row,'projLead'])

        if type(s) == str:

            s = s.replace("'","")

            for key in badDict:

                s = s.replace(key, badDict[key])
                s = s.strip()

            df.at[row,'projLead'] = s

        elif type(s) == list:

            newList = []
            for sub in s:
                xyz = sub.replace("'","")
                xyz = xyz.strip()
                for key in badDict:
                    xyz = xyz.replace(key, badDict[key])
                xyz = xyz.strip()
                newList.append(xyz)

            df.at[row,'projLead'] = newList

    #print(df['projCollab'].values.tolist())
    #df.drop_duplicates(subset="projName", keep='first',inplace=True)
    df = df.replace(np.nan, '', regex=True)
    df.reset_index(inplace=True, drop=True)
    df.to_excel('mergedt.xlsx')
    df.to_pickle('Pickles/classifiedDF.pickle')

def listify():

    """ Converts the projCollab and projGrouping columns into lists (to make later processing easier). """

    df = pd.read_pickle('Pickles/classifiedDF.pickle')

    try:
        df['projCollab'] = df['projCollab'].apply(lambda x: x.split(','))
    except:
        AttributeError

    try:
        df['projGrouping'] = df['projGrouping'].apply(lambda x: x.split(','))
    except:
        AttributeError

    df.to_pickle('Pickles/classifiedDF.pickle')


# oneFile()
# standardize()
# listify()
