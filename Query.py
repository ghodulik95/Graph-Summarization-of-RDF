import pyodbc as odbc
import time
import numpy
import random

class AbstractQueryer(object):
    def __init__(self, dbname):
        self.dbname = dbname
        self.cnxn = odbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=' + dbname + r';Trusted_Connection=yes;')

    def connection_query(self, start, end, num_hops=1):
        if num_hops == 0:
            return start == end

        start_time = time.time()
        hops = 0
        visited = set()
        next = set()
        curr = {start}
        num_neighbors = {}
        prev = {}
        while hops < num_hops:
            while len(curr) > 0:
                c = curr.pop()
                visited.add(c)
                neighbors = self.get_neighbors(c)
                num_neighbors[c] = len(neighbors)
                for n in neighbors:
                    if n == end:
                        prev[n] = c
                        num_neighbors[n] = "N/A"
                        return self.get_output(start,end,prev,num_neighbors,start_time)
                    if n not in visited:
                        next.add(n)
                        prev[n] = c
            curr = next
            next = set()
            hops += 1
        return False

    def get_macro_headers(self):
        return "start,end,Path, Runtime, min_degree, max_degree, avg_degree, median_degree, degree_deviation,path_length"

    def get_output(self,start,end,prev,num_neighbors,start_time):
        end_time = time.time()
        elapsed_time = end_time - start_time
        curr = end
        num_neighbors_on_path = []
        s = "%s, %s, " % (start,end)
        while 1:
            s += "%s (%s) <- " % (curr, str(num_neighbors[curr]))
            if num_neighbors[curr] != "N/A":
                num_neighbors_on_path.append(num_neighbors[curr])
            if curr == start:
                break

            curr = prev[curr]
        s += ", %s, %s, %s, %s, %s, %s,%s" % (str(elapsed_time),
                                         str(min(num_neighbors_on_path)),
                                         str(max(num_neighbors_on_path)),
                                         str(float(sum(num_neighbors_on_path))/ len(num_neighbors_on_path)),
                                         str(numpy.median(num_neighbors_on_path)),
                                         str(numpy.std(num_neighbors_on_path)),
                                              str(len(num_neighbors_on_path)))
        return s


    def get_neighbors(self,c):
        raise NotImplementedError()

    def close_connection(self):
        self.cnxn.close()

class SummaryQueryer(AbstractQueryer):
    def __init__(self, dbname, summary):
        self.summary = summary
        self.trial_num=0
        AbstractQueryer.__init__(self,dbname)

    def connection_query(self, start, end, num_hops=1):
        self.trial_num += 1
        return AbstractQueryer.connection_query(self,start,end,num_hops)

    def get_neighbors(self, uri):
        cursor = self.cnxn.cursor()
        q = "Exec [dbo].[GetNeighbors] @uri = '%s', @table = '%s'" % (uri, self.summary)
        cursor.execute(q)
        neighbors = set()
        while 1:
            n = cursor.fetchone()
            if not n:
                break
            neighbors.add(n.Subject)

        return neighbors

    def get_macro_headers(self):
        return "Trial Num, start,end, Path, Runtime, min_degree, max_degree, avg_degree, median_degree, degree_deviation, min_num_corrections, max_num_corrections, avg_num_corrections, path_length"

    def get_micro_headers(self):
        return "Node, degree, num_additions, num_subtractions, num_corrections"

    def get_output(self,start,end,prev,num_neighbors,start_time):
        end_time = time.time()
        elapsed_time = end_time - start_time
        curr = end
        num_neighbors_on_path = []
        num_additions_on_path = []
        num_subtractions_on_path = []
        m = ""
        s = "%s, %s, %s, " % (str(self.trial_num),start,end)
        while 1:
            s += "%s (%s) <- " % (curr, str(num_neighbors[curr]))
            m += curr
            if num_neighbors[curr] != "N/A":
                num_neighbors_on_path.append(num_neighbors[curr])
                num_add = self.get_num_additions(curr)
                num_sub = self.get_num_subtractions(curr)
                num_additions_on_path.append(num_add)
                num_subtractions_on_path.append(num_sub)
                m += ", %d, %d, %d, %d\n" % (num_neighbors[curr], num_add, num_sub, num_add + num_sub)
            else:
                m+= ","+str(elapsed_time)+",,,\n"

            if curr == start:
                break

            curr = prev[curr]

        num_corrections = [num_additions_on_path[i] + num_subtractions_on_path[i] for i in range(len(num_additions_on_path))]
        s += ", %s, %s, %s, %s, %s, %s, %s, %s, %s, %s" % (str(elapsed_time),
                                                         str(min(num_neighbors_on_path)),
                                                         str(max(num_neighbors_on_path)),
                                                         str(float(sum(num_neighbors_on_path))/ len(num_neighbors_on_path)),
                                                         str(numpy.median(num_neighbors_on_path)),
                                                         str(numpy.std(num_neighbors_on_path)),
                                                       str(min(num_corrections)),
                                                       str(max(num_corrections)),
                                                       str(float(sum(num_additions_on_path))/ len(num_corrections)),
                                                           str(len(num_corrections)))
        return s,m

    def get_corrections_table_name(self):
        name = "SummaryCorrections_"+self.summary+self.dbname
        if self.summary == 'Altered':
            name += "_50_100_1"
        return name

    def get_num_additions(self,c):
        c_table = self.get_corrections_table_name()
        q = "SELECT COUNT(*) AS c FROM [dbo].[%s] WHERE posOrNeg = '+' AND ([Subject] = '%s' OR [Object] = '%s')" %(c_table,c,c)
        cursor = self.cnxn.cursor()
        cursor.execute(q)
        r = cursor.fetchone()
        return r.c

    def get_num_subtractions(self,c):
        c_table = self.get_corrections_table_name()
        q = "SELECT COUNT(*) AS c FROM [dbo].[%s] WHERE posOrNeg = '-' AND ([Subject] = '%s' OR [Object] = '%s')" %(c_table,c,c)
        cursor = self.cnxn.cursor()
        cursor.execute(q)
        r = cursor.fetchone()
        return r.c

class BreadthQueryer(AbstractQueryer):

    def get_random_neighborhood(self,uri,num_hops=1):
        if num_hops == 0:
            return set()
        hops = 0
        visited = set()
        next = set()
        curr = {uri}
        while hops < num_hops:
            if len(curr) > 20:
                curr = random.sample(curr,20)
            while len(curr) > 0:
                c = curr.pop()
                visited.add(c)
                neighbors = self.get_neighbors(c)
                for n in neighbors:
                    if n not in visited:
                        next.add(n)
            curr = next
            next = set()
            hops += 1
        return curr

    def get_neighbors(self, uri):
        cursor = self.cnxn.cursor()
        q = "( SELECT [Subject] FROM [dbo].[Summarized_RDF] WHERE [Object] = '%s' ) UNION (SELECT [Object] FROM [dbo].[Summarized_RDF] WHERE [Subject] = '%s')" % (uri, uri)
        cursor.execute(q)
        neighbors = set()
        while 1:
            n = cursor.fetchone()
            if not n:
                break
            neighbors.add(n.Subject)

        return neighbors

    def get_all_nodes(self):
        cursor = self.cnxn.cursor()
        q = "SELECT DISTINCT s.o AS n FROM ( (SELECT [Subject] AS o FROM [dbo].[Summarized_RDF]) UNION (SELECT [Object] AS o FROM [dbo].[Summarized_RDF])) s"
        cursor.execute(q)
        nodes = set()
        while 1:
            n = cursor.fetchone()
            if not n:
                break
            nodes.add(n.n)
        return nodes

class MergeQueryer(AbstractQueryer):

    def connection_query(self, start, end, num_hops=1):
        if num_hops == 0:
            return start == end
        tableNames = ["s"+str(i) for i in range(num_hops)]
        q = "SELECT TOP 1 * FROM " + ' , '.join(map(lambda x: " [dbo].[Summarized_RDF]"+x, tableNames))
        raise NotImplementedError()


if __name__ == "__main__":
    q = SummaryQueryer("DBLP4", "Pure")
    print q.connection_query('<http://dblp.rkbexplorer.com/id/journal-50517d5257aaced071536999c8711091>',
                             '<http://dblp.rkbexplorer.com/id/people-5c46a99b51de5a17d24325f842c5271a-1655e90b53e68f5d2130f3cd9548fee9>',2)
    print q.connection_query('<http://dblp.rkbexplorer.com/id/journal-50517d5257aaced071536999c8711091>',
                             '<http://dblp.rkbexplorer.com/id/people-5c46a99b51de5a17d24325f842c5271a-1655e90b53e68f5d2130f3cd9548fee9>',
                             1)
    q.close_connection()
    q = BreadthQueryer("DBLP4")
    print q.connection_query('<http://dblp.rkbexplorer.com/id/journal-50517d5257aaced071536999c8711091>',
                             '<http://dblp.rkbexplorer.com/id/people-5c46a99b51de5a17d24325f842c5271a-1655e90b53e68f5d2130f3cd9548fee9>',
                             2)
    print q.connection_query('<http://dblp.rkbexplorer.com/id/journal-50517d5257aaced071536999c8711091>',
                             '<http://dblp.rkbexplorer.com/id/people-5c46a99b51de5a17d24325f842c5271a-1655e90b53e68f5d2130f3cd9548fee9>',
                             1)
    q.close_connection()
