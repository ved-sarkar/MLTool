import numpy as np
from numpy import mean
from numpy import std
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import sklearn
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC
from sklearn import svm
from sklearn.naive_bayes import GaussianNB
from sklearn.model_selection import train_test_split
from sklearn import metrics
from sklearn.datasets import make_classification
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_validate
import xgboost
from xgboost import XGBClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.calibration import calibration_curve
from sklearn.metrics import confusion_matrix
import io
import cv2
import glob 
import os
from pathlib import Path
from joblib import dump, load

class Data():

    def __init__(self, fileName):
        self.fileName = fileName
        if (self.fileName != ""):
            self.loadData()
        self.inputVariables = []
        self.outputVariables = []
        self.categoricalVariables = []
        self.continuousVariables = []

    def loadData(self):
        self.df = pd.read_excel(self.fileName)

    def readColumnNames(self):
        return np.array(self.df.columns.values)

    def exportData(self, data):
        # Get the Parent Path where the Data Lives
        path = Path(self.fileName)
        parentPath = path.parent.resolve()
        # Create the Parent Directory
        os.mkdir(parentPath / "MedML")
        # Save the Feature Selection Data as a Numpy Binary File
        np.save(parentPath / "MedML" / data[0][0])
        for key, value in data[1]:
            # Create a New Directory for each Model
            os.mkdir(parentPath / "MedML" / key)
            # Save the Model as a Joblib Serialisation file
            dump(value[0], parentPath / "MedML" / key / key + "-Model.joblib")
            for test in value[1]:
                # Save each Test as a Numpy Binary File and as a PNG Figure
                np.save(test[1], parentPath / "MedML" / key / key + "-" + test[0] + ".npy")
                if isinstance(test[2], matplotlib.axes._subplots.AxesSubplot):
                    test[2].savefig(parentPath / "MedML" / key / key + "-" + test[0] + ".png")

class Processing():
    def __init__(self):
        pass
