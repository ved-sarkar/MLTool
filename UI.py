import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import ttkwidgets
from DataScience import Data, Controller, AsyncTrainModel
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
from threading import Thread

# Main App Class
class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self._frame = None

        self.title("MedML")
        self.window_width = 800
        self.window_height = 900

        # get the screen dimension
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        # find the center point
        center_x = int(screen_width/2 - self.window_width / 2)
        center_y = int(screen_height/2 - self.window_height / 2)

        # set the position of the window to the center of the screen
        self.geometry(f'{self.window_width}x{self.window_height}+{center_x}+{center_y}')

        self.controller = Controller()

        self.switch_frame(StartPage)

        #self.modelNames = ['Logistic Regression','Support Vector Machine','Decision Tree','k-Nearest Neighbour','Extreme Gradient Boosting','Random Forest']
        #self.test_names = ['Accuracy','Sensitivity/Recall','PPV/Precision','Specificity','ROC AUC','Brier score','Confusion matrix','Feature Importance Scores','Shap Feature Importance','Partial Dependence Plots']

    def switch_frame(self, frame_class, **kwargs):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self, **kwargs)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill='both', expand=True)

# Initial Starting Page of the App
class StartPage(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)
        #tk.Label(self, text="This is the start page").pack(side="top", fill="x", pady=10)
        #tk.Button(self, text="Open page one", command=lambda: master.switch_frame(PageOne)).pack()
        #tk.Button(self, text="Open page two", command=lambda: master.switch_frame(PageTwo)).pack()
        self.text1 = ttk.Label(self, text="Welcome to MedML")
        self.text2 = ttk.Label(self, text="Please use the Button below to select a File")

        self.text1.config(font=('Helvatical bold',20))
        self.text2.config(font=('Helvetica', 14))

        self.text1.grid(row=0, column=0)
        self.text2.grid(row=1, column=0)

        self.button_explore = ttk.Button(self, text = "Browse Files", command = lambda: self.browseFiles(master)).grid(row=2, column=0)

        self.rowconfigure(0, weight=1)
        self.rowconfigure(1, weight=1)
        self.rowconfigure(2, weight=2)
        self.columnconfigure(0, weight=1)

    def browseFiles(self, master):
        filename = filedialog.askopenfilename(initialdir = "/", title = "Select a File", filetypes = (("Excel", "*.xlsx"), ("all files", "*.*")))
        master.controller.data = Data(filename)
        master.switch_frame(PageOne)

# Select Output Variables for the App
class PageOne(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        ttk.Label(self, text='Please Select the Output Variables').pack()

        self.outputVariableTable = ttkwidgets.CheckboxTreeview(self)
        self.outputVariableTable.heading('#0', text='Output Variables')

        columnNames = master.controller.data.readColumnNames()
        for name in columnNames:
            self.outputVariableTable.insert("", "end", name, text=" " + name)

        self.outputVariableTable.pack(fill='both', expand=True)

        self.frame1 = tk.Frame(self)
        self.frame1.columnconfigure(0, weight=1)
        self.frame1.columnconfigure(1, weight=10)
        self.frame1.columnconfigure(2, weight=1)

        self.label1_1 = ttk.Label(self.frame1, text="1")
        self.label1_1.grid(row=0, column=0, sticky='E')
        self.sliderVariable = tk.StringVar()
        self.slider = ttk.Scale(self.frame1, from_=1, to=50, orient='horizontal', length=450, variable=self.sliderVariable)
        self.slider.set(1)
        self.slider.bind('<ButtonRelease-1>', self.on_configure)
        self.slider.grid(row=0, column=1)
        self.label1_2 = ttk.Label(self.frame1, text=50)
        self.label1_2.grid(row=0, column=2, sticky='W')
        self.label1_3 = ttk.Label(self.frame1, text="Percentage of Samples for Validation: " + str(round(self.slider.get())) + "%")
        self.label1_3.grid(row=1, column=0, columnspan=3)

        self.frame1.pack(fill='x', expand=True, padx=20, pady=20)

        self.submitButton = ttk.Button(self, text="Continue", command=lambda: self.submitVariables(master))
        self.submitButton.pack(side='bottom', fill='both', expand=True, padx=20)

    def submitVariables(self, master):
        master.controller.data.setInputOutputVariables(self.outputVariableTable.get_checked())
        master.controller.data.splitData(round(self.slider.get())/100)
        master.switch_frame(PageTwo)
    
    def on_configure(self, event):
        self.label1_3.configure(text="Percentage of Samples for Validation: " + str(round(self.slider.get())) + "%")

# Select the Categorical Variables for the App as well as Determine what Pre-Processing Steps to Perform on the Data
class PageTwo(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        ttk.Label(self, text='Please Select the Categorical Variables').pack()

        self.categoricalVariableTable = ttkwidgets.CheckboxTreeview(self)
        self.categoricalVariableTable.heading('#0', text='Categorical Variables')

        columnNames = master.controller.data.readColumnNames()
        categoricalColumnNames = master.controller.data.returnColumnStringDtypes()

        for name in columnNames:
            if name in categoricalColumnNames:
                self.categoricalVariableTable.insert("", "end", name, text=" " + name, tags=('checked',))
            else:
                self.categoricalVariableTable.insert("", "end", name, text=" " + name, tags=('unchecked',))

        self.categoricalVariableTable.pack(fill='both', expand=True)

        self.frame1 = tk.Frame(self)
        self.frame1.rowconfigure(0, weight=1)
        self.frame1.rowconfigure(1, weight=1)
        self.frame1.rowconfigure(2, weight=1)
        self.frame1.columnconfigure(0, weight=1)
        self.frame1.columnconfigure(1, weight=1)
        ttk.Label(self.frame1, text='Normalise Continuous Variables?').grid(row=0, column = 0, columnspan=2)
        self.normalise = tk.IntVar()
        Yes2 = ttk.Radiobutton(self.frame1, text='Yes', variable=self.normalise, value=1)
        No2 = ttk.Radiobutton(self.frame1, text='No', variable=self.normalise, value=0)
        Yes2.grid(row=1, column=0, sticky='W')
        No2.grid(row=2, column=0, sticky='W')
        self.normalise_var = tk.StringVar()
        combobox1 = ttk.Combobox(self.frame1, textvariable=self.normalise_var)
        combobox1['values'] = ('Standardise', 'Normalise', 'MinMax')
        combobox1['state'] = 'readonly'
        combobox1.current(0)
        combobox1.grid(row=1, rowspan=2, column=1, padx=20, sticky='E')

        self.frame1.pack(fill='x', padx=10, pady=20)

        self.frame2 = tk.Frame(self)
        self.frame2.rowconfigure(0, weight=1)
        self.frame2.rowconfigure(1, weight=1)
        self.frame2.rowconfigure(2, weight=1)
        self.frame2.columnconfigure(0, weight=1)
        self.frame2.columnconfigure(1, weight=1)
        ttk.Label(self.frame2, text='One Hot Encode Categorical Variables?').grid(row=0, column=0, columnspan=2)
        self.one_hot_encode = tk.IntVar()
        Yes1 = ttk.Radiobutton(self.frame2, text='Yes', variable=self.one_hot_encode, value=1)
        No1 = ttk.Radiobutton(self.frame2, text='No', variable=self.one_hot_encode, value=0)
        Yes1.grid(row=1, column=0, sticky='W')
        No1.grid(row=2, column=0, sticky='W')
        self.encode_var = tk.StringVar()
        combobox2 = ttk.Combobox(self.frame2, textvariable=self.encode_var)
        combobox2['values'] = ('Ordinal Encode', 'One Hot Encode')
        combobox2['state'] = 'readonly'
        combobox2.current(1)
        combobox2.grid(row=1, rowspan=2, column=1, padx=20, sticky='E')

        self.frame2.pack(fill='x', padx=10, pady=10, expand=True)

        self.frame3 = tk.Frame(self)
        self.frame3.rowconfigure(0, weight=1)
        self.frame3.rowconfigure(1, weight=1)
        self.frame3.rowconfigure(2, weight=1)
        self.frame3.rowconfigure(3, weight=2)
        self.frame3.columnconfigure(0, weight=1)
        self.frame3.columnconfigure(1, weight=1)

        ttk.Label(self.frame3, text='Perform Feature Selection?').grid(row=0, column=0, columnspan=2)
        self.isfeatureSelection = tk.IntVar()
        Yes3 = ttk.Radiobutton(self.frame3, text='Yes', variable=self.isfeatureSelection, value=1)
        No3 = ttk.Radiobutton(self.frame3, text='No', variable=self.isfeatureSelection, value=0)
        Yes3.grid(row=1, column=0, sticky='W')
        No3.grid(row=2, column=0, sticky='W')
        self.feature_var = tk.StringVar()
        self.combobox3 = ttk.Combobox(self.frame3, textvariable=self.feature_var)
        self.combobox3['values'] = ('Principal Component Analysis', 'Recursive Feature Elimination')
        self.combobox3['state'] = 'readonly'
        self.combobox3.current(1)
        self.combobox3.grid(row=1, rowspan=2, column=1, padx=10, sticky='E')

        self.combobox3.bind('<<ComboboxSelected>>', self.feature_selector_changed)

        self.frame4 = tk.Frame(self.frame3)
        self.frame4.columnconfigure(0, weight=1)
        self.frame4.columnconfigure(1, weight=3)
        self.frame4.columnconfigure(2, weight=1)

        self.label4_1 = ttk.Label(self.frame4, text="1")
        self.label4_1.grid(row=0, column=0)
        self.sliderVariable = tk.StringVar()
        self.slider = ttk.Scale(self.frame4, from_=1, to=len(columnNames)-1, orient='horizontal', length=200, variable=self.sliderVariable)
        self.slider.set(1)
        self.slider.bind('<ButtonRelease-1>', self.on_configure)
        self.slider.grid(row=0, column=1, padx=20)
        self.label4_2 = ttk.Label(self.frame4, text=str(len(columnNames)-1))
        self.label4_2.grid(row=0, column=2)
        self.label4_3 = ttk.Label(self.frame4, text="Minimum Number of Features to Keep: " + str(round(self.slider.get())))
        self.label4_3.grid(row=1, column=0, columnspan=3)

        self.frame4.grid(row=3, column=0, columnspan=2, padx=20)

        self.frame3.pack(fill='x', padx=10, pady=10, expand=True)
        
        self.submitButton = ttk.Button(self, text="Continue", command=lambda: self.submitVariables(master))
        self.submitButton.pack(side='top', fill='x', expand=True, padx=20)

    def submitVariables(self, master):
        master.controller.data.setVariableTypes(self.categoricalVariableTable.get_checked())
        master.controller.data.setContinuousVariableNormalisation(self.normalise.get(), self.normalise_var.get())
        master.controller.data.setCategoricalVariableEncoding(self.one_hot_encode.get(), self.encode_var.get())
        master.controller.setValidModels()
        master.controller.data.setFeatureSelection(self.isfeatureSelection.get(), self.feature_var.get(), round(self.slider.get()))
        master.switch_frame(PageThree)

    def feature_selector_changed(self):
        pass

    def on_configure(self, event):
        self.label4_3.configure(text="Minimum Number of Features to Keep: " + str(round(self.slider.get())))

# Get the Results of the Preprocessing Steps and Select which Variables to Drop
class PageThree(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        ttk.Label(self, text='Select which Input Variables to Drop').pack()

        self.dropVariableTable = ttkwidgets.CheckboxTreeview(self, columns = ('FSS'))
        self.dropVariableTable.heading('#0', text='Input Variables')
        self.dropVariableTable.heading('FSS', text='Feature Selector Ranking')

        self.dropVariableTable.column('FSS', anchor='center')

        features = master.controller.data.afterFeatureSelection

        for index in range(len(features[0])):
            if features[0][index] in features[1]:
                self.dropVariableTable.insert("", "end", features[0][index], text= " " + features[0][index], values=(str(features[2][index])), tags=("Keep", "checked"))
            else:
                self.dropVariableTable.insert("", "end", features[0][index], text= " " + features[0][index], values=(str(features[2][index])), tags=("Remove", "unchecked"))

        self.dropVariableTable.tag_configure("Remove", background='red')
        self.dropVariableTable.tag_configure("Keep", background='green')

        self.dropVariableTable.pack(fill='both', expand=True)

        self.submitButton = ttk.Button(self, text="Drop Features", command=lambda: self.submitVariables(master))
        self.submitButton.pack(side='bottom', fill='both', expand=True, padx=20)

    def submitVariables(self, master):
        master.controller.data.setFeatureSelectedData(self.dropVariableTable.get_checked())
        master.switch_frame(PageFour)

# Select which Models to Train
class PageFour(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        ttk.Label(self, text='Select which ML Models to Train').pack()

        self.modelSelectTable = ttkwidgets.CheckboxTreeview(self, columns=('Cross Validation Metric', 'Test Set Score'))
        self.modelSelectTable.heading('#0', text='ML Models', anchor='center')
        self.modelSelectTable.heading('Cross Validation Metric', text='Cross Validation Metric', anchor='center')
        self.modelSelectTable.heading('Test Set Score', text='Test Set Score', anchor='center')

        self.modelSelectTable.column('#0', anchor='center')
        self.modelSelectTable.column('Cross Validation Metric', anchor='center')
        self.modelSelectTable.column('Test Set Score', anchor='center')

        for model in master.controller.validModels:
            self.modelSelectTable.insert("", "end", model.name, text= " " + model.name, values=('-', '-'))

        self.modelSelectTable.pack(fill='both', expand=True)

        self.progressVariable = tk.IntVar()
        self.progressBar = ttk.Progressbar(self, orient='horizontal', length=500, mode='indeterminate', variable=self.progressVariable)
        self.progressBar.pack(fill='x', expand=True, padx='20', pady=20)

        self.frame1 = tk.Frame(self)
        self.frame1.columnconfigure(0, weight=1)
        self.frame1.columnconfigure(1, weight=1)
        self.submitButton1 = ttk.Button(self.frame1, text="Train Models", command=lambda: self.trainModels(master))
        #self.submitButton1.pack(side='bottom', fill='both', expand=True, padx=20)
        self.submitButton1.grid(row=0, column=0, padx=20)
        self.submitButton2 = ttk.Button(self.frame1, text="Continue", command=lambda: self.submitVariables(master), state='disabled')
        #self.submitButton2.pack(side='bottom', fill='both', expand=True, padx=20)
        self.submitButton2.grid(row=0, column=1)
        self.frame1.pack(expand=True, fill='x')

    def submitVariables(self, master):
        master.controller.setSelectedTestModels(self.modelSelectTable.get_checked())
        master.switch_frame(PageFive)

    def trainModels(self, master):
        self.submitButton1.configure(state='disabled')
        self.submitButton2.configure(state='disabled')
        self.progressBar.start(50)
        threadList = master.controller.trainModels(self.modelSelectTable.get_checked())
        self.monitor(master, threadList)

        #score = master.controller.getModelScores()
        #for key, value in score.items():
            #if value != None:
                #self.modelSelectTable.item(key, values=(str(value[0]), str(value[1])))

    def monitor(self, master, threadList):
        for thread in threadList:
            if thread.is_alive():
                master.after(500, lambda: self.monitor(master, threadList))
                break
        else:
            score = master.controller.getModelScores()
            for key, value in score.items():
                if value != None:
                    self.modelSelectTable.item(key, values=(str(value[0]), str(value[1])))
            self.progressBar.stop()
            self.submitButton2.configure(state='normal')
            self.submitButton1.configure(state='normal')

# See the Outputs of the Trained Model Tests
class PageFive(tk.Frame):
    def __init__(self, master):
        tk.Frame.__init__(self, master)

        # Frame to Choose Models
        self.frame1 = tk.Frame(self)

        self.hscrollbar = ttk.Scrollbar(self.frame1, orient='horizontal')
        self.hscrollbar.pack(fill='x', side='bottom', expand=False)
        self.canvas1 = tk.Canvas(self.frame1, xscrollcommand=self.hscrollbar.set, height=30, highlightthickness=0)
        self.canvas1.pack(side='top', fill='both', expand=True)
        self.hscrollbar.config(command=self.canvas1.xview)
        self.canvas1.xview_moveto(0)
        self.canvas1.yview_moveto(0)

        self.frame2 = tk.Frame(self.canvas1)
        self.modelButtonDict = {}
        for model in master.controller.selectedTestModels:
            button1 = ttk.Button(self.frame2, text=model.name)
            button1.config(command=lambda button=button1: self.changeModel(master, button))
            self.modelButtonDict[model.name] = master.controller.selectedTestModels.index(model)
            button1.pack(side='left')
        self.id = self.canvas1.create_window(0, 0, window=self.frame2, anchor='nw')
        #self.canvas1.configure(scrollregion=self.canvas1.bbox("all"))

        # Track changes to the canvas and frame width and sync them,
        # also updating the scrollbar.
        def _configure_interior(event):
            # Update the scrollbars to match the size of the inner frame.
            size = (self.frame2.winfo_reqwidth(), self.frame2.winfo_reqheight())
            self.canvas1.config(scrollregion="0 0 %s %s" % size)
            if self.frame2.winfo_reqwidth() != self.canvas1.winfo_width():
                # Update the canvas's width to fit the inner frame.
                self.canvas1.config(width=self.frame2.winfo_reqwidth())
        self.frame2.bind('<Configure>', _configure_interior)

        """def _configure_canvas(event):
            if self.frame2.winfo_reqwidth() != self.canvas1.winfo_width():
                # Update the inner frame's width to fill the canvas.
                self.canvas1.itemconfigure(self.id, width=self.canvas1.winfo_width())
        #self.canvas1.bind('<Configure>', _configure_canvas)"""
        self.canvas1.bind('<Configure>', lambda e: self.canvas1.configure(scrollregion=self.canvas1.bbox('all')))

        self.frame1.pack(fill='both', expand=True, padx=20, pady=10)

        self.frame5 = tk.Frame(self)

        # Checkbox Treeview to select Tests
        self.testTreeView = ttkwidgets.CheckboxTreeview(self.frame5)

        self.testTreeView.column('#0', anchor='center')
        self.testTreeView.heading('#0', text='Model Tests', anchor='center')

        for test in master.controller.selectedTestModels[0].validTests:
            self.testTreeView.insert("", "end", test.name, text= " " + test.name)

        self.testTreeView.bind('<<TreeviewSelect>>', lambda event: self.changeTest(event, master))
        self.testTreeView.tag_configure("selected", background='blue')

        self.testTreeView.focus(self.testTreeView.identify_row(0))

        self.testTreeView.pack(fill='y', side='left', padx=20, pady=10)
        
        # Matplotlib Graph Drawing
        self.frame3 = tk.Frame(self.frame5)
        self.label1 = ttk.Label(self.frame3, text=master.controller.validModels[0].name + " - "  + self.testTreeView.focus(), anchor='center')
        self.label1.pack(fill='x', expand=True, padx=20, pady=20)

        self.f = Figure(figsize=(5, 5), dpi=100)
        self.ax = self.f.add_subplot(111)
        master.controller.selectedTestModels[0].validTests[0].generateFigure(self.ax)
        self.canvas2 = FigureCanvasTkAgg(self.f, master=self.frame3)  # A tk.DrawingArea.
        self.canvas2.draw()
        self.canvas2.get_tk_widget().pack(fill='both', expand=True)

        self.frame3.pack(fill='both', padx=20, pady=20, side='right')

        self.frame5.pack(fill='both', expand=True)

        # Export and Quit Buttons
        self.frame4 = tk.Frame(self)
        self.frame4.rowconfigure(0, weight=1)
        self.frame4.columnconfigure(0, weight=1)
        self.frame4.columnconfigure(1, weight=1)
        self.submitButton3 = ttk.Button(self.frame4, text="Export", command=lambda: self.submitVariable(master))
        #self.submitButton3.(fill='x', expand=True, padx=10, pady=10)
        self.submitButton3.grid(row=0, column=0, padx=10, pady=10)
        self.submitButton4 = ttk.Button(self.frame4, text="Quit")
        #self.submitButton4.pack(fill='x', expand=True, padx=10, pady=10)
        self.submitButton4.grid(row=0, column=1, padx=10, pady=10)

        self.frame4.pack(fill='x', expand=True, padx=20, pady=10)

        self.currentlySelectedModel = master.controller.validModels[0].name
        self.currentlySelectedTest = self.testTreeView.focus()
        currentlySelectedTags = self.testTreeView.item(self.currentlySelectedTest, "tags")
        newTags = [tag for tag in currentlySelectedTags if tag != ["selected"]]
        self.testTreeView.item(self.currentlySelectedTest, tags=newTags)

    def submitVariable(self, master):
        master.controller.exportData()

    def changeModel(self, master, button):
        self.currentlySelectedModel = button['text']
        self.label1.configure(text=button['text'] + " - " + self.testTreeView.focus())
        self.testTreeView.delete(*self.testTreeView.get_children())
        for test in master.controller.selectedTestModels[self.modelButtonDict[button['text']]].validTests:
            self.testTreeView.insert("", "end", test.name, text= " " + test.name)

    def changeTest(self, event, master):
        currentlySelectedTags = self.testTreeView.item(self.currentlySelectedTest, "tags")
        newTags = [tag for tag in currentlySelectedTags if tag != "selected"]
        self.testTreeView.item(self.currentlySelectedTest, tags=newTags)

        self.testTreeView.item(self.testTreeView.focus(), tags=newTags + ['selected'])
        self.currentlySelectedTest = self.testTreeView.focus()
        self.label1.configure(text=self.currentlySelectedModel + " - " + self.testTreeView.focus())

        for test in master.controller.selectedTestModels[self.modelButtonDict[self.currentlySelectedModel]].validTests:
            if test.name == self.testTreeView.focus():
                self.ax.cla()
                test.generateFigure(self.ax)
                self.canvas2.draw()

if __name__ == "__main__":
    app = App()
    app.mainloop()