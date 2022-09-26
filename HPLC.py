import pandas as pd
import numpy as np
import os

def create(path):
    Data = pd.DataFrame()
    try: 
        dirs = os.listdir(path)
    except Exception:
        print("That path isn't real\nfrigin noob\n")
        continue
    else:
        for file in dirs:
            Data = pd.concat([Data, pd.read_excel(f"{path}/{file}")])
        Data.index = Data['Unnamed: 0']
        Data.index.name = 'Compound'
        Data.dropna(how = 'all', inplace =True)
        Data.drop(columns = "Unnamed: 0", inplace = True)
        Data.drop(index = 'Name', inplace = True)
        Data.reset_index(inplace = True)
        Data["Unnamed: 1"].fillna(method = 'ffill', inplace = True)
        Data.sort_index(inplace = True)
        Data.index = Data.Compound
        Data.drop("Sample_Name" , inplace = True)
        Data.drop("Compound" , axis = 1, inplace = True)
        Data.index = pd.MultiIndex.from_tuples(list(zip(Data.index.to_list(), Data["Unnamed: 1"].to_list())))
        Data.drop("Unnamed: 1", axis = 1, inplace = True)
        Data.sort_index(inplace = True)
    
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
    return 'Good to go!'

def repl(df):
    df = df 
    while True :
        inp = input("REPL >> ")
        print(eval(inp))
        if inp == quit:
            break

def SwitchKey(inp, df):
    df = df
    switch={
            'new' : lambda x : create(x),
            'format' : lambda : ind_col(df),
            'write' : lambda x : writeOut(x, df),
            'test' : lambda x : x,
            'REPL' : lambda x : repl(x),
            'quit' : lambda : quit()
            }
    return switch.get(inp)

def main():
    df = pd.DataFrame()
    print(f'new : path to hplc files -> raw frame\nformat : raw frame -> frame with formated index and column\nwrite : file name -> excel file')
    while True:
        inp = input('\n--> ').split()
        try: 
            if len(inp) == 2:
                SwitchKey(inp[0], df)(inp[1])
            else:
                SwitchKey(inp[0], df)()

        except TypeError:
            continue
        else:

            if len(inp) == 2:
                df = SwitchKey(inp[0], df)(inp[1])
                print(df)
            else:
                df = SwitchKey(inp[0], df)()
                print(df)

if __name__ == "__main__":
    main()
