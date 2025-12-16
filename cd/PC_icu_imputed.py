import pandas as pd
from causallearn.search.ConstraintBased.PC import pc
from causallearn.graph.GraphClass import CausalGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.utils.PCUtils.BackgroundKnowledge import BackgroundKnowledge
from causallearn.utils.GraphUtils import GraphUtils


df = pd.read_csv("/Users/kayvans/Documents/mimic/icu_data.csv")

categorical_cols= ['gender', 'race']

binary_cols = ['sepsis', 'septic_shock', 'hospital_expire_flag','arf','antibiotics_given','vaso_given']
df["race"] = df["race"]=="WHITE"

for col in categorical_cols:
    df[col] = df[col].astype('category').cat.codes
for col in binary_cols:
    df[col] = df[col].astype('int')
core_cols = ['hospital_expire_flag','antibiotics_given', 'vaso_given','creatinine_admission_max', 'bun_admission_max', 'blood_pressure_min','lactate_max','platelet_max','temperature_max_F','gsc_motor_min','gsc_verbal_min','gsc_eye_min','pH_min','wbc_max','anchor_age','gender', 'septic_shock', 'sepsis', 'arf','race']
data = df[core_cols].to_numpy()
print(df[core_cols])
cg = pc(data, indep_test='fisherz')
nodes = cg.G.get_nodes()
bk = BackgroundKnowledge()
for i in range(len(nodes)):
    bk.add_forbidden_by_node(nodes[0], nodes[i])
bk.add_forbidden_by_node(nodes[16], nodes[17])

cg_with_background_knowledge = pc(data,indep_test='fisherz', background_knowledge=bk)
cg_with_background_knowledge.draw_pydot_graph(labels=core_cols)
pyd = GraphUtils.to_pydot(cg_with_background_knowledge.G,labels=core_cols) 
pyd.write_png("graphs/cd_knn_icu_2.png")
# # df[core_cols].to_csv("data_processed3.csv", index=False)
