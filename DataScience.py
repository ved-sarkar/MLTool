from threading import Thread
import numpy as np
from numpy import mean
from numpy import std
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
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
from sklearn.feature_selection import RFECV
from sklearn.model_selection import KFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, LabelBinarizer, OneHotEncoder, OrdinalEncoder, Normalizer, MinMaxScaler
import os
from pathlib import Path
from joblib import dump, load
import re

class Data():

    def __init__(self, fileName):
        self.fileName = fileName
        if (self.fileName != ""):
            self.loadData()
        self.inputVariables = []
        self.outputVariables = []
        self.categoricalVariables = []
        self.continuousVariables = []

        self.encoderDict = {"One Hot Encode": OneHotEncoder, "Ordinal Encode": OrdinalEncoder, "None": None}
        self.normaliserDict = {"Standardise": StandardScaler, "Normaliser": Normalizer, "MinMax": MinMaxScaler, "None": None}

    def loadData(self):
        self.df = pd.read_excel(self.fileName)

    def readColumnNames(self):
        return np.array(self.df.columns.values)

    def returnColumnStringDtypes(self):
        return self.df.select_dtypes(include='object').columns.values

    def splitData(self, test_size):
        X_train, X_test, Y_train, Y_test = train_test_split(self.df[self.inputVariables], self.df[self.outputVariables], test_size=test_size, random_state=1234)

        self.X_train = pd.DataFrame(X_train, columns=self.inputVariables)
        self.X_test = pd.DataFrame(X_test, columns=self.inputVariables)

        self.Y_train = pd.DataFrame(Y_train, columns=self.outputVariables)
        self.Y_test = pd.DataFrame(Y_test, columns=self.outputVariables)

    def setInputOutputVariables(self, outputVariables):
        self.outputVariables = outputVariables
        self.inputVariables = [columnName for columnName in self.df.columns if (columnName not in self.outputVariables)]

    def setVariableTypes(self, categoricalVariables):
        self.categoricalVariables = categoricalVariables
        self.continuousVariables = [columnName for columnName in self.df.columns if (columnName not in self.categoricalVariables)]

    def setContinuousVariableNormalisation(self, apply, option):
        if apply:
            self.continuousNormaliser = option
        else:
            self.continuousNormaliser = 'None'

    def setCategoricalVariableEncoding(self, apply, option):
        if apply:
            self.categoricalEncoder = option
        else:
            self.categoricalEncoder = 'None'

    def setFeatureSelection(self, apply, option, minFeaturesToSelect):
        if apply:
            self.featureSelection = option
            if option == "Recursive Feature Elimination":

                featureSelectionPipeline = self.createFeatureSelectionPipeline(self.normaliserDict[self.continuousNormaliser], self.encoderDict[self.categoricalEncoder], RFECV, estimator=LogisticRegression(random_state=1234), step=1, min_features_to_select=minFeaturesToSelect)

                featureSelectionPipeline.fit(self.X_train, self.Y_train.to_numpy().ravel())

                if self.categoricalEncoder != 'None' and self.continuousNormaliser != 'None':
                    expanded_features = [re.split("^(.*?)__", feature_name)[-1] for feature_name in featureSelectionPipeline['Preprocessing'].get_feature_names_out()]
                else:
                    expanded_features = self.X_train.columns

                selected_features = featureSelectionPipeline['selector'].get_feature_names_out(expanded_features)
                feature_scores = featureSelectionPipeline['selector'].ranking_

                self.afterFeatureSelection = (expanded_features, selected_features, feature_scores)
                self.featureSelectionPipeline = featureSelectionPipeline

            elif option == "Principal Component Analysis":
                pass
        else:
            self.featureSelection = 'None'
            featureSelectionPipeline = self.createFeatureSelectionPipeline(self.normaliserDict[self.continuousNormaliser], self.encoderDict[self.categoricalEncoder], None)

            if featureSelectionPipeline != None:
                featureSelectionPipeline.fit(self.X_train, self.Y_train.to_numpy().ravel())

                expanded_features = self.X_train.columns
                if self.categoricalEncoder != "None":
                    expanded_features = [re.split("^(.*?)__", feature_name)[-1] for feature_name in featureSelectionPipeline['Preprocessing'].get_feature_names_out()]

                self.afterFeatureSelection = (expanded_features, expanded_features, np.array([1 for _ in expanded_features]))
            else:
                self.afterFeatureSelection = (self.X_train.columns, self.X_train.columns, np.array([1 for _ in self.X_train.columns]))
            self.featureSelectionPipeline = featureSelectionPipeline

    def createFeatureSelectionPipeline(self, normaliser, encoder, featureSelector, **kwargs):
        kf = KFold(n_splits=5, shuffle=True)

        columnTransformerBuildList= []
        if normaliser != None:
            columnTransformerBuildList.append(('continuousData', normaliser(), [column for column in self.continuousVariables if column not in self.outputVariables]))
        if encoder != None:
            columnTransformerBuildList.append(('categoricalData', encoder(drop='if_binary', handle_unknown='ignore'), [column for column in self.categoricalVariables if column not in self.outputVariables]))

        pipelineBuildList = []

        if len(columnTransformerBuildList) != 0:
            pipelineBuildList.append(("Preprocessing", ColumnTransformer(columnTransformerBuildList, remainder='passthrough')))

        if self.featureSelection != "None":
            pipelineBuildList.append(("selector", featureSelector(cv=kf, **kwargs)))

        if self.featureSelection == "None" and len(columnTransformerBuildList) == 0:
            return None
        else:
            return Pipeline(pipelineBuildList)

    def setFeatureSelectedData(self, selectedColumns):
        #! Still Need to Actually use selectedColumns variable passed from the UI
        if self.featureSelectionPipeline != None:
            self.X_train_modified = pd.DataFrame(self.featureSelectionPipeline.transform(self.X_train), columns=self.afterFeatureSelection[1])
            self.X_test_modified = pd.DataFrame(self.featureSelectionPipeline.transform(self.X_test), columns=self.afterFeatureSelection[1])
        else:
            self.X_train_modified = self.X_train
            self.X_test_modified = self.X_test

class TestWrapper():
    def __init__(self, name, testClass, title, x_axis_title, y_axis_title, x_axis_tick_labels, y_axis_tick_labels, graphType):
        self.name = name
        self.testFunction = testClass
        self.title = title
        self.x_axis_title = x_axis_title 
        self.y_axis_title = y_axis_title 
        self.x_axis_tick_labels = x_axis_tick_labels 
        self.y_axis_tick_labels = y_axis_tick_labels
        self.graphType = graphType
        self.result = None
        self.figure = None

    def calculateResult(self, pred_data, actual_data):
        self.result = self.testFunction(actual_data, pred_data)

    def generateFigure(self, ax):
        #ax = plt.subplot()
        ax.xaxis.set_label(self.x_axis_title)
        ax.yaxis.set_label(self.y_axis_title)
        ax.set_title(self.title)
        ax.xaxis.set_ticklabels(self.x_axis_tick_labels)
        ax.yaxis.set_ticklabels(self.y_axis_tick_labels)
        self.graphType(self.result, annot=True, ax=ax, cbar=False)

class ModelWrapper():
    def __init__(self, name, validTests, typeOfModel, modelClass, **kwargs):
        self.name = name
        self.validTests = validTests
        self.typeOfModel = typeOfModel
        self.isTrained = False
        self.model = modelClass(**kwargs)

    def fitModel(self, x_data, y_data, x_test):
        self.model.fit(x_data, y_data.to_numpy().ravel())
        self.testSetResults = self.model.score
        self.predictedValues = self.model.predict(x_test)

    def crossValidateModel(self, x_data, y_data, preprocess):
        kf = KFold(n_splits = 5, shuffle=True)
        pipelineList = []
        if preprocess != None:
            pipelineList.append(("Preprocess", preprocess))
        pipelineList.append(("Model", self.model))
        crossValidatePipeline = Pipeline(pipelineList)
        self.crossValidateResults = cross_validate(crossValidatePipeline, x_data, y_data.to_numpy().ravel(), cv=kf, n_jobs=-1)

class Controller():
    def __init__(self):
        self.models = [
            ModelWrapper('Logistic Regression', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", LogisticRegression),
            ModelWrapper('Support Vector Classifier', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", SVC),
            ModelWrapper('Decision Tree', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", DecisionTreeClassifier),
            ModelWrapper('k-Nearest Neighbour', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", KNeighborsClassifier),
            ModelWrapper('Extreme Gradient Boosting', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", XGBClassifier),
            ModelWrapper('Random Forest', (TestWrapper("Confusion Matrix", confusion_matrix, 'Confusion Matrix', 'Predicted labels', 'Actual labels', ['True','False'], ['True','False'], sns.heatmap),), "Classifier", RandomForestClassifier)
        ]

    def load_data(self, fileName):
        self.data = Data(fileName)

    def setValidModels(self):
        if self.data.outputVariables[0] in self.data.categoricalVariables:
            self.validModels = [model for model in self.models if model.typeOfModel == "Classifier"]
        else:
            self.validModels = [model for model in self.models if model.typeOfModel == "Regression"]

    def setSelectedTestModels(self, selectedModels):
        self.selectedTestModels = [model for model in self.models if (model.name in selectedModels) and model.isTrained]

    def trainModels(self, selectedModels):
        threadList = []
        for model in self.validModels:
            if model.name in selectedModels:
                newThread = AsyncTrainModel(model, self.data)
                threadList.append(newThread)
                newThread.start()
        return threadList

    def getModelScores(self):
        results = {}
        for model in self.validModels:
            if model.isTrained:
                results[model.name] = (np.mean(model.crossValidateResults['test_score']), model.model.score(self.data.X_test_modified, self.data.Y_test))
            else:
                results[model.name] = (None, None)
        return results

    def exportData(self):
        # Get the Parent Path where the Data Lives
        path = Path(self.data.fileName)
        parentPath = path.parent.resolve()
        # Create the Parent Directory
        Path(parentPath / "MedML").mkdir(parents=False, exist_ok=True)
        #os.mkdir(parentPath / "MedML")
        # Save the Feature Selection Data as a Numpy Binary File
        if self.data.featureSelection != 'None':
            np.save(parentPath / "MedML" / "FeatureSelection.npy", self.data.afterFeatureSelection[1])
        for model in self.selectedTestModels:
            # Create a New Directory for each Model
            Path(parentPath / "MedML" / model.name).mkdir(parents=False, exist_ok=True)
            #os.mkdir(parentPath / "MedML" / model.name)
            # Save the Model as a Joblib Serialisation file
            dump(model.model, parentPath / "MedML" / model.name / (model.name + "-Model.joblib"))
            for test in model.validTests:
                # Save each Test as a Numpy Binary File and as a PNG Figure
                np.save(parentPath / "MedML" / model.name / (model.name + "-" + test.name + ".npy"), test.result)
                #if isinstance(test[2], matplotlib.axes._subplots.AxesSubplot):
                    #test[2].savefig(parentPath / "MedML" / key / key + "-" + test[0] + ".png")

class AsyncTrainModel(Thread):
    def __init__(self, model, data):
        super().__init__()
        self.model = model
        self.data = data
    
    def run(self):
        if self.data.featureSelection != "None":
            if self.data.featureSelection == 'Recursive Feature Elimination':
                self.model.crossValidateModel(self.data.X_train, self.data.Y_train, self.data.createFeatureSelectionPipeline(self.data.normaliserDict[self.data.continuousNormaliser], self.data.encoderDict[self.data.categoricalEncoder], RFECV, estimator=LogisticRegression(random_state=1234), step=1, min_features_to_select=1))
            elif self.data.featureSelection == "Principle Component Analysis":
                pass
        else:
            self.model.crossValidateModel(self.data.X_train, self.data.Y_train, self.data.createFeatureSelectionPipeline(self.data.normaliserDict[self.data.continuousNormaliser], self.data.encoderDict[self.data.categoricalEncoder], None))
        self.model.fitModel(self.data.X_train_modified, self.data.Y_train, self.data.X_test_modified)
        for test in self.model.validTests:
            test.calculateResult(self.model.predictedValues, self.data.Y_test)
        self.model.isTrained = True