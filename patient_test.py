import pandas as pd 
import matplotlib.pyplot as plt
icd_codes_septic_shock = ["R6521","78552"]
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
    return patients, admissions, labs, d_labitems, diagnoses, d_diagnoses, icustays, chartevents, d_items

septic_diagnoses = diagnoses[diagnoses["icd_code"].isin(icd_codes_septic_shock)]
septic_hadm = septic_diagnoses["hadm_id"].unique()
septic_admissions = admissions[admissions["hadm_id"].isin(septic_hadm)& (admissions["hospital_expire_flag"]==1)]
admission = septic_admissions.iloc[0,:]
patient = admission["subject_id"]
hosp = admission["hadm_id"]
hosp_chartevents = chartevents[chartevents["hadm_id"]==hosp]
hosp_labs = labs[labs["hadm_id"]==hosp]