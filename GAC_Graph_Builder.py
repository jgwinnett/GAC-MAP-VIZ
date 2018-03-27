import pandas as pd
import numpy as np
import pprint as pp
import ast

# def dropEmpties():
#     df = pd.read_excel('All_Projects.xlsx')
#
#     df.replace('', np.nan, inplace=True)
#
#     df.dropna(axis=0, how='any', thresh=2, inplace=True)
#     df.to_excel('All_Projects.xlsx')
#     df.to_pickle('Pickles/allProjectsConnected.pickle')

def standardizeNames():

    # Dev Note: if merging this into the same folder as GAC will need to address this over-writing the classified DF.

    df = pd.read_pickle('Pickles/classifiedDF.pickle')
    try:
        df['projApplic'] = df['projApplic'].apply(lambda x: x.upper())
        temp = df.groupby('projApplic')
        df = temp.get_group('YES')
    except:
        KeyError
    badDict = {
    'Alcatel-Lucent':'Alcatel Lucent',
    'Alcatel-lucnet':'Alcatel Lucent',
    'Alcatel-lucent':'Alcatel Lucent',
    'Alcatel-Lucent':'Alcatel Lucent',
    'Alcatel-Lucent Technologies':'Alcatel Lucent',
    'Alcatel-lucent':'Alcatel Lucent',
    'Athens Information Technology AIT':'Athens Information Technology',
    'BlueWireless':'Blu Wireless',
    'BAE Systems':'BAE',
    'BT Group':'BT',
    'British Telecommunications Plc':'BT',
    'Brisol': 'Bristol',
    'Blu Wireless Technology Limited':'Blu Wireless',
    'BlueWireless': 'Blu Wireless',
    'Blu Wireless Technology':'Blue Wireless',
    'CORSA Technology':'CORSA',
    'CREAT-NET':'CREATE-NET',
    'Cabridge':'Cambridge',
    'Cabridge':'Cambridge',
    'Cambidge':'Cambridge',
    'Cardiff ':'Cardiff',
    'China Mobile Limited':'China Mobile',
    'Cisco Systems UK':'Cisco',
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
    'Huawei ...':'Huawei',
    'Huawei Technologies (UK) Co. Ltd':'Huawei',
    'Huawei Technologies Co Limited':'Huawei',
    'Huawei …':'Huawei',
    'IPAccess':'IP.Access',
    'Interdigital':'InterDigital',
    'Intrasoft ...':'Intrasoft',
    'Keisight':'Keysight',
    'Lancaster University':'Lancaster',
    'London Internet Exchange Ltd':'London Internet Exchange',
    'Liverpool John Moores ':'Liverpool John Moores',
    'NEC Telecom MODUS Ltd':'NEC',
    'O2 (UK) Ltd':'O2',
    'MobileVCE':'Mobile VCE',
    'Oxford ..':'Oxford',
    'Qinetiq':'QinetiQ',
    'Quinetiq':'QinetiQ',
    'QinetiQ Ltd':'QinetiQ',
    'Roke Manor Research':'Roke',
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
    'Quenns (Belfast)': 'Queen\'s Univ. (Belfast)',
    'Thales Research and Technology UK Ltd':'Thales',
    'Toshiba Research Europe Ltd':'Toshiba',
    'University College London':'UCL',
    'University of ':'',
    'Uni. of ':'',
    'Uni ':'',
    'Rohde Schwarz':'Rohde & Schwarz',
    'Rohde & Swarz':'Rohde & Schwarz',
    'Zeetta Net.':'Zeetta',
    'Zeetta Networks':'Zeetta',
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

    #projName
    #	projDesc
    #	projLead
    #projCollab
    #projFunding
    #projGrouping
    #projSource


    df.reset_index(inplace=True, drop=True)

    for row in range(len(df['projCollab'])):
        s = (df.at[row,'projCollab'])

        if type(s) == str:
            for key in badDict:
                s = sub.replace("'","")
                s = sub.replace(" ","")
                s = s.replace(key, badDict[key])

            df.at[row,'projCollab'] = s

        elif type(s) == list:

            newList = []
            for sub in s:
                xyz = sub.replace("'","")
                xyz = xyz.strip()
                for key in badDict:
                    xyz = xyz.replace(key, badDict[key])
                newList.append(xyz)

            #print(newList)
            #print(df.at[row,'projCollabl'])
            df.at[row,'projCollab'] = newList
            #print(df.at[row,' '])

    for row in range(len(df['projLead'])):
        s = (df.at[row,'projLead'])
        #print(type(s))

        xyz = s.replace('University of ', '')
        #print("Replace 'university of ' - : " + xyz)
        xyz = xyz.replace(' University','')

        for key in badDict:
            xyz = xyz.replace(key, badDict[key])
    #    print(xyz)
        df.at[row,'projLead'] = xyz
    #print(df['projCollab'].values.tolist())
    df.drop_duplicates(subset="projName", keep='first',inplace=True)
    df.reset_index(inplace=True, drop=True)
    df.to_pickle('Pickles/classifiedDF.pickle')
    df.to_excel('test.xlsx')

def setting(df):

        setValz = set()
        listy = df.projCollab.values.tolist()

        #pp.pprint(listy)

        for l in listy:

            # if type(l) == str:
            #     if "," in l:
            #         ist = l.split(",")
            #         for splits in ist:
            #             splits = splits.strip()
            #             setValz.add(splits)
            #     else:
            #         l = l.strip()
            #         setValz.add(l)
            if type(l) == list:
                for val in l:
                    xyz = val.replace("'","")
                    xyz = xyz.strip()
                    #pp.pprint(xyz)
                    setValz.add(xyz)
            else:
                print(str(l) + " is not a list!!")


        listy = df['projLead'].values.tolist()

        for l in listy:

            # toList appears to transmute lists in literal strings?
            if type(l) == str:
                if l[0:1] == '[':
                    li = ast.literal_eval(l)
                    for splits in li:
                    #    pp.pprint(splits)
                        setValz.add(splits)
                else:
                    l = l.strip()
                    setValz.add(l)
            else:
                print(l + " is not a list!")

        return setValz

def findEdges(instSet):

    from collections import defaultdict


    tree = lambda: defaultdict(tree)
    linkDict = tree()

    df = pd.read_pickle('Pickles/classifiedDF.pickle')
    df= df.replace(np.nan,'', regex=True)

    # create baseline dictionaries
#    instSet = setting(df)
    #pp.pprint(instSet)
    for inst in instSet:

        linkDict[inst] = {}


    for i in linkDict:
        for inst in instSet:
            if i != inst:
                linkDict[i][inst] = 0

    #pp.pprint(linkDict)
    # create edges

    targetCols = ['projLead', 'projCollab']
    length = len(df.index)

    cheekyCounter = 0

    for i in range(length):
        orgSet = set()

        for cols in targetCols:

            val = df.at[i, cols]
            if type(val) == list:
                for summat in val:
                    orgSet.add(summat)
            elif type(val) == str:
                if val[0:1] == '[':
                    SEND_HELP = ast.literal_eval(val)
                    for HELPERS in SEND_HELP:
                        orgSet.add(HELPERS)
                else:
                    orgSet.add(val)

            else:
                print("something myserious is afoot")


        orgSet = [x for x  in orgSet if x != ""]

        # iterate through this list
        for i in orgSet:
            for n in orgSet:
                if i != n:
                    try:
                        linkDict[i][n] = linkDict[i][n] + 1

                    except:
                        #print("Error happened")
                        TypeError


    for i in linkDict:
        for n in linkDict:
            if i != n:
                try:
                    if linkDict[i][n] < 1:
                        del linkDict[i][n]
                        #print("something worked")
                except:
                        #print("Something went wrong")
                        KeyError

    setSet = set()

    for i in linkDict:

        for key in linkDict[i].keys():
            setSet.add(key)

    return linkDict


def kostasGraphing():

    from collections import defaultdict


    tree = lambda: defaultdict(tree)
    linkDict = tree()

    df = pd.read_pickle('Pickles/classifiedDF.pickle')

    # create baseline dictionaries
    instSet = setting(df)

    for inst in instSet:
        #print(inst)
        linkDict[inst] = {}

    for i in linkDict:

        for inst in instSet:
            if i != inst:
                linkDict[i][inst] = 0

    # create edges

    targetCols = ['projLead', 'projCollab']
    length = len(df.index)

    cheekyCounter = 0

    for i in range(length):
        orgSet = set()

        for cols in targetCols:

            val = df.at[i, cols]


            if type(val) == list:
                orgSet.update(val)
            elif type(val) != float:
                s = val.split(',')
                for stringy in s:
                    stringy = stringy.strip()
                    orgSet.add(stringy)

        orgSet = [x for x  in orgSet if x != ""]

        # iterate through this list

        for i in orgSet:
            for n in orgSet:
                if i != n:
                    try:
                        linkDict[i][n] = linkDict[i][n] + 1

                    except:
                        #print("Error happened")
                        TypeError
    #
    for i in linkDict:
        for n in linkDict:
            if i != n:
                try:
                    if linkDict[i][n] == 0:
                        del linkDict[i][n]
                        #print("something worked")
                except:
                        print("Something went wrong")
                        KeyError

def stupidTextWorkaround(stryng):
    x = {
        'Queen Mary, London':'QUEEN MARY UNIVERSITY OF LONDON',
        'Queen Mary':'QUEEN MARY UNIVERSITY OF LONDON',
        'Queen Mary (London)': 'QUEEN MARY UNIVERSITY OF LONDON',
        'Queen\'s Belfast':'THE QUEEN\'S UNIVERSITY OF BELFAST',
        'Smart Antenna Technologies Limited':'SMART ANTENNA TECHNOLOGIES LTD',
        'Avanti Communications Limited': 'AVANTI COMMUNICATIONS LTD',
        'Royal Holloway, London': 'ROYAL HOLLOWAY AND BEDFORD NEW COLLEGE',
        'Brunel London': 'BRUNEL UNIVERSITY LONDON',
        'Imperial College London':'IMPERIAL COLLEGE OF SCIENCE TECHNOLOGY AND MEDICINE'
    }

    try:
        y = x[stryng]
        return y
    except:
        KeyError
        return stryng
# dropEmpties()
