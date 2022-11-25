import pandas as pd
from typing import Dict, Union, Any
import numpy as np
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, precision_score
import joblib
import lime
import lime.lime_tabular
from src.analytics.models.pipelines import *


def create_xai_pipeline_classification(training_set: pd.DataFrame, target: str, inference_set: pd.DataFrame, type_of_task: str
) -> Dict[str, Dict[str, float]]:
    
    xai_dataset=training_set.drop(columns=[target])
    xai_report={}

    """""
    Make a mapping dictionary which will be used lated to map the explainer index
    with the features names
    """""

    mapping_dict={}
    for feature in range (0,len(xai_dataset.columns.tolist())):
        mapping_dict[feature]=xai_dataset.columns.tolist()[feature]

    """""
    Retrieve model from file system. We have to revisit this spot for adding
    an option for a model from user's file system. Maybe we have to set an optional parameter
    in the function above with the path
    """""

    # model = joblib.load(model_path)

    """""
    Expainability for both classifications tasks
    We have again to revisit here in the future as in case we upload the model
    from the file system we don't care if it is binary or multi-class
    """""

    if type_of_task=='multiclass_classification':
        
        model, eval = create_multiclass_classification_training_model_pipeline(training_set, target) 
        explainer = lime.lime_tabular.LimeTabularExplainer(xai_dataset.values, feature_names=xai_dataset.columns.values.tolist(), mode="classification",random_state=1)
        
        
        for inference_row in range(0,len(inference_set)):
            exp = explainer.explain_instance(inference_set.values[inference_row], model.predict)
            med_report=exp.as_map()
            temp_dict = dict(list(med_report.values())[0])
            map_dict = {mapping_dict[name]: val for name, val in temp_dict.items()}
            xai_report["row{}".format(inference_row)]= map_dict
               

    elif type_of_task=='binary_classification':     
        
        model, eval = create_binary_classification_training_model_pipeline(training_set, target) 
        explainer = lime.lime_tabular.LimeTabularExplainer(xai_dataset.values, feature_names=xai_dataset.columns.values.tolist(), mode="classification",random_state=1)
        
        
        for inference_row in range(0,len(inference_set)):
            exp = explainer.explain_instance(inference_set.values[inference_row], model.predict)
            med_report=exp.as_map()
            temp_dict = dict(list(med_report.values())[0])
            map_dict = {mapping_dict[name]: val for name, val in temp_dict.items()}
            xai_report["row{}".format(inference_row)]= map_dict

            
    return xai_report
