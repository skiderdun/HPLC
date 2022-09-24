import pandas as pd
import numpy as np
import os

def create(path):
    Data = pd.DataFrame()
    dirs = os.listdir(path)
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
    new_ind = list(set([x[1] for x in frame.index.to_list()]))
    new_cols = list(set([x[0] for x in frame.index.to_list()]))
    tempframe = pd.DataFrame(columns = new_cols,index = new_ind)
    for i in frame.iterrows():
        val = i[1].values.astype(float)[0]
        if tempframe.at[i[0][1],i[0][0]] == val:
            tempframe.at[i[0][1],i[0][0]] = (val + tempframe.at[i[0][1],i[0][0]])/2
        else:
            tempframe.at[i[0][1],i[0][0]] = val

    return tempframe

def repl(hold):
    hold = hold
    while True :
        inp = input("REPL >> ")
        print(eval(inp))
                if inp == quit:
            break

def SwitchKey(inp):
    switch={
            'new' : lambda x : create(x),
            'format' : lambda x : ind_col(x),
            'test' : lambda x : x,
            'REPL' : lambda x : repl(x),
            'quit' : lambda x : quit()
            }
    return switch.get(inp)

def main():
    print(f'new : path to hplc files -> raw frame\nformat : raw frame -> frame with formated index and column\nc')
    while True:
        inp = input('\n--> ').split()
        try:
            callable(SwitchKey(inp[0]))
        except Exception:
            print("WRONG\ntry again dumbass")
            pass
        finally:

            if len(inp) == 2:
                df = SwitchKey(inp[0])(inp[1])
                print(df)
            else:
                df = SwitchKey(inp[0])(df)
                print(df)

if __name__ == "__main__":
    main()
