import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import ast
import math
from forex_python.converter import CurrencyRates

# total funding
# funding split
# funding per academic inst (broked down?)

class map_stats():

    """ This class is responsible for analysing and visualizing the output of GAC_MAP (or MIX_Source_Prep). Most functionality is focused on specifc data from Digital Catapult's 5G Mapping efforts
    and is not directly applicable to the output of GAC_MAP. It delivers funding totals for different sources and a basic bar graph. It also offers an institution by institution breakdown by source, with stacked bar graphs"
    """

    def __init__(self):

        self.df_path = 'Pickles/classifiedDF.pickle'
        self.df = pd.read_pickle(self.df_path)
        self.c = CurrencyRates()

        self.funding_overview = None
        self.funding_overview_df = None

        self.uni_funding_dict = None

        self.GBP_groups = ['EPSRC', 'Industrial']
        self.EUR_groups = ['5GPPP','FIRE', 'Other EU' ]

    def total_funding(self):

        """ Takes the source labels and projFunding figures from the classifiedDF.pickle and totals them. Amounts recorded as 'EUR X' are converted using live data via python_forex. Results are stored in their own dataframe 'funding_overview_df' """

        df = self.df[['Source', 'projFunding']]

        grouped = df.groupby(by='Source')

        # EPSRC and Industrial use GBP, others use EUR
        GBP_groups = self.GBP_groups
        EUR_groups = self.EUR_groups


        funding_dict = {}

        for tg in GBP_groups:

            group = grouped.get_group(tg)
            group['projFunding'] = group['projFunding'].apply(lambda x: x if isinstance(x, int) else 0)


            funding_dict[tg] = group['projFunding'].sum()

        for tg in EUR_groups:

            group = grouped.get_group(tg)


            # please ignore these ugly transforms, thank you
            group['projFunding'] = group['projFunding'].apply(lambda x: x.replace('EUR ', ''))
            group['projFunding'] = group['projFunding'].apply(lambda x: x.replace(' ', ''))
            group['projFunding'] = group['projFunding'].apply(lambda x: x.replace(',', '.'))
            group['projFunding'] = group['projFunding'].apply(lambda x: 0 if x == '' else x)
            group['projFunding'] = group['projFunding'].apply(lambda x: float(x))
            group['projFunding'] = group['projFunding'].apply(lambda x: int(x))
            group['projFunding'] = group['projFunding'].apply(lambda x: self.c.convert('EUR', 'GBP', x))

            funding_dict[tg] = group['projFunding'].sum()


        self.funding_overview = funding_dict
        df = pd.DataFrame.from_dict(self.funding_overview, orient='index')
        df.columns = ['Funding Total (£)']
        self.funding_overview_df = df

    def funding_overview_to_excel(self):


        """ Takes the funding overview dataframe and exports it to an .xlsx format file """
        df = self.funding_overview_df
        df.to_excel('funding_overview.xlsx')

    def funding_overview_graph(self):

        """ Tales the funding overview dataframe and creates a bar chart from the data inside. """

        sourceTitles = self.funding_overview.keys()
        sourceVals = self.funding_overview.values()

        #print(instOrderVals)
        # make the bloody bar

        index = np.arange(len(sourceTitles))

        fig, ax = plt.subplots(1,1, figsize=(2,2))
        plt.bar(index,sourceVals)
        plt.xlabel('Institution',   fontsize = 18, labelpad=20)
        plt.ylabel('Money Spent', fontsize = 18, labelpad=20)
        fmt = '£{x:,.0f}'
        tick = mtick.StrMethodFormatter(fmt)
        ax.yaxis.set_major_formatter(tick)
        plt.xticks(index, sourceTitles, fontsize = 12, rotation=90)
        plt.gcf().subplots_adjust(left=0.25, bottom=0.25)
        plt.show()

    def university_funding(self):

        """ Takes the classifiedDF dataframe and extrapolates a breakdown of funding source for each institution that leads a recorded project.
        This is powered by pandas' groupby function - groups are created based on projectLead values and these groups are sub-grouped by funding source.
        Each project leader has a funding dictionary created for it and values are updated as the sub-groups are totaled. """

        df = self.df

        uni_funding_dict = {}

        grouped = df.groupby('projLead')
        group_names = grouped.groups

        for gru in group_names:

            if gru != '':
                uni_funding_dict[gru] = {'EPSRC': 0, 'Industrial': 0, '5GPPP': 0, 'FIRE': 0, 'Other EU': 0 }

                grouper = grouped.get_group(gru)
                source_group = grouper.groupby('Source')

                for s in self.GBP_groups:

                    try:
                        gruup = source_group.get_group(s)
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: x if isinstance(x, int) else 0)

                        uni_funding_dict[gru][s] = gruup['projFunding'].sum()
                    except:
                        KeyError

                for s in self.EUR_groups:

                    try:
                        gruup = source_group.get_group(s)
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: x.replace('EUR ', ''))
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: x.replace(' ', ''))
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: x.replace(',', '.'))
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: 0 if x == '' else x)
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: float(x))
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: int(x))
                        gruup['projFunding'] = gruup['projFunding'].apply(lambda x: self.c.convert('EUR', 'GBP', x))
                        uni_funding_dict[gru][s] = gruup['projFunding'].sum()
                    except:
                        KeyError
            else:
                pass


        print(uni_funding_dict)
        self.uni_funding_dict = uni_funding_dict

    def uni_funding_export(self):

        """ Exports the per university funding breakdown to a .CSV file """

        df = pd.DataFrame.from_dict(self.uni_funding_dict)
        df.to_csv('uni_funding_breakdown.csv')

    def uni_funding_bar(self):

        """ Generates a stacked bar graph using matplotlib and the funding dictionary generated by university_funding. Values are translated into a numpy array
        which is split into 5 slices (specifics to the work this was created for). """

        sourceTitles = []
        sourceVals = []

        for i, key in enumerate(self.uni_funding_dict):

            vals = list(self.uni_funding_dict[key].values())

            if any(t > 0 for t in vals):
                sourceTitles.append(key)
                sourceVals.append(vals)

        # make the bloody bar

        a = np.zeros(shape=(len(sourceTitles), 5))



        for i, li in enumerate(sourceVals):
            print(sourceTitles[i])
            print(li)
            a[i] = li

        epsrc = a[:,0]
        indust = a[:,1]
        fiveGPPP = a[:,2]
        FIRE = a[:,3]
        otherEU = a[:,4]

        print(len(epsrc),len(indust), len(sourceTitles))
        width = 0.75
        index = np.arange(len(sourceTitles))

        fig, ax = plt.subplots(1,1, figsize=(2,2))

        p1 = plt.bar(index, epsrc, width)
        p2 = plt.bar(index, indust, width, bottom=sum([epsrc]))
        p3 = plt.bar(index, fiveGPPP, width, bottom=sum([epsrc, indust]))
        p4 = plt.bar(index, FIRE, width, bottom=sum([epsrc,indust, fiveGPPP]))
        p5 = plt.bar(index, otherEU, width, bottom=sum([epsrc,indust, fiveGPPP, FIRE ]))

        plt.xlabel('Institution', fontsize = 18, labelpad=20)
        plt.ylabel('Money Invested', fontsize = 18, labelpad=20)
        fmt = '£{x:,.0f}'
        tick = mtick.StrMethodFormatter(fmt)
        ax.yaxis.set_major_formatter(tick)
        plt.xticks(index, sourceTitles, fontsize = 12, rotation=90)
        plt.gcf().subplots_adjust(left=0.25, bottom=0.35)
        plt.legend((p1[0], p2[0], p3[0],p4[0],p5[0]), ("EPSRC", "Industrial", "5GPPP", "FIRE", "Other EU"))
        plt.show()


# Example Calling
# x = map_stats()
# x.total_funding()
# # x.funding_overview_to_excel()
# # x.funding_overview_graph()
# x.university_funding()
# x.uni_funding_export()
# x.uni_funding_bar()
