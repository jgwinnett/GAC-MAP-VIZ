# import Mixed_Source_Graph_Builder as Mixed_Graph_Builder
import GAC_Graph_Builder as Graph_Builder
import pandas as pd
import json
import ast
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import numpy as np

class dataWangler():

    def __init__(self):
        self.DF_main = None




        self.foreignUniVals = None
        self.UKUniVals = None
        self.eligiblenames = None
        self.veryDirtyWorkaround = ['FOCUS','FLUOR', 'GE', 'NI', 'OTE', 'ROKE', 'LONDON', 'ENGINEERING']


        ### FILE PATHS ###
        # Pickles
        self.CORDIS_Countries_Path = "Pickles/CORDIS_Countries.pickle"
        self.DF__main_Path = "Pickles/classifiedDF.pickle"

        # Dodgy .txt files

        self.foreignUniTxt_path = "Workaround txts/Foreign Unis.txt"
        self.UKUniTxt_path = "Workaround txts/UK Unis.txt"
        self.UK_companies_path = "Workaround txts/moreWorkarounds.txt"

        self.DF_load()

        self.node_jsonList = []
        self.edge_jsonList = []
        self.setzzz = Graph_Builder.setting((self.DF_main))
        self.linkDict =  Graph_Builder.findEdges(self.setzzz)
        self.instList = self.makeSetaList(self.setzzz)



    def loadWorkArounds(self):

        foreignUniTxt = open(self.foreignUniTxt_path,'r')
        UKUniTxt = open(self.UKUniTxt_path,'r')
        dfCordisNames = pd.read_pickle(self.CORDIS_Countries_Path)
        uk_comps = open(self.UK_companies_path, 'r')

        self.temp_workaround = uk_comps.read().splitlines()
        self.foreignUniVals = foreignUniTxt.read().splitlines()
        self.UKUniVals = UKUniTxt.read().splitlines()
        self.eligiblenames = dfCordisNames.name.values.tolist()

    def popIneligible(self):

        delSetList = []


        for inst in self.setzzz:


             nameCheck = Graph_Builder.stupidTextWorkaround(inst)
             nameCheck = nameCheck.upper()

            # print(nameCheck)
             firstFound = next((x for x in self.eligiblenames if nameCheck in x), None)
             #print(firstFound)
             if inst in self.temp_workaround:
                 pass
             elif inst in self.UKUniVals:
                pass
             elif inst in self.foreignUniVals:
                 self.linkDict.pop(inst)
                 delSetList.append(inst)
             elif firstFound is None:
                 self.linkDict.pop(inst)
                 delSetList.append(inst)
                 print(inst + " popped as not in CORDIS")
             elif nameCheck in self.veryDirtyWorkaround:
                 self.linkDict.pop(inst)
                 delSetList.append(inst)

        for inst in delSetList:
            self.setzzz.remove(inst)

        self.instList = list(self.setzzz)

    def nodeBuilder(self):

        for n, name in enumerate(self.instList):


            if name in self.UKUniVals:
                parentFlag = "UK_University"
            else:
                parentFlag = "UK_Industry"

            node_jsonDict = {}
            node_jsonDict = {
                "id": n + 1,
                "name": name,
                "instType": parentFlag
            }

            self.node_jsonList.append(node_jsonDict)

    def edgeBuilder(self):

        for i, row in enumerate(self.DF_main.values):


            #collab, fund, grouping, lead, name = row
            #name, desc, lead, collab, grouping, source, index = row
            source, collab, funding, grouping, lead, name = row

            try:
                lead = ast.literal_eval(lead)
            except:
                ValueError
                lead = [lead]

            # establish lead as edge source, errors are fine
            for x in lead:
                #x = Graph_Builder.stupidTextWorkaround(x)

                if x == "Cardiff ":
                    print("yay!")
                source_tar = x
                try:
                    source_match = next((t for t in self.node_jsonList if t['name'] == source_tar), None)
                    source_id = source_match['id']
                except:
                    KeyError
                    #print(x + " Error'd at source")
                    print(source_tar, source_match, source_id)
                    # construct directed edge for each collab
                try:
                    for inst in collab:
                        if inst != '':
                            target_tar = inst
                            target_match = next((t for t in self.node_jsonList if t['name'] == target_tar), None)
                            try:
                                target_id = target_match['id']
                                edge_jsonDict = {
                                        "source": source_id,
                                        "target": target_id,
                                        "numProj": 1
                                    }
                                self.edge_jsonList.append(edge_jsonDict)
                            except:
                                KeyError
                except:
                    TypeError

    def node_cleanup(self):

        counter = 0
        for i, name in enumerate(self.node_jsonList):

            #print(i, name)
            id = name["id"]

            if any(d['source'] == id for d in self.edge_jsonList):
                pass
            elif any(d['target'] == id for d in self.edge_jsonList):
                pass
            else:
                counter += 1
                del self.node_jsonList[i]
                print(str(name) + " popped in node cleanup")

        return counter

    def node_financials(self):

        df = self.DF_main

        grouped = df.groupby(by="projLead")
        df_wurds = sorted(list(grouped.groups))

        for n, node_dict in enumerate(self.node_jsonList):

            name = node_dict["name"]

            name_grouped = None

            try:
                name_grouped = grouped.get_group(name)
            except:
                KeyError
                #print(name + " does not lead any projects")

            if name_grouped is not None:
                name_grouped.reset_index(inplace=True)
                for n, val in enumerate(name_grouped["projFunding"]):

                    tempVal = 0

                    if type(val) is str:

                        val = val.replace(' ', '')
                        val = val.replace(',', '.')


                        if "EUR" in val:
                            tempVal = val[3:]
                            tempVal = float(tempVal)
                            tempVal = tempVal * 0.89
                        else:
                            tempVal = float(tempVal)
                    elif val == "":
                        pass
                    else:
                        tempVal = val


                    name_grouped.at[n, "projFunding"] = tempVal


                fundingTotal = name_grouped.agg({'projFunding' : ['sum']}).loc["sum", "projFunding"]
                fundingTotal = np.asscalar(fundingTotal)

                for i, n in enumerate(self.node_jsonList):
                    if n['name'] == name:
                        self.node_jsonList[i].update({'Funding': fundingTotal})

    def node_ProjectCount(self):

        df = self.DF_main

        grouped = df.groupby(by="projLead")

        for n in grouped:

            name = n[0]
            numProj = len(n[1])

            for i, n in enumerate(self.node_jsonList):


                if n['name'] == name:
                    self.node_jsonList[i].update({'numProjects': numProj})

    def edge_dupe_check(self):

        to_pop = []

        for i, edge in enumerate(self.edge_jsonList):
            for e in self.edge_jsonList[i+1:]:
                if edge == e:
                    edge["numProj"] += 1
                    to_pop.append(int(i+1))

        rev_to_pop = to_pop[::-1]
        for intz in rev_to_pop:

            del self.edge_jsonList[intz]


    def json_toDisk(self):

        with open('VegaViz/edges.json','w') as outfile:
            json.dump(self.edge_jsonList, outfile)

        with open('VegaViz/nodes.json','w') as outfile:
            json.dump(self.node_jsonList, outfile)

    def DF_load(self):

        self.DF_main = pd.read_pickle(self.DF__main_Path)

    def makeSetaList (self, set):

        lizt = []
        for vals in set:
            if vals != "":
                lizt.append(vals)
        return lizt





x = dataWangler()
x.loadWorkArounds()
x.popIneligible()
x.nodeBuilder()
x.node_ProjectCount()

x.node_financials()

x.edgeBuilder()

x.edge_dupe_check()

count = 20

while count > 0:
    y = x.node_cleanup()
    print(y)
    count -= 1
# nodes_dirty = True
# while nodes_dirty:
#     check = x.node_cleanup()
#     if check == 0:
#         nodes_dirty = False

x.json_toDisk()
