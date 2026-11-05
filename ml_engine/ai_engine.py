"""Self-contained ML engine for MediScan AI.

The included benchmark dataset is synthetic and is intended for software/academic
 demonstration only. It is NOT a clinically validated diagnostic model.
"""
from pathlib import Path
import json
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.svm import SVC
from sklearn.inspection import permutation_importance

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "ml_engine" / "artifacts"
ART.mkdir(parents=True, exist_ok=True)

FEATURES = [
    "Hemoglobin","WBC","RBC","Platelets","Hematocrit","MCV","MCH","MCHC","RDW",
    "Fasting Glucose","HbA1c","Total Cholesterol","Triglycerides","HDL","LDL",
    "Creatinine","Blood Urea","eGFR","TSH","T3","T4"
]

RANGES = {
    "Hemoglobin":(12,15),"WBC":(4000,11000),"RBC":(4.2,5.4),"Platelets":(150000,450000),
    "Hematocrit":(36,46),"MCV":(80,100),"MCH":(27,33),"MCHC":(32,36),"RDW":(11.5,14.5),
    "Fasting Glucose":(70,99),"HbA1c":(4,5.6),"Total Cholesterol":(125,200),"Triglycerides":(0,150),
    "HDL":(40,60),"LDL":(0,100),"Creatinine":(.6,1.2),"Blood Urea":(7,20),"eGFR":(90,120),
    "TSH":(.4,4),"T3":(80,200),"T4":(5,12)
}


def _deviation(v, lo, hi):
    if v is None or pd.isna(v): return 0.0
    span = max(hi-lo, 1e-9)
    if v < lo: return (v-lo)/span
    if v > hi: return (v-hi)/span
    return 0.0


def feature_frame(extracted):
    row = {f: 0.0 for f in FEATURES}
    for item in extracted or []:
        p = item.get("Parameter")
        if p not in RANGES:
            continue
        # Prefer the reference interval extracted from the uploaded report.
        # This matters when a laboratory uses units/ranges different from the
        # project's generic benchmark ranges (for example T3).
        lo = item.get("Min", RANGES[p][0])
        hi = item.get("Max", RANGES[p][1])
        try:
            lo, hi = float(lo), float(hi)
            row[p] = _deviation(float(item["Value"]), lo, hi)
        except (TypeError, ValueError):
            row[p] = 0.0
    return pd.DataFrame([row], columns=FEATURES)


def _synthetic(n=1800, seed=42):
    rng = np.random.default_rng(seed)
    rows=[]; labels=[]
    for _ in range(n):
        x={f:0.0 for f in FEATURES}
        label="Normal Pattern"
        u=rng.random()
        if u<.18: # anemia-like
            label="Anemia-like Pattern"; x["Hemoglobin"]=rng.uniform(-1.0,-.25); x["MCV"]=rng.uniform(-.9,.15); x["MCH"]=rng.uniform(-.9,.1); x["Hematocrit"]=rng.uniform(-.8,-.15)
        elif u<.33: # infection-like
            label="Inflammatory Pattern"; x["WBC"]=rng.uniform(.2,1.4)
        elif u<.48: # metabolic
            label="Metabolic Pattern"; x["Fasting Glucose"]=rng.uniform(.15,2.2); x["HbA1c"]=rng.uniform(.2,1.8)
        elif u<.63: # lipid
            label="Lipid Pattern"; x["LDL"]=rng.uniform(.15,2.0); x["Total Cholesterol"]=rng.uniform(.15,1.7); x["Triglycerides"]=rng.uniform(.1,1.8); x["HDL"]=rng.uniform(-.8,-.05)
        elif u<.78: # renal
            label="Renal Pattern"; x["Creatinine"]=rng.uniform(.2,2.0); x["Blood Urea"]=rng.uniform(.2,2.0); x["eGFR"]=rng.uniform(-2.0,-.15)
        elif u<.90: # thyroid
            label="Thyroid Pattern"; x["TSH"]=rng.choice([rng.uniform(.2,2.0),rng.uniform(-1.0,-.1)]); x["T4"]=rng.uniform(-.8,.8)
        # noise on all features
        for f in FEATURES:
            if x[f]==0: x[f]=rng.normal(0,.035)
            else: x[f]+=rng.normal(0,.06)
        rows.append(x); labels.append(label)
    return pd.DataFrame(rows), pd.Series(labels, name="label")


def train_models(force=False):
    model_file=ART/"models.json"
    if model_file.exists() and not force:
        return load_models()
    X,y=_synthetic()
    Xtr,Xte,ytr,yte=train_test_split(X,y,test_size=.25,random_state=42,stratify=y)
    models={
        "Logistic Regression":Pipeline([("scale",StandardScaler()),("model",LogisticRegression(max_iter=1200))]),
        "SVM":Pipeline([("scale",StandardScaler()),("model",SVC(probability=True,random_state=42))]),
        "Random Forest":RandomForestClassifier(n_estimators=220,random_state=42,n_jobs=-1,max_depth=12)
    }
    results={}; trained={}
    for name,m in models.items():
        m.fit(Xtr,ytr); pred=m.predict(Xte)
        pr,re,f1,_=precision_recall_fscore_support(yte,pred,average="weighted",zero_division=0)
        results[name]={"accuracy":float(accuracy_score(yte,pred)),"precision":float(pr),"recall":float(re),"f1":float(f1),"classes":sorted(y.unique().tolist()),"confusion_matrix":confusion_matrix(yte,pred,labels=sorted(y.unique())).tolist()}
        trained[name]=m
    # save lightweight metadata; models are retrained on demand to avoid pickle/version issues
    model_file.write_text(json.dumps(results,indent=2),encoding="utf-8")
    return trained,results


def load_models():
    # Always retrain in-memory; fast enough and avoids sklearn pickle incompatibility.
    return train_models(force=True)


def predict(extracted):
    models, results = train_models()
    X=feature_frame(extracted)
    preds=[]
    for name,m in models.items():
        pred=m.predict(X)[0]
        prob=float(np.max(m.predict_proba(X)[0])) if hasattr(m,"predict_proba") else 0.0
        preds.append((name,pred,prob))
    # ensemble = majority vote, confidence = mean model confidence for chosen label
    labels=[p[1] for p in preds]; chosen=max(set(labels),key=labels.count)
    conf=float(np.mean([p[2] for p in preds if p[1]==chosen])) if any(p[1]==chosen for p in preds) else 0.0
    return chosen,conf,preds,results


def explain(extracted, chosen):
    X=feature_frame(extracted)
    nonzero=[]
    for f,v in X.iloc[0].items():
        if abs(v)>0.08: nonzero.append((f,abs(v),v))
    nonzero.sort(key=lambda z:z[1],reverse=True)
    return nonzero[:8]


def evaluation_table(results):
    return pd.DataFrame([{"Model":k,"Accuracy":v["accuracy"],"Precision":v["precision"],"Recall":v["recall"],"F1":v["f1"]} for k,v in results.items()])
