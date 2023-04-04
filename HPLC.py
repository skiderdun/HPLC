

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
        self.checks = {}

        # create a window to host buttons
        self.button_frame = tkinter.Frame(self.master)
        self.button_frame.pack()

        # on startup, check to see if there is a data directory in project root directory
        # if there is, import all files in the directory
        # otherwise, create a data directory in the project root directory to store data files
        if Path('data').is_dir():
            for file in Path('data').glob('*.csv'):
                self.data[file.stem] = pd.read_csv(file)
                self.check(file.stem)
        else:
            Path('data').mkdir()

        # create a button to import data from a file
        self.import_file = tkinter.Button(self.button_frame, text="Import File", command=self.import_file)
        self.import_file.pack(side=tkinter.LEFT)

        # create a button to process data
        self.process = tkinter.Button(self.button_frame, text="Process", command=self.process)
        self.process.pack(side=tkinter.LEFT)

        # save as button
        self.save_as = tkinter.Button(self.button_frame, text="Save As", command=self.save_as)
        self.save_as.pack(side=tkinter.LEFT)

        # button to clear data in the data dictionary and the data directory
        self.clear = tkinter.Button(self.button_frame, text="Clear", command=self.clear)
        self.clear.pack(side=tkinter.LEFT)

        # create a button to to display the data
        self.display = tkinter.Button(self.button_frame, text="Display", command=self.display)
        self.display.pack(side=tkinter.LEFT)

        # on close of the window, save the data to the data directory
        self.master.protocol("WM_DELETE_WINDOW", self.on_closing)

    def clear(self):
        # clear checked data from the data dictionary and the data directory
        for key in self.check():
            self.data.pop(key)
            self.checks[key][1].destroy()
            self.checks.pop(key)
            Path('data').joinpath(key + '.csv').unlink()

    def on_closing(self):
        for key in self.data.keys():
            self.data[key].to_csv(Path('data').joinpath(key + '.csv'))
        self.master.destroy()

    def check(self, key = None):
        # if no key is provided, return a list of all checked keys
        if key == None:
            return [key for key in self.checks.keys() if self.checks[key][0].get() == 1 and key != 'All']
        # otherwise create a check box for the key
        else:

            self.checks[key] = [0, 0]
            self.checks[key][0] = tkinter.IntVar()
            self.checks[key][1] = tkinter.Checkbutton(self.button_frame, text=key, variable=self.checks[key][0], onvalue=1, offvalue=0)
            self.checks[key][1].pack(side=tkinter.BOTTOM, anchor=tkinter.S)

    def process(self):
        # get the path to the directory containing the data files
        self.path = Path(tkinter.filedialog.askdirectory())
        if self.path.is_dir():
            names = tkinter.simpledialog.askstring('Variables', 'Enter The Names of the Variables Your Data is Testing\n Example: Time,Temprature \n(separated by commas):')
            names = [x.strip() for x in names.split(',')] + ['#']
            self.check(key=self.path.stem)
            self.hplc_import(path=self.path, names=names)

    def import_file(self):
        # get the path to the file containing the data
        self.path = Path(tkinter.filedialog.askopenfilename())
        if self.path.is_file():
            file_extension = self.path.suffix.lower()
            ind_cols = tkinter.simpledialog.askinteger('Index', 'Number of Index Levels?:')

            if file_extension == '.xlsx' or file_extension == '.xls':
                # import the excel file into a dataframe
                self.data[self.path.stem] = pd.read_excel(self.path, index_col=list(np.arange(0,ind_cols)))
                print(self.data[self.path.stem])
            elif file_extension == '.ods':
                # import the ods file into a dataframe
                self.data[self.path.stem] = pd.read_excel(self.path, index_col=list(np.arange(0,ind_cols)), engine='odf')
            else:
                try: 
                    # import the csv file into a dataframe
                    self.data[self.path.stem] = pd.read_csv(self.path, index_col=list(np.arange(0,ind_cols)))
                except:
                    tkinter.messagebox.showerror('File Type Error', 'File Type Not Recognized')
                    return
            self.check(key=self.path.stem)

    def hplc_import(self, path, names = None):
        self.data[self.path.stem] = pd.DataFrame()
        for file in path.glob('*.xls'):
            
            temp = pd.read_excel(file, skiprows=1)
            temp = temp.transpose()
            temp.columns = temp.iloc[0]
            temp = temp.drop(temp.index[0])
            temp = temp.drop(columns=['Name'])
            temp.dropna(axis=1, how='all', inplace=True)
            temp.Sample_Name.fillna(method='ffill', inplace=True)
            temp.dropna(axis=0, how='any', inplace=True)
            temp = temp.transpose()
        
            self.data[self.path.stem] = pd.concat([self.data[self.path.stem], temp], axis=1)
        self.data[self.path.stem].columns = [x for x in range(len(self.data[self.path.stem].columns))]
        self.data[self.path.stem].index.name = '#'
        self.data[self.path.stem] = self.data[self.path.stem].transpose()
        # change any nan values to 0
        self.data[self.path.stem].fillna(0, inplace=True)

        # if names are provided, split the Sampel_Name column into the names provided
        if names != None:
            for i in range(len(names)-1):
                self.data[self.path.stem][names[i]] = self.data[self.path.stem]['Sample_Name'].str.split(' ').str[i]
                # bring the names to the front of the dataframe
                self.data[self.path.stem] = self.data[self.path.stem][[names[i]] + [col for col in self.data[self.path.stem].columns if col != names[i]]]
            self.data[self.path.stem].drop(columns=['Sample_Name'], inplace=True)

        # check if any data can be converted to numeric
        for col in self.data[self.path.stem].columns:
            try:
                self.data[self.path.stem][col] = pd.to_numeric(self.data[self.path.stem][col])
            except:
                pass
        
        self.data[self.path.stem] = self.data[self.path.stem]
        print(self.data[self.path.stem])
    
    def save_as(self):
        self.path = Path(tkinter.filedialog.asksaveasfilename(initialdir=self.path.parent,
                                                title='Save File',
                                                filetypes=(('Excel Files', '*.xlsx'), ('OpenDocument', '*.ods'), ('All Files', '*.*'))))
        # if no file extension is given, add .xlsx
        if self.path.suffix == '':
            self.path = self.path.with_suffix('.xlsx')
        file_extension = self.path.suffix.lower()
        for key in self.check():
            if file_extension == '.xlsx' or file_extension == '.xls':
                with pd.ExcelWriter(str(self.path.stem) + '_' + str(key) + '.xlsx') as writer:
                    self.data[key].to_excel(writer, sheet_name=str(key))
            elif file_extension == '.ods':
                self.data[key].to_excel(str(self.path.stem) + '_' + str(key) + '.ods', engine='odf')
            else:
                self.data[key].to_csv(str(self.path.stem) + '_' + str(key) + '.csv')                        

    def create_grid_new(self, key=None):
        #  display the data in a excel like grid in a new TopLevel window
        grid = tkinter.Toplevel(self.master, takefocus=True, padx=10, pady=10)
        grid.title(key)

        row_canvas = tkinter.Canvas(grid, borderwidth=0, highlightthickness=0)
        row_canvas.pack(side=tkinter.TOP, fill=tkinter.X)
        row_canvas.config(scrollregion=row_canvas.bbox(tkinter.ALL))
        
        col_canvas = tkinter.Canvas(grid, borderwidth=0, highlightthickness=0)
        col_canvas.pack(side=tkinter.LEFT, fill=tkinter.Y)
        col_canvas.config(scrollregion=col_canvas.bbox(tkinter.ALL))

        grid_canvas = tkinter.Canvas(grid, borderwidth=0, highlightthickness=0)
        grid_canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        grid_canvas.config(scrollregion=grid_canvas.bbox(tkinter.ALL))

        # create scroll bars
        hbar = tkinter.Scrollbar(grid, orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        hbar.config(command=grid_canvas.xview)
        vbar = tkinter.Scrollbar(grid, orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        vbar.config(command=grid_canvas.yview)

        # bind vertical scroll bar to mouse wheel
        grid.bind_all("<MouseWheel>", lambda event: grid_canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # create a frame to contain the grids
        row_frame = tkinter.Frame(row_canvas)
        row_window = row_canvas.create_window((0,0), window=row_frame, anchor='nw')
        col_frame = tkinter.Frame(col_canvas)
        col_window = col_canvas.create_window((0,0), window=col_frame, anchor='nw')
        grid_frame = tkinter.Frame(grid_canvas)
        grid_window = grid_canvas.create_window((0,0), window=grid_frame, anchor='nw')

        # create entry boxes for the row and column names
        row_names = []
        col_names = []
        for i in range(len(self.data[key].index)):
            row_names.append(tkinter.Entry(row_frame, width=10))
            row_names[i].grid(row=i, column=0)
            row_names[i].insert(0, self.data[key].index[i])
        for i in range(len(self.data[key].columns)):
            col_names.append(tkinter.Entry(col_frame, width=10))
            col_names[i].grid(row=0, column=i)
            col_names[i].insert(0, self.data[key].columns[i])
        
        # create entry boxes for the data
        data = []
        for i in range(len(self.data[key].index)):
            data.append([])
            for j in range(len(self.data[key].columns)):
                data[i].append(tkinter.Entry(grid_frame, width=10))
                data[i][j].grid(row=i, column=j)
                data[i][j].insert(0, self.data[key].iloc[i, j])
        
        # bind the scroll bars to the canvas
        row_canvas.config(xscrollcommand=hbar.set)
        col_canvas.config(yscrollcommand=vbar.set)
        grid_canvas.config(xscrollcommand=hbar.set, yscrollcommand=vbar.set)

        # bind the entry boxes to the scroll bars
        def xview(*args):
            row_canvas.xview(*args)
            grid_canvas.xview(*args)
        def yview(*args):
            col_canvas.yview(*args)
            grid_canvas.yview(*args)
        row_canvas.xview_moveto(0)
        col_canvas.yview_moveto(0)
        grid_canvas.xview_moveto(0)
        grid_canvas.yview_moveto(0)
        row_canvas.config(xscrollcommand=xview)
        col_canvas.config(yscrollcommand=yview)
        grid_canvas.config(xscrollcommand=xview, yscrollcommand=yview)

        # update the scroll region to encompass the inner frame
        def update_scroll_region(event):
            row_canvas.config(scrollregion=row_canvas.bbox(tkinter.ALL))
            col_canvas.config(scrollregion=col_canvas.bbox(tkinter.ALL))
            grid_canvas.config(scrollregion=grid_canvas.bbox(tkinter.ALL))
        row_frame.bind('<Configure>', update_scroll_region)
        col_frame.bind('<Configure>', update_scroll_region)
        grid_frame.bind('<Configure>', update_scroll_region)



    def create_grid(self, key=None):
        #  display the data in a excel like grid in a new TopLevel window
        grid = tkinter.Toplevel(self.master, takefocus=True, padx=10, pady=10)
        grid.title(key)

        # Create a canvas to contain the grid frame and scrollbar
        canvas = tkinter.Canvas(grid, borderwidth=0, highlightthickness=0)
        
        # create scroll bars
        hbar = tkinter.Scrollbar(grid, orient=tkinter.HORIZONTAL)
        hbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
        hbar.config(command=canvas.xview)
        vbar = tkinter.Scrollbar(grid, orient=tkinter.VERTICAL)
        vbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
        vbar.config(command=canvas.yview)

        # bind vertical scroll bar to mouse wheel
        grid.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # bind horizontal scroll bar to shift mouse wheel
        grid.bind_all("<Shift-MouseWheel>", lambda event: canvas.xview_scroll(int(-1*(event.delta/120)), "units"))

        # bind vertical scroll bar to page up and page down keys
        grid.bind_all("<Prior>", lambda event: canvas.yview_scroll(-1, "pages"))
        grid.bind_all("<Next>", lambda event: canvas.yview_scroll(1, "pages"))

        # bind horizontal scroll bar to shift page up and shift page down keys
        grid.bind_all("<Shift-Prior>", lambda event: canvas.xview_scroll(-1, "pages"))
        grid.bind_all("<Shift-Next>", lambda event: canvas.xview_scroll(1, "pages"))

        # Create a frame to hold the grid entries
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        grid_frame = tkinter.Frame(canvas)
        canvas.create_window((0, 0), window=grid_frame, anchor=tkinter.NW)

        # Create labels for the index columns
        for col, name in enumerate(self.data[key].index.names):
            label = tkinter.Label(grid_frame, text=name, font=('Arial', 12, 'bold'))
            label.grid(row=0, column=col)
        
        # Create a Tkinter Label for each index value in the multiindex and align under the respective column header
        if len(self.data[key].index.names) > 1:
            for row, index in enumerate(self.data[key].index):
                for col, name in enumerate(self.data[key].index.names):
                    entry = tkinter.Label(grid_frame, text=index[col], font=('Arial', 12))
                    entry.grid(row=row+1, column=col)
        else:
            for row, index in enumerate(self.data[key].index):
                entry = tkinter.Label(grid_frame, text=index, font=('Arial', 12))
                entry.grid(row=row+1, column=0)

        # Create a Tkinter Label for the column headers
        for col, header in enumerate(self.data[key].columns):
            label = tkinter.Label(grid_frame, text=header, font=('Arial', 12, 'bold'))
            label.grid(row=0, column=col+len(self.data[key].index.names))
                
        # Create a Tkinter Entry widget for each cell in the grid
        self.entries = {}
        for row, index in enumerate(self.data[key].index):
            for col, column in enumerate(self.data[key].columns):
                entry_var = tkinter.StringVar(value=self.data[key].at[index, column])
                entry = tkinter.Entry(grid_frame, textvariable=entry_var, font=('Arial', 12))
                entry.grid(row=row+1, column=col+len(self.data[key].index.names))
                self.entries[(row, col)] = entry_var

        # Update the canvas scroll region after the grid frame is created
        grid_frame.update_idletasks()

        # configure the canvas
        canvas.config(yscrollcommand=vbar.set)
        canvas.config(xscrollcommand=hbar.set)
        canvas.config(scrollregion=canvas.bbox("all"))

    def display(self):
        # create a grid for each data frame marked in checkboxes
        for key in self.check():
            self.create_grid_new(key)

        # get grids with the title of the data frame and destroy them
        for grid in self.master.winfo_children():
            if isinstance(grid, tkinter.Toplevel) and grid.title() not in self.check():
                grid.destroy()

def main():
    run = HPLC(master=tkinter.Tk())
    run.master.mainloop()

if __name__ == '__main__':
    main()