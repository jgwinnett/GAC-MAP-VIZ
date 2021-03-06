import GAC_Graph_Builder as Graph_Builder
import pandas as pd
import json
import ast
import numpy as np
from forex_python.converter import CurrencyRates

class dataWangler():

    """ This class is responsible for constructing the various .json files needed for the VEGA visualization. Processing is done predominantly by pandas and stored in python dictionaries
    before being written to disk. """


    def __init__(self):

        """ Stores variable names and file paths. Also calls upon GAC_Graph_Builder to generate a set of institutions and a dictionary of inst. to inst. relationships """
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

        """ Loads the workaround text files. These are used as stop-gaps for checking eligibility for inclusion (UK or not) """

        foreignUniTxt = open(self.foreignUniTxt_path,'r')
        UKUniTxt = open(self.UKUniTxt_path,'r')
        dfCordisNames = pd.read_pickle(self.CORDIS_Countries_Path)
        uk_comps = open(self.UK_companies_path, 'r')

        self.temp_workaround = uk_comps.read().splitlines()
        self.foreignUniVals = foreignUniTxt.read().splitlines()
        self.UKUniVals = UKUniTxt.read().splitlines()
        self.eligiblenames = dfCordisNames.name.values.tolist()

    def popIneligible(self):


        """ Removes nodes that should not be included, i.e. they are not U.K based. Unfortunately there's no clean programmatic way of assessing whether a company is "UK Based"
        (it's hard to even articulate a definition for that phrase).

        The first test is whether it appears in the CORDIS list of U.K companies. If not it is then checked against the
        different 'workaround texts'. If it's a value in the list of foreign univserities it is removed.

         I compiled these .txt files by hand as a quick'n'dirty way of bulk labelling instiutions.

        """

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

        """ Builds a list of dictionaries. Each dictionary constitutes a node and stores useful information inside it. In this function this creates the id number, stores the name
        and labels the node as being academic or industry """

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

        """ Constructs a list of dictionaries. Each dictionary represents an edge between two nodes. It stores the source, target and number of projects (links).

            This is done by iterating over each row in the dataframe. Links are only created between the projLead and projCollab, not intra projCollab.

            Each name in projLead/projCollab is checked against the list of nodes, if the id is found for both then the edge is created.

        """

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
                source_tar = x
                try:
                    source_match = next((t for t in self.node_jsonList if t['name'] == source_tar), None)
                    source_id = source_match['id']
                except:
                    KeyError
                    #print(x + " Error'd at source")
                    #print(source_tar, source_match, source_id)

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

        """ This cleans up orphan nodes - those without any edges listing the node as a source or target.

            Orphan nodes are mostly created when projects are recorded without collaborators or where the only collaborators were outside the U.K

            Iterates over the nodes and performs a check for the ID in the entire list of edges.
        """

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

        """ Modies the nodes to store financial information. Only stores the information for projects where the node name/ID is recorded as projLead within the dataframe.

            Information is stored by updating the node dictionary

            Some values are Euros and recorded within the dataframe as such. We use forex_python to convert currency based on live rates """

        df = self.DF_main

        c = CurrencyRates()

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
                            tempVal = c.convert('EUR', 'GBP', tempVal))
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

        """ Adds to node information by summing the number of projects a node is recorded as being projLead """

        df = self.DF_main

        grouped = df.groupby(by="projLead")

        for n in grouped:

            name = n[0]
            numProj = len(n[1])

            for i, n in enumerate(self.node_jsonList):


                if n['name'] == name:
                    self.node_jsonList[i].update({'numProjects': numProj})

    def edge_dupe_check(self):

        """ Removes duplicate edges when a projLead and projCollab work together on different projects. When a a duplicate edge is removed this is stored
        as an edge property to measure the number of collaborations """

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

        """ Writes the lists of dictionaries to json files named edges.json and nodes.json """

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




#
# x = dataWangler()
# x.loadWorkArounds()
# x.popIneligible()
# x.nodeBuilder()
# x.node_ProjectCount()
#
# x.node_financials()
#
# x.edgeBuilder()
#
# x.edge_dupe_check()
#
# count = 20
#
# while count > 0:
#     y = x.node_cleanup()
#     print(y)
#     count -= 1
# # nodes_dirty = True
# # while nodes_dirty:
# #     check = x.node_cleanup()
# #     if check == 0:
# #         nodes_dirty = False
#
# x.json_toDisk()
