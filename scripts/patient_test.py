import pandas as pd 
import matplotlib.pyplot as plt
icd_codes_septic_shock = ["R6521","78552"]
vitals_dict = {
    "heart_rate":        {"itemid": [220045]},          
    "blood_pressure":{"itemid": [220181]},          
}

labs_dict = {
    "pH":          {"itemid": [50820]},
    "lactate":     {"itemid": [50813, 52442, 53154]},
    "bun":         {"itemid": [51006, 52647]},
    "creatinine":  {"itemid": [50912, 52546]},
    "hemoglobin":  {"itemid": [50811, 51222, 51640]},
    "platelets":   {"itemid": [51704, 51265]},
}
USECOLS = {
    "patients": ["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group"],
    "admissions": ["subject_id", "hadm_id", "admittime", "dischtime", "race", "hospital_expire_flag"],
    "labevents": ["subject_id","hadm_id","itemid","charttime","valuenum"],
    "d_labitems": ["itemid","label"],
    "diagnoses_icd": ["subject_id","hadm_id","icd_code","icd_version","seq_num"],
    "d_icd_diagnoses": ["icd_code","long_title"],
    "icustays": ["subject_id","hadm_id","stay_id","intime","outtime"],
    "chartevents": ["subject_id","hadm_id","itemid","charttime","valuenum"],
    "d_items": ["itemid","label","category"]
}

path_hosp = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/hosp"
path_icu  = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/icu"

def load_data():
    def read(path, name):
        print(f"Loading {name}...")
        return pd.read_csv(
            f"{path}/{name}.csv.gz",
            usecols=USECOLS.get(name))
        
    

    patients     = read(path_hosp, "patients")
    admissions   = read(path_hosp, "admissions")
    labs         = read(path_hosp, "labevents")
    d_labitems   = read(path_hosp, "d_labitems")
    diagnoses    = read(path_hosp, "diagnoses_icd")
    d_diagnoses  = read(path_hosp, "d_icd_diagnoses")
    icustays       = read(path_icu, "icustays")
    chartevents    = read(path_icu, "chartevents")
    d_items        = read(path_icu, "d_items")
    

    septic_diagnoses = diagnoses[diagnoses["icd_code"].isin(icd_codes_septic_shock)]
    septic_hadm = septic_diagnoses["hadm_id"].unique()
    septic_admissions = admissions[admissions["hadm_id"].isin(septic_hadm)& (admissions["hospital_expire_flag"]==0)]
    admission = septic_admissions.iloc[0]
    patient = admission["subject_id"]
    hosp = admission["hadm_id"]
    hosp_chartevents = chartevents[chartevents["hadm_id"]==hosp].copy()
    hosp_labs = labs[labs["hadm_id"]==hosp].copy()
    for df in [hosp_chartevents, hosp_labs]:
        df["charttime"] = pd.to_datetime(df["charttime"], errors="coerce")

    return patient,hosp,hosp_chartevents,hosp_labs

def extract_vitals(chartevents, vitals_dict):
    out = {}
    for name, spec in vitals_dict.items():
        ids = spec["itemid"]
        df = chartevents[chartevents["itemid"].isin(ids)][["charttime", "valuenum"]].copy()
        df = df.dropna().sort_values("charttime")
        out[name] = df
    return out
def extract_labs(labs, labs_dict):
    out = {}
    for name, spec in labs_dict.items():
        ids = spec["itemid"]
        df = labs[labs["itemid"].isin(ids)][["charttime", "valuenum"]].copy()
        df = df.dropna().sort_values("charttime")
        out[name] = df
    return out

def plot_timeseries(vitals, labs):
    fig, axes = plt.subplots(len(vitals)+len(labs),1, figsize=(10,15), sharex=True)
    i = 0
    for name, df in vitals.items():
        axes[i].plot(df["charttime"], df["valuenum"], marker="o", linestyle="-")
        axes[i].set_title(name)
        i += 1
    for name, df in labs.items():
        axes[i].plot(df["charttime"], df["valuenum"], marker="o", linestyle="-")
        axes[i].set_title(name)
        i += 1
    plt.xlabel("Time")
    plt.tight_layout()
    plt.show()