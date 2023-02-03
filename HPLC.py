import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

import pandas as pd
import numpy as np
import os
import sys
import xlrd

def log(reg):
    if "table.txt" not in os.listdir():
        open("table.txt", "w").close()
    elif type(reg) == pd.core.frame.DataFrame:
        df = reg
        try:
            df.to_csv('table.txt')
        except Exception:
            df = pd.DataFrame.to_csv('table.txt')
    else:
        with open('log.txt', 'a') as file:
            print(reg, file)
    return pd.read_csv('table.txt', index_col = [0,1])

def create(path):
    path = path.replace("\\",'/').replace('\'','').replace('\"','')
    try: 
        dirs = os.listdir(path)
    except Exception:
        return "That path isn't real\nfrigin noob\n"
    else:
        values = {}
        n = 0

        for file in dirs:
            
            tempfile = xlrd.open_workbook(f"{path}/{file}", logfile=open(os.devnull, 'w'))
            
            temp = pd.read_excel(tempfile, index_col = 0)
                        
            columns =  list(temp.drop(columns = 'Unnamed: 1').dropna().index[1:])
            index = [x for x in list(set(temp['Unnamed: 1'].dropna())) if x != 'Sample_Name'][0]
            data = [temp.at[column,"Unnamed: 2"] for column in columns]
            n += 1
            
            values[index,n] = dict(zip(columns,data))
           
        Data = pd.DataFrame(values).transpose()
        Data = Data.fillna(0.000)

     
    return Data

def ind_col(frame):
    new_cols = list(set([x[0] for x in frame.index.to_list()]))

    ind_len = int(0)
    for col in new_cols:
        length = frame.loc[col].size
        if length > ind_len:
            ind_len = int(length) 

    new_ind = pd.MultiIndex.from_tuples([tuple(y.split()) for y in list([x[1] for x in frame.index.to_list()])[0:ind_len]])

    tempframe = pd.DataFrame(columns = new_cols,index = new_ind)


    for col in new_cols:
        for i in enumerate(frame.loc[col].values.astype(float).tolist()):
            tempframe[col].iloc[i[0]] = i[1][0]

    return tempframe

def writeOut(name, df):
    if name[-5:] != ".xlsx":
        name = name + '.xlsx'
    with pd.ExcelWriter(name) as writer:
        df.to_excel(writer, sheet_name = "Data") 
    return 'Good to go!\n'

def getOld(path, df):
    path = path.replace("\\",'/').replace('\'','').replace('\"','')
    df = df
    if path[-5:] != ".xlsx":
        path = path + '.xlsx'
    try:
        df = pd.read_excel(path, index_col = [0,1], dtype = object)
    except Exception:
        return "Check your spelling on that path"
        
    else:
        return df

def SwitchKey(inp, df):
    df = df
    switch={
            'new' : lambda x : create(x),
            'format' : lambda : ind_col(df),
            'write' : lambda x : writeOut(x, df),
            'old' : lambda x : getOld(x, df),
            'test' : lambda x : x,
            'quit' : lambda : sys.exit()
            }
    return switch.get(inp)

def Parse():
    inp = input('\n--> ').split()
    reg = () 
    df = log(reg)
    while True:
        try:
            SwitchKey(inp[0], df)(inp[1:])
        except:
            return "WAT!?"
def main():
    reg = () 
    df = log(reg)
    print(f'new : path to hplc files -> raw frame\nformat : -> frame with formated index and column\nwrite : file name -> excel file\nold : file name -> old data frame\ndf -> database name')
    while True:
        inp = input('\n--> ').split()
        try:
            if len(inp) == 2:
                SwitchKey(inp[0], df)(inp[1])
            else:
                SwitchKey(inp[0], df)()
        except TypeError:
            try:
                print(eval(' '.join(inp)))
            except Exception:
                print('didn\'t catch that')
                continue
        else:
            if len(inp) == 2:
                reg = SwitchKey(inp[0], df)(inp[1])
                df = log(reg)
                print(df)
            else:
                reg = SwitchKey(inp[0], df)()
                df = log(reg)
                print(df)

if __name__ == "__main__":
    main()
