def Hierarchy():


    import pandas as pd
    import numpy as np
    import pprint as pp
    import locale
    import matplotlib.pyplot as plt
    import matplotlib.ticker as tkr
    import graph_tool.all as gt
    import math
    # Need to drag this out into the real world
    from kostas import findEdges, stupidTextWorkaround



    t = gt.Graph(directed = True)

    tprop_label = t.new_vertex_property("string")
    tprop_instType = t.new_vertex_property("string")

    linkDict, instSet = findEdges()

    # ingest our university checking lists [this is sloppy, TBI]

    foreignUniTxt = open('Workaround txts/Foreign Unis.txt','r')
    UKUniTxt = open('Workaround txts/UK Unis.txt','r')

    forerignUniVals = foreignUniTxt.read().splitlines()
    UKUniVals = UKUniTxt.read().splitlines()

    # add vertices and label them based on their names.

    ######## FILTERING BASED ON CORDIS RESIDENCY ##########

    dfCordisNames = pd.read_pickle('Pickles/CORDIS_Countries.pickle')

    eligiblenames = dfCordisNames.name.values.tolist()

    veryDirtyWorkaround = ['FOCUS','FLUOR', 'GE', 'NI', 'OTE', 'ROKE', 'LONDON',]
    for inst in instSet:

        nameCheck = stupidTextWorkaround(inst)
        nameCheck = nameCheck.upper()
       # print(nameCheck)
        firstFound = next((x for x in eligiblenames if nameCheck in x), None)
        #print(firstFound)
        if inst in forerignUniVals:
            del(linkDict[inst])
        elif firstFound is None:
            del(linkDict[inst])
        elif nameCheck in veryDirtyWorkaround:
            del(linkDict[inst])
        else:
            vert = t.add_vertex()
            tprop_label[vert] = str(inst)

    del(linkDict[''])

    # internalise property map
    t.vertex_properties["label"] = tprop_label

    # explicitly declare the hierarchy defining vertices and edges, the sequencing here matters.
    for_uni = t.add_vertex()
    UK_uni = t.add_vertex()
    other = t.add_vertex()
    root = t.add_vertex()

    edgeList = [(root, for_uni),(root,UK_uni),(root,other)]
    t.add_edge_list(edgeList)



    # use label name to add edges to hierarchy
    for i in range(t.num_vertices())[:-4]:
        if tprop_label[i] in forerignUniVals:
            t.add_edge(for_uni, t.vertex(i))
            tprop_instType[i] = "Foreign Uni"
        elif tprop_label[i] in UKUniVals:
            t.add_edge(UK_uni, t.vertex(i))
            tprop_instType[i] = "UK Uni"
        else:
            t.add_edge(other, t.vertex(i))
            tprop_instType[i] = "Other Institution"



    t.vertex_properties["instType"] = tprop_instType
    tpos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() -1), rel_order_leaf = True)


    ######### MAIN GRAPH DRAWING ################

    g = gt.Graph(directed = False)
    # creates graph g, using the same nodes (with the same index!)

    for v in t.vertices():
        gv = g.add_vertex()

    # we remove: root, for_uni, uk_uni or 'other' vertices

    lower = g.num_vertices() - 5
    current = g.num_vertices() - 1

    while current > lower:
        g.remove_vertex(current)
        current -= 1

    # Pull vertex properties from t

    labelDict = t.vertex_properties["label"]
    instTypeDict = t.vertex_properties["instType"]

    # create properties for g vertices

    gprop_label = g.new_vertex_property("string")
    gprop_instType = g.new_vertex_property("string")

    # match labels between g and t

    for v in g.vertices():
        gprop_label[v] = labelDict[v]
        gprop_instType[v] =  instTypeDict[v]

    # make property map internal to graph g
    g.vertex_properties["label"] = gprop_label
    g.vertex_properties["instType"] = gprop_instType

    ###### COLOUR VERTICES #########

    # Reclaim variable names because lazy

    gprop_vcolour = g.new_vertex_property("string")

    for v in g.vertices():

        if gprop_instType[v] == "Foreign Uni":
            gprop_vcolour[v] = "red"
        elif gprop_instType[v] == "UK Uni":
            gprop_vcolour[v] = "blue"
        else:
            gprop_vcolour[v] = "white"

    g.vertex_properties["vcolour"] = gprop_vcolour

    # create numLinks edge property for g edges

    eprop_numLinks = g.new_edge_property("int")

    # creates the edges between nodes

    for i in linkDict:
        for n in linkDict[i]:
            #print(i)
            vertex_i = gt.find_vertex(g, gprop_label, i)[0]
            #print(n)
            try:
                vertex_n = gt.find_vertex(g, gprop_label, n)[0]
                e = g.add_edge(vertex_i,vertex_n)
                eprop_numLinks[e] = linkDict[i][n]
            except:
                IndexError

    ###### EXPERIMENTAL SIZE THINGS ######

    gvprop_size = g.new_vertex_property('float')

    deleteList = []

    for v in g.vertices():

        # sum the num edges and the number of links they correspond to
        # use this to find a ratio and scale size off of this.

        numEdges = sum(1 for _ in v.all_edges())
        numLinks = 0

        for e in v.all_edges():

            numLinks += eprop_numLinks[e]

        print(gprop_label[v])
        print ("NumEdges = " + str(numEdges) + " NumLinks = " + str(numLinks))
        # create a delete list


        try:
            ratio = (numLinks / numEdges)
            # gvprop_size[v] = ratio
        except:
            ZeroDivisionError
            NameError
            deleteList.append(v)


    # gvprop_size = gt.prop_to_size(gvprop_size)
    # g.vertex_properties["vsize"] = gvprop_size
    #### Delete linkless vertices #######

    for v in reversed(sorted(deleteList)):
        g.remove_vertex(v)

    for v in reversed(sorted(deleteList)):
        t.remove_vertex(v)

    tpos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() -1), rel_order_leaf = True)

    #######

    #g.vertex_properties['size'] = gvprop_size

    # in order to make sure labels fit in the image we have to manually adjust the
    # co-ordinates of each vertex.

    x, y = gt.ungroup_vector_property(tpos, [0, 1])
    x.a = (x.a - x.a.min()) / (x.a.max() - x.a.min()) * 1400 + 400
    y.a = (y.a - y.a.min()) / (y.a.max() - y.a.min()) * 1400 + 400
    tpos = gt.group_vector_property([x, y])

    # This draws the 'Bezier spline control points' for edges
    # it draws the edges directed in graph g, but uses the hierarchy / positioning of graph t.
    cts = gt.get_hierarchy_control_points(g, t, tpos)


    pos = g.own_property(tpos)

    ###### Create interactive window #####
    gt.graph_draw(g,
                  vertex_text_position="centered",
                  vertex_text=g.vertex_properties["label"],
                  vertex_font_size=14,
                  vertex_anchor=0,
                  vertex_aspect=1,
                  vertex_shape = "square",
                  vertex_fill_color = g.vertex_properties["vcolour"],
                  vertex_size = 10,
                  fit_view = False,
                 # edge_color=g.edge_properties["colour"],
                  # edge_pen_width=g.edge_properties["thickness"],
                  edge_end_marker="none",
                  edge_pen_width=0.2,
                  edge_color="white",
                  bg_color=[0,0,0,1],
                  output_size=[2000,2000],
                  output='DIRTY_TESTS.png',
                  pos=pos,
                  edge_control_points=cts)

    g.save("test_graph_export.gml", fmt='graphml')

def Stochastic():

    import pandas as pd
    import numpy as np
    import pprint as pp
    import locale
    import matplotlib.pyplot as plt
    import matplotlib.ticker as tkr
    import graph_tool.all as gt
    import math

    # Need to drag this out into the real world
    from kostas import findEdges


    t = gt.Graph(directed = True)

    tprop_label = t.new_vertex_property("string")
    tprop_instType = t.new_vertex_property("string")

    linkDict, instSet = findEdges()

    # ingest our university checking lists [this is sloppy, TBI]

    foreignUniTxt = open('Workaround txts/Foreign Unis.txt','r')
    UKUniTxt = open('Workaround txts/UK Unis.txt','r')

    forerignUniVals = foreignUniTxt.read().splitlines()
    UKUniVals = UKUniTxt.read().splitlines()

    # add vertices and label them based on their names.

    ######## FILTERING BASED ON CORDIS RESIDENCY ##########

    dfCordisNames = pd.read_pickle('Pickles/CORDIS_Countries.pickle')

    eligiblenames = dfCordisNames.name.values.tolist()

    veryDirtyWorkaround = ['FOCUS','FLUOR', 'GE', 'NI', 'OTE', 'ROKE']



    for inst in instSet:

        nameCheck = inst.upper()
        firstFound = next((x for x in eligiblenames if nameCheck in x), None)
        if inst in forerignUniVals:
            del(linkDict[inst])
        elif nameCheck in veryDirtyWorkaround:
            del(linkDict[inst])
        elif firstFound is None:
            del(linkDict[inst])
        else:
            vert = t.add_vertex()
            tprop_label[vert] = str(inst)

    del(linkDict[''])

    # internalise property map
    t.vertex_properties["label"] = tprop_label

    # explicitly declare the hierarchy defining vertices and edges, the sequencing here matters.
    for_uni = t.add_vertex()
    UK_uni = t.add_vertex()
    other = t.add_vertex()
    root = t.add_vertex()

    edgeList = [(root, for_uni),(root,UK_uni),(root,other)]
    t.add_edge_list(edgeList)



    # use label name to add edges to hierarchy
    for i in range(t.num_vertices())[:-4]:
        if tprop_label[i] in forerignUniVals:
            t.add_edge(for_uni, t.vertex(i))
            tprop_instType[i] = "Foreign Uni"
        elif tprop_label[i] in UKUniVals:
            t.add_edge(UK_uni, t.vertex(i))
            tprop_instType[i] = "UK Uni"
        else:
            t.add_edge(other, t.vertex(i))
            tprop_instType[i] = "Other Institution"

    t.vertex_properties["instType"] = tprop_instType
    tpos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() -1), rel_order_leaf = True)


    ######### MAIN GRAPH DRAWING ################

    g = gt.Graph(directed = False)
    # creates graph g, using the same nodes (with the same index!)

    for v in t.vertices():
        gv = g.add_vertex()

    # we remove: root, for_uni, uk_uni or 'other' vertices

    lower = g.num_vertices() - 5
    current = g.num_vertices() - 1

    while current > lower:
        g.remove_vertex(current)
        current -= 1

    # Pull vertex properties from t

    labelDict = t.vertex_properties["label"]
    instTypeDict = t.vertex_properties["instType"]

    # create properties for g vertices

    gprop_label = g.new_vertex_property("string")
    gprop_instType = g.new_vertex_property("string")

    # match labels between g and t

    for v in g.vertices():
        gprop_label[v] = labelDict[v]
        gprop_instType[v] =  instTypeDict[v]

    # make property map internal to graph g
    g.vertex_properties["label"] = gprop_label
    g.vertex_properties["instType"] = gprop_instType

    ###### COLOUR VERTICES #########

    # Reclaim variable names because lazy

    gprop_vcolour = g.new_vertex_property("string")

    for v in g.vertices():

        if gprop_instType[v] == "Foreign Uni":
            gprop_vcolour[v] = "red"
        elif gprop_instType[v] == "UK Uni":
            gprop_vcolour[v] = "blue"
        else:
            gprop_vcolour[v] = "white"

    g.vertex_properties["vcolour"] = gprop_vcolour

    # create numLinks edge property for g edges

    eprop_numLinks = g.new_edge_property("int")

    # creates the edges between nodes

    for i in linkDict:
        for n in linkDict[i]:
            #print(i)
            vertex_i = gt.find_vertex(g, gprop_label, i)[0]
            #print(n)
            try:
                vertex_n = gt.find_vertex(g, gprop_label, n)[0]
                e = g.add_edge(vertex_i,vertex_n)
                eprop_numLinks[e] = linkDict[i][n]
            except:
                IndexError

    ##### EXPERIMENTAL SIZE THINGS ######

    #gvprop_size = g.new_vertex_property('float')

    deleteList = []

    for v in g.vertices():

        # sum the num edges and the number of links they correspond to
        # use this to find a ratio and scale size off of this.

        numEdges = sum(1 for _ in v.all_edges())
        numLinks = 0

        for e in v.all_edges():

            numLinks += eprop_numLinks[e]

        #print(gprop_label[v])
        print ("NumEdges = " + str(numEdges) + " NumLinks = " + str(numLinks))
        # create a delete list


        try:
            ratio = (numLinks / numEdges) * 5 * 2
        except:
            ZeroDivisionError
            deleteList.append(v)

        #gvprop_size[v] = ratio

    #g.vertex_properties['size'] = gvprop_size



    #### Delete linkless vertices #######

    for v in reversed(sorted(deleteList)):
        g.remove_vertex(v)

    for v in reversed(sorted(deleteList)):
        t.remove_vertex(v)

    tpos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() -1), rel_order_leaf = True)

    #######

    ############ stochastic BLOCK MODEL ####################

    state = gt.minimize_nested_blockmodel_dl(g, deg_corr=True, verbose = True)
    t = gt.get_hierarchy_tree(state)[0]
    tpos = pos = gt.radial_tree_layout(t, t.vertex(t.num_vertices() - 1), weighted=True)




    # in order to make sure labels fit in the image we have to manually adjust the
    # co-ordinates of each vertex.

    x, y = gt.ungroup_vector_property(tpos, [0, 1])
    x.a = (x.a - x.a.min()) / (x.a.max() - x.a.min()) * 1400 + 400
    y.a = (y.a - y.a.min()) / (y.a.max() - y.a.min()) * 1400 + 400
    tpos = gt.group_vector_property([x, y])

    # This draws the 'Bezier spline control points' for edges
    # it draws the edges directed in graph g, but uses the hierarchy / positioning of graph t.
    cts = gt.get_hierarchy_control_points(g, t, tpos)


    pos = g.own_property(tpos)


    gt.graph_draw(g,
                  vertex_text_position="centered",
                  vertex_text=g.vertex_properties["label"],
                  vertex_font_size=14,
                  vertex_anchor=0,
                  vertex_aspect=1,
                  vertex_shape = "square",
                  vertex_fill_color = g.vertex_properties["vcolour"],
                  vertex_size = 10,
                  fit_view = False,
                 # edge_color=g.edge_properties["colour"],
                  # edge_pen_width=g.edge_properties["thickness"],
                  edge_end_marker="none",
                  edge_pen_width=0.2,
                  edge_color="white",
                  bg_color=[0,0,0,1],
                  output_size=[2000,2000],
                  output='UK_ONLY_RELATIONSHIPS_stochastic.png',
                  pos=pos,
                  edge_control_points=cts)


    if __name__ == '__main__':
        pyjd.setup("Hello.html")

Hierarchy()
