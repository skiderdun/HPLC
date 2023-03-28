

import tkinter
from tkinter import filedialog
import xlrd
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class HPLC:
    def __init__(self, master):
        self.master = master
        master.title("HPLC")

        self.data = {}
        self.path = Path.cwd()
        self.path_key = self.path.stem
        self.names = []
        self.grid_frame = None

        # create a window to host buttons
        self.button_frame = tkinter.Frame(self.master)
        self.button_frame.pack()

        # create a button to import data from a file
        self.import_file = tkinter.Button(self.button_frame, text="Import File", command=self.import_file)
        self.import_file.pack(side=tkinter.LEFT)

        # save as button
        self.save_as = tkinter.Button(self.button_frame, text="Save As", command=self.save_as)
        self.save_as.pack(side=tkinter.LEFT)

        # create a button to process data
        self.process = tkinter.Button(self.button_frame, text="Process", command=self.process)
        self.process.pack(side=tkinter.LEFT)

    def process(self):
        # get the path to the directory containing the data files
        self.path = Path(tkinter.filedialog.askdirectory())
        self.path_key = self.path.stem
        if self.path.isdir():
            names = tkinter.simpledialog.askstring('Index Column Names', 'Enter the Index Column Names (comma-separated):')
            self.names = [x.strip() for x in names.split(',')] + ['#']
            self.from_hplc_files(path=self.path, names=self.names)

    def import_file(self):
        # get the path to the file containing the data
        self.path = Path(tkinter.filedialog.askopenfilename())
        if self.path.is_file():
            file_extension = self.path.suffix.lower()
            ind_cols = tkinter.simpledialog.askinteger('Index', 'Number of Index Levels?:')
            if file_extension == '.csv':
                self.new_csv(path=self.path, ind_cols=int(ind_cols))
            elif file_extension == '.xlsx' or file_extension == '.xls':
                self.new_excel(path=self.path, ind_cols=int(ind_cols))

    def new_csv(self, path, ind_cols):
        # import the csv file into a dataframe
        Data = pd.read_csv(path, index_col=list(np.arange(0,ind_cols)))
        Data = Data.astype(float)
        self.data[self.path.stem] = Data
        self.create_grid(Data)
    
    def new_excel(self, path, ind_cols):
        # import the excel file into a dataframe
        Data = pd.read_excel(path, index_col=list(np.arange(0,ind_cols)))
        Data = Data.astype(float)
        self.data[self.path.stem] = Data
        print(Data)
        self.create_grid(Data)

    def from_hplc_files(self, path, names):
        dirs = path.glob('*.xls*')
        # import all files in the directory into a single dataframe     

        values = {}
        n = 0
        for file in dirs:
                
            with xlrd.open_workbook(os.path.join(path, file), logfile=open(os.devnull, 'w')) as tempfile:
            
                temp = pd.read_excel(tempfile, index_col=0)

            columns =  list(temp.drop(columns = 'Unnamed: 1').dropna().index[1:])
            index = [x.split(' ') + [n] for x in list(set(temp['Unnamed: 1'].dropna())) if x != 'Sample_Name'][0]

            n += 1
            
            data = [float(temp.at[column,"Unnamed: 2"]) for column in columns]       
            
            index = tuple(index)

            values[index] = dict(zip(columns,data))

        Data = pd.DataFrame(values).transpose()
            
        Data = Data.fillna(0.000)

        if names[-1] != '#':
            names = names + ['#']

        Data.index.names = names

        Data.index = Data.index.map(lambda x: tuple([int(y) if isinstance(y, str) and y.isdigit() else y for y in x])
                                    if not isinstance(x, float) and not isinstance(x, int) else x)

        Data.sort_index(inplace=True)

              
        new_index = []
        for x in np.arange(Data.index.size):
            new_index.append(Data.index[x][0:-1] + (x,))
        new_index = pd.MultiIndex.from_tuples(new_index, names=Data.index.names)
        Data.index = new_index

        Data = Data.astype(float)

        self.data[self.path_key] = Data
        print(Data)
        self.create_grid(Data)
    
    def save_as(self):
        def save_data():
            self.path = Path(tkinter.filedialog.asksaveasfilename(initialdir=self.path.parent,
                                                    title='Save File',
                                                    filetypes=(('Excel Files', '*.xlsx'), ('OpenDocument', '*.ods'), ('All Files', '*.*'))))
            # if no file extension is given, add .xlsx
            if self.path.suffix == '':
                self.path = self.path.with_suffix('.xlsx')
            self.path_key = self.path.stem
            file_extension = self.path.suffix.lower()
            for key in self.checks.keys():
                if self.checks[key].get() == 1:
                            if file_extension == '.xlsx' or file_extension == '.xls':
                                with pd.ExcelWriter(str(self.path_key) + '_' + str(key) + '.xlsx') as writer:
                                    self.data[key].to_excel(writer, sheet_name=str(key))
                            elif file_extension == '.ods':
                                self.data[key].to_excel(str(self.path_key) + '_' + str(key) + '.ods', engine='odf')
                            else:
                                self.data[key].to_csv(str(self.path_key) + '_' + str(key) + '.csv')
                            
            self.save_dialog.destroy()
        
        # new window to select which data frames to save
        self.save_dialog = tkinter.Toplevel(self.master, takefocus=True, padx=10, pady=10)
        self.save_dialog.title('Save As')

        # create a button to save the selected data frames
        self.save_button = tkinter.Button(self.save_dialog, text="Save", command=save_data)
        self.save_button.pack(side=tkinter.BOTTOM)

        # each entry in self.data has a check button and is labeled with the name of the data frame
        self.checks = {}
        for key in self.data.keys():
            self.checks[key] = tkinter.IntVar()
            tkinter.Checkbutton(self.save_dialog, text=key, variable=self.checks[key]).pack(side=tkinter.TOP)

    def create_grid(self, data=None):
        #  display the data in a excel like grid in a new TopLevel window
        self.grid = tkinter.Toplevel(self.master, takefocus=True, padx=10, pady=10)
        self.grid.title(self.path_key)

        # Create a canvas to contain the grid frame and scrollbar
        canvas = tkinter.Canvas(self.grid, borderwidth=0, highlightthickness=0)
        
        # create scroll bars
        hbar = tkinter.Scrollbar(self.grid, orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        hbar.config(command=canvas.xview)
        vbar = tkinter.Scrollbar(self.grid, orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        vbar.config(command=canvas.yview)

        # bind vertical scroll bar to mouse wheel
        self.grid.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # bind horizontal scroll bar to shift mouse wheel
        self.grid.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1*(event.delta/120)), "units"))

        # bind vertical scroll bar to page up and page down keys
        self.grid.bind_all("<Prior>", lambda event: canvas.yview_scroll(-1, "pages"))
        self.grid.bind_all("<Next>", lambda event: canvas.yview_scroll(1, "pages"))

        # bind horizontal scroll bar to shift page up and shift page down keys
        self.grid.bind_all("<Shift-Prior>", lambda event: canvas.xview_scroll(-1, "pages"))
        self.grid.bind_all("<Shift-Next>", lambda event: canvas.xview_scroll(1, "pages"))

        # Create a frame to hold the grid entries
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        self.grid_frame = tkinter.Frame(canvas)
        canvas.create_window((0, 0), window=self.grid_frame, anchor=tkinter.NW)

        # Create labels for the index columns
        for col, name in enumerate(data.index.names):
            label = tkinter.Label(self.grid_frame, text=name, font=('Arial', 12, 'bold'))
            label.grid(row=0, column=col)
        
        # Create a Tkinter Label for each index value in the multiindex and align under the respective column header
        for row, index in enumerate(data.index):
            for col, name in enumerate(data.index.names):
                entry = tkinter.Label(self.grid_frame, text=index[col], font=('Arial', 12))
                entry.grid(row=row+1, column=col)

        # Create a Tkinter Label for the column headers
        for col, header in enumerate(data.columns):
            label = tkinter.Label(self.grid_frame, text=header, font=('Arial', 12, 'bold'))
            label.grid(row=0, column=col+len(data.index.names))
                
        # Create a Tkinter Entry widget for each cell in the grid
        self.entries = {}
        for row, index in enumerate(data.index):
            for col, column in enumerate(data.columns):
                entry_var = tkinter.StringVar(value=data.at[index, column])
                entry = tkinter.Entry(self.grid_frame, textvariable=entry_var, font=('Arial', 12))
                entry.grid(row=row+1, column=col+len(data.index.names))
                self.entries[(row, col)] = entry_var

        # Update the canvas scroll region after the grid frame is created
        self.grid_frame.update_idletasks()

        # configure the canvas
        canvas.config(yscrollcommand=vbar.set)
        canvas.config(xscrollcommand=hbar.set)
        canvas.config(scrollregion=canvas.bbox("all"))



def main():
    run = HPLC(master=tkinter.Tk())
    run.master.mainloop()

if __name__ == '__main__':
    main()