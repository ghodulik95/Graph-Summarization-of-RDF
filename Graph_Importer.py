#Graph Importer module
import pyodbc as odbc
import igraph as ig

def get_label(name):
    if "movie" in name:
        return "m"
    if "person" in name:
        return "p"
    if "company" in name:
        return "c"
    return name

def import_graph_regular(dbname, cutoff=50, year_s=1990, year_e=1992,include_real_name=True,fulldb=False, get_remaining=False):
    cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=' + dbname + r';Trusted_Connection=yes;')
    # cnxn.autoCommit = True
    cursor = cnxn.cursor()
    if dbname == "DBLP4" and not fulldb:
        year_start = year_s
        year_end = year_e
        lim_num_docs = cutoff
        params = (year_start, year_end, lim_num_docs)
        q = "Exec Rows_From_Year_Range @year_start = %d, @year_end = %d, @lim_num_docs = %d" % params
        cursor.execute(q)
    elif get_remaining:
        print """SELECT [Subject],[Object] FROM [%s].[dbo].[RDF] WHERE [Subject] IN ( SELECT [Original_name] FROM [%s].[dbo].[SummaryONAME2SNODE_Pure%s] )
                           AND [Object] IN ( SELECT [Original_name] FROM [%s].[dbo].[SummaryONAME2SNODE_Pure%s] ) """ % (dbname, dbname, dbname, dbname, dbname)
        cursor.execute("""SELECT [Subject],[Object] FROM [%s].[dbo].[RDF] WHERE [Subject] IN ( SELECT [Original_name] FROM [%s].[dbo].[SummaryONAME2SNODE_Pure%s] )
                           AND [Object] IN ( SELECT [Original_name] FROM [%s].[dbo].[SummaryONAME2SNODE_Pure%s] ) """ % (dbname, dbname, dbname, dbname, dbname))
    else:
        cursor.execute(
            """SELECT * FROM RDF WHERE [Object] NOT LIKE '%"%' AND [Object] NOT LIKE '%#%' AND [Object] LIKE '%<%' AND [Predicate] NOT LIKE '%#type%'
                AND [Object] LIKE '%[^0-9]%' AND [Subject] NOT LIKE '%"%' AND [Subject] LIKE '%[^0-9]%' AND [Object] NOT LIKE '%Disease_Annotation>%'
            """)

    node_name_to_id = {}
    id_to_node_name = {}
    edges = set()
    max_node_id = -1
    count = 0
    while 1:
        row = cursor.fetchone()
        if not row:
            break
        subject_name = row.Subject
        predicate_name = None
        if not get_remaining:
            predicate_name = row.Predicate
        object_name = row.Object

        # print subject_name+" "+predicate_name+" "+object_name
        if can_skip(subject_name, predicate_name, object_name):
            continue

        if not node_name_to_id.has_key(subject_name):
            max_node_id += 1
            node_name_to_id[subject_name] = max_node_id
            id_to_node_name[max_node_id] = subject_name
        if not node_name_to_id.has_key(object_name):
            max_node_id += 1
            node_name_to_id[object_name] = max_node_id
            id_to_node_name[max_node_id] = object_name
        edges.add((node_name_to_id[subject_name], node_name_to_id[object_name]))
        count += 1
        if dbname != "DBLP4" and count >= cutoff and not fulldb:
            break

    cnxn.close()

    g = ig.Graph(directed=False)
    g.add_vertices(max_node_id + 1)
    if include_real_name:
        g.vs["name"] = [str(id_to_node_name[id]) for id in range(max_node_id + 1)]
        g.vs["label"] = [get_label(id_to_node_name[id])+str(id) for id in range(max_node_id + 1)]
        #print g.vs["name"]
    g.add_edges(edges)

    return g, id_to_node_name, node_name_to_id

def can_skip(s,p,o):
    if o[0] == '"':
        return True
    if s == o:
        return True
    return False