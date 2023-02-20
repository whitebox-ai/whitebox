import numpy as np
import pandas as pd
import streamlit as st
from typing import Dict, Union, List
from matplotlib import pyplot as plt
import json


from tabs.drifting import *
from tabs.sidebar import *
from tabs.overview import *
from tabs.performance import *
from tabs.inferences import *
from tabs.monitors import *
from tabs.alerts import *
from cards import *
from utils.transformation import get_models_names, get_model_from_name

from whitebox import Whitebox

wb = Whitebox(
    host="http://127.0.0.1:8000",
    api_key="c37b902f5af13c43af33652770d7c51008f5e18b0cf4cf9cc870ab93bea98f3f",
)

st.set_option("deprecation.showPyplotGlobalUse", False)

# Load config
# st.set_page_config(page_title="Whitebox", layout="wide")

# ----------------------------------------
def format_evaluation_metrics_binary(
    accuracy: float,
    precision: float,
    recall: float,
    f1: float,
    tn: int,
    fp: int,
    fn: int,
    tp: int,
) -> Dict[str, Union[int, float]]:
    formated_metrics_for_binary = {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "true_negative": tn,
        "false_positive": fp,
        "false_negative": fn,
        "true_positive": tp,
    }

    return formated_metrics_for_binary


models_list = wb.get_models()
model_names = get_models_names(models_list)


evaluation_metrics_binary = format_evaluation_metrics_binary(
    0.64, 0.5, 0.11, 0.72, 1200, 600, 840, 260
)
evaluation_metrics_binary_df = pd.DataFrame(evaluation_metrics_binary, index=[0])
base_evaluation_metrics_binary_df = evaluation_metrics_binary_df[
    ["accuracy", "precision", "recall", "f1"]
]
# Conf matrix
first_part = [
    evaluation_metrics_binary["true_positive"],
    evaluation_metrics_binary["false_positive"],
]
second_part = [
    evaluation_metrics_binary["false_negative"],
    evaluation_metrics_binary["true_negative"],
]
cm = np.array([first_part, second_part])

# f = open("whitebox/streamlit/mock/drift.json")
# drift = json.load(f)
# f.close()

# f = open("whitebox/streamlit/mock/performance.json")
# perf = json.load(f)
# f.close()

# f = open("whitebox/streamlit/mock/inferences.json")
# inf = json.load(f)
# f.close()

# f = open("whitebox/streamlit/mock/monitors.json")
# mon = json.load(f)
# f.close()

# f = open("whitebox/streamlit/mock/alerts.json")
# al = json.load(f)
# f.close()


# -----------------------------------
overview, performance, drifting, inferences, monitors, alerts = st.tabs(
    ["Overview", "Performance", "Drifting", "Inferences", "Monitors", "Alerts"]
)

model_option, button = create_sidebar(model_names)
model = get_model_from_name(models_list, model_option)
pred_column = model["prediction"]
model_id = model["id"]

inf = wb.get_inferences(model_id)
perf = wb.get_performance_metrics(model_id)
drift = wb.get_drifting_metrics(model_id)
mon = wb.get_monitors(model_id)
al = wb.get_alerts(model_id)

if button:
    with overview:
        create_overview_tab(model, cm, base_evaluation_metrics_binary_df)

    with performance:
        create_performance_tab(perf, model)

    with drifting:
        create_drift_tab(drift)

    with inferences:
        create_inferences_tab(inf, pred_column)

    with monitors:
        create_monitors_tab(mon, al)

    with alerts:
        create_alerts_tab(al, mon)
