import pandas as pd
import cleaning

USECOLS = {
    "patients": ["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group"],
    "admissions": ["subject_id", "hadm_id", "admittime", "dischtime", "race", "hospital_expire_flag"],
    "labevents": ["subject_id","hadm_id","itemid","charttime","valuenum"],
    "d_labitems": ["itemid","label"],
    "pharmacy": ["subject_id","hadm_id","medication","starttime"],
    "diagnoses_icd": ["subject_id","hadm_id","icd_code","icd_version","seq_num"],
    "d_icd_diagnoses": ["icd_code","long_title"],
    "procedures_icd": ["subject_id","hadm_id","icd_code","icd_version"],
    "d_icd_procedures": ["icd_code","icd_version","long_title"],
    "omr": ["subject_id","result_name","result_value","chartdate"],
    "icustays": ["subject_id","hadm_id","stay_id","intime","outtime"],
    "chartevents": ["subject_id","hadm_id","itemid","charttime","valuenum"],
    "d_items": ["itemid","label","category"]
}
def load_all():
    path_hosp = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/hosp"
    path_icu  = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/icu"

    def read(path, name):
        print(f"Loading {name}...")
        return pd.read_csv(
            f"{path}/{name}.csv.gz",
            usecols=USECOLS.get(name)
    )

    patients     = read(path_hosp, "patients")
    admissions   = read(path_hosp, "admissions")
    labs         = read(path_hosp, "labevents")
    d_labitems   = read(path_hosp, "d_labitems")
    pharmacy     = read(path_hosp, "pharmacy")
    diagnoses    = read(path_hosp, "diagnoses_icd")
    d_diagnoses  = read(path_hosp, "d_icd_diagnoses")
    procedures   = read(path_hosp, "procedures_icd")
    d_procedures = read(path_hosp, "d_icd_procedures")
    omr          = read(path_hosp, "omr")
    icustays       = read(path_icu, "icustays")
    chartevents    = read(path_icu, "chartevents")
    d_items        = read(path_icu, "d_items")

    p_diagnoses = diagnoses[diagnoses["seq_num"]==1]
    p_diagnoses = p_diagnoses.merge(d_diagnoses, on="icd_code", how="left")

    matched_titles = p_diagnoses[p_diagnoses["long_title"].str.contains("Urinary tract infection", case=False,na=False)].copy()
    patients_info = patients[patients["subject_id"].isin(matched_titles["subject_id"])].copy().reset_index(drop=True)
    admissions_info = admissions[admissions["hadm_id"].isin(matched_titles["hadm_id"])].copy().reset_index(drop=True)
    df = patients_info.merge(admissions_info,on="subject_id")
    vitals = {"heart_rate_max":{'itemid':220045, 'agg':'max'}, "blood_pressure_min":{'itemid':220181,"agg":'min'},"spO2_min":{'itemid':220277,'agg':'min'},"FiO2_max":{'itemid':223835, 'agg':'max'},"temperature_max_C":{'itemid':223762, 'agg':'max'},"temperature_max_F":{'itemid':223761,'agg':'max'},"gsc_motor_min":{'itemid':223901,'agg':'min'},"gsc_verbal_min":{'itemid':223900,'agg':'min'},"gsc_eye_min":{'itemid':220739,'agg':'min'}}
    labevents = {"sodium_max":{'itemid':[50983,52623],'agg':'max'}, "sodium_min":{'itemid':[50983,52623],'agg':'min'},"potassium_max":{'itemid':[52610,50971],'agg':'max'},"bun_max":{'itemid':[51006,52647], 'agg':'max'},"creatinine_max":{'itemid':[50912,52546],'agg':'max'},"glucose_min":{'itemid':[50931,52569],'agg':'min'},"pH_min":{'itemid':[50820],'agg':'min'},"lactate_max":{'itemid':[50813, 52442, 53154],'agg':'max'}, "platelet_max":{'itemid':[51704,51265],'agg':'max'},"wbc_max":{'itemid':[51301, 51755, 51756],'agg':'max'},"hemoglobin_min":{'itemid':[50811, 51222, 51640],'agg':'min'},"ast_max":{'itemid':[53088,50878],'agg':'max'},"alt_max":{'itemid':[50861],'agg':'max'},"bilirubin_max":{'itemid':[50885,53089],'agg':'max'},"inr_max":{'itemid':[51675,51237],'agg':'max'}}
    df = df.merge(icustays,on=["hadm_id","subject_id"],how="left")
    df["outtime"]= pd.to_datetime(df["outtime"])
    df["intime"]=pd.to_datetime(df["intime"])
    df["ICU_length"] = (df["outtime"] - df["intime"]).dt.total_seconds() / (24*3600)
    df["admittime"] =pd.to_datetime(df["admittime"])
    df["dischtime"] = pd.to_datetime(df["dischtime"])
    df["Hospital_length"] = (df["dischtime"]-df["admittime"]).dt.total_seconds() / (24*3600)
    return df, chartevents, labs, pharmacy, diagnoses
