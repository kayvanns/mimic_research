import pandas as pd
import matplotlib.pyplot as plt

def read(path, name, usecols=None):
    print(f"Loading {name}...")
    return pd.read_csv(
        f"{path}/{name}.csv.gz",
        usecols=usecols
    )

path_hosp = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/hosp"
path_icu = "/Users/kayvans/Documents/mimic/mimic-iv-3.1/icu"

patients = read(path_hosp, "patients", ["subject_id", "gender", "anchor_age", "anchor_year", "anchor_year_group"])
admissions = read(path_hosp, "admissions", ["subject_id", "hadm_id", "admittime", "dischtime", "race","hospital_expire_flag"])
icu = read(path_icu, "icustays", ['subject_id', 'hadm_id', 'stay_id', 'intime', 'outtime'])
diagnoses = read(path_hosp, "diagnoses_icd", ["subject_id", "hadm_id", "icd_code", "icd_version","seq_num"])  
d_diagnoses = read(path_hosp, "d_icd_diagnoses", ["icd_code", "long_title"])

admissions["admittime"] = pd.to_datetime(admissions["admittime"])
admissions["dischtime"] = pd.to_datetime(admissions["dischtime"])
icu["intime"] = pd.to_datetime(icu["intime"])
icu["outtime"] = pd.to_datetime(icu["outtime"]) 


admissions["year"] = admissions["admittime"].dt.year
admissions_per_year = admissions.groupby("year")["hadm_id"].nunique()

overall_mortality_rate= ((admissions["hospital_expire_flag"] == 1).astype(int)).mean()
icu_mortality = admissions[admissions["hadm_id"].isin(icu["hadm_id"])]["hospital_expire_flag"].mean()
mortality_per_year = admissions.groupby("year")["hospital_expire_flag"].mean()

icu["icu_los"] = (icu["outtime"] - icu["intime"]).dt.total_seconds() / (24*3600)
icu_los_per_hadm = icu.groupby("hadm_id")["icu_los"].sum()
admissions["hosp_length"] = (admissions["dischtime"]-admissions["admittime"]).dt.total_seconds() / (24*3600)

p_diagnoses = diagnoses[diagnoses["seq_num"]==1]
p_diagnoses = p_diagnoses.merge(d_diagnoses, on="icd_code", how="left")
top_primary = (p_diagnoses["long_title"].value_counts().head(10))

print("Unique Patients:", patients["subject_id"].nunique())
print("Unique Hospitalizations:", admissions["hadm_id"].nunique())
print("Unique ICU Stays:", icu["stay_id"].nunique())
print("Hospitalizations with ICU Stay:", icu["hadm_id"].nunique())
print("Overall Mortality:", overall_mortality_rate)
print("ICU Mortality:", icu_mortality)
print("Top Primary Diagnoses:\n", top_primary)

fig,(ax1,ax2,ax3,ax4)=plt.subplots(ncols=4,figsize=(24,5))
admissions_per_year.plot(ax=ax1)
ax1.set_title("Number of Admissions per Year")
ax1.set_xlabel("Year")
ax1.set_ylabel("Number of Admissions")
mortality_per_year.plot(ax=ax2)
ax2.set_title("Hospital Mortality Rate per Year")
ax2.set_xlabel("Year")
ax2.set_ylabel("Mortality Rate")
icu_los_per_hadm.plot.hist( bins=50, ax=ax3)
ax3.set_title("ICU Length of Stay per Hospitalization")
ax3.set_xlabel("ICU Length of Stay (days)")
ax3.set_ylabel("Frequency")
admissions["hosp_length"].plot.hist(bins=50,ax=ax4)
ax4.set_title("Hospital Length of Stay")
ax4.set_xlabel("Hospital Length of Stay (days)")
ax4.set_ylabel("Frequency") 
plt.tight_layout()
fig.savefig("graphs/mimic_challenges.png")