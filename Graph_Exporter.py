from Graph_Summary import Abstract_Graph_Summary
import pyodbc as odbc


def export_summary(summary,dbname,appendage):
    """
    :type summary: Abstract_Graph_Summary
    :param summary:
    :param dbname:
    :param appendage:
    :return:
    """

    cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=DBLP4;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    summary_tables_cmd = "Exec [dbo].Restart_Summary @dbname = N'"+dbname+"', @appendage = N'"+appendage+"';"

    cursor.execute(summary_tables_cmd)
    cursor.commit()
    #print "There was an error making the summary tables!"

    cnxn.close()

    summary_edges_sql = "INSERT INTO [dbo].SummaryRDF_"+appendage+" VALUES (?,?)"
    edges = []
    for e in summary.s.es:
        if not e['to_be_removed']:
            s = summary.s.vs[e.source]['name']
            t = summary.s.vs[e.target]['name']
            edges.append((s,t))
    cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database='+dbname+';Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    cursor.executemany(summary_edges_sql,edges)

    mappings_sql = "INSERT INTO [dbo].SummaryONAME2SNODE_"+appendage+" VALUES (?,?)"
    mappings = []
    for i in range(0,summary.g.vcount()):
        o_uri = summary.oid_to_uri[i]
        snode = summary.oid_to_sname[i]
        mappings.append((o_uri,snode))
    cursor.executemany(mappings_sql,mappings)

    corrections_sql = "INSERT INTO [dbo].SummaryCorrections_"+appendage+" VALUES (?,?,?)"
    corrections = []
    for addition_l in summary.additions.keys():
        for addition_r in summary.additions[addition_l]:
            o_uri_l = summary.oid_to_uri[addition_l]
            o_uri_r = summary.oid_to_uri[addition_r]
            corrections.append(('+',o_uri_l,o_uri_r))
    for subtraction_l in summary.subtractions.keys():
        for subtraction_r in summary.subtractions[subtraction_l]:
            o_uri_l = summary.oid_to_uri[subtraction_l]
            o_uri_r = summary.oid_to_uri[subtraction_r]
            corrections.append(('-',o_uri_l,o_uri_r))
    cursor.executemany(corrections_sql,corrections)
    cursor.commit()
    cnxn.close()
