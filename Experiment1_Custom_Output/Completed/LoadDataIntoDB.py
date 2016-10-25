import os
import pyodbc
import logging

def get_num_lines(filename):
    count = -1
    with open(filename,"r") as file:
        for line in file:
            count += 1
    return count

def isfloat(x):
    try:
        a = float(x)
    except ValueError:
        return False
    else:
        return True

def isint(x):
    try:
        a = float(x)
        b = int(a)
    except ValueError:
        return False
    else:
        return a == b

if __name__=='__main__':
    logging.basicConfig(filename="LoadingLog.log",level=logging.INFO)
    logging.info("STARTING")
    dir = os.path.dirname(os.path.realpath(__file__)) #r'D:\\Completed'
    cnxn = pyodbc.connect(r'Driver={SQL Server};Server=.\SQLEXPRESS;Database=ExperimentData;Trusted_Connection=yes;')
    cursor = cnxn.cursor()
    currFilename = "NADA"
    try:
        for filename in os.listdir(dir):
            currFilename = filename
            if 'Iterative.csv' in filename:
                file = open(os.path.join(dir,filename))
                first = True
                rows = []
                for line in file:
                    if not first:
                        l = line.split(',')
                        r = [filename]
                        for d in l:
                            val = d
                            if isfloat(d):
                                val = float(d)
                            if isint(d):
                                val = int(val)
                            if d == 'None' or d == 'nan':
                                val = None
                            if d == 'True':
                                val = 1
                            if d == 'False':
                                val = 0
                            r.append(val)
                        if len(r) == 5:
                            r.append(None)
                        r.append(1)
                        rows.append(r)
                    first = False
                sql = "INSERT INTO [dbo].[Iterative_Data] VALUES ( ?, ?, ?, ?, ?, ?, ?)"

                cursor.executemany(sql,rows)
                cursor.commit()

                logging.info(filename+" FINISHED")
            if "Merge.csv" in filename:
                print filename
                numLines = float(get_num_lines(os.path.join(dir,filename)))
                file = open(os.path.join(dir,filename))
                first = True
                rows = []
                i = 0
                count = 0
                for line in file:
                    if not first:
                        l = line.split(',')
                        r = [filename]
                        for d in l:
                            val = d
                            if isfloat(d):
                                val = float(d)
                            if isint(d):
                                val = int(val)
                            if d == 'None' or d == 'nan':
                                val = None
                            if d == 'True':
                                val = 1
                            if d == 'False':
                                val = 0
                            r.append(val)

                        i += 1
                        count += 1
                        ##if r[len(r) - 2] == 0:
                        ##    continue
                        rows.append(r)
                        if count >= 40000:
                            count = 0
                            print float(i)/ numLines
                            sql = "INSERT INTO [dbo].[Merge_Data] VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"

                            cursor.executemany(sql,rows)
                            cursor.commit()
                            rows = []
                    first = False
                if len(rows) > 0:
                    sql = "INSERT INTO [dbo].[Merge_Data] VALUES ( ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
                    cursor.executemany(sql,rows)
                    cursor.commit()
                logging.info(filename+" FINISHED")
    except Exception as e:
        print e
        logging.info(currFilename+" DID NOT FINISH")
    cnxn.close()