
import pandas as pd
from causallearn.search.ConstraintBased.PC import pc
from causallearn.graph.GraphClass import CausalGraph
from causallearn.graph.GraphNode import GraphNode
from causallearn.utils.PCUtils.BackgroundKnowledge import BackgroundKnowledge
from causallearn.utils.GraphUtils import GraphUtils
from sklearn.impute import SimpleImputer


df = pd.read_csv("/Users/kayvans/Documents/mimic/draft.csv")


categorical_cols= ['gender', 'race']

binary_cols = ['sepsis', 'septic_shock', 'hospital_expire_flag','arf','antibiotics_given','vaso_given']
df["race"] = df["race"]=="WHITE"

for col in categorical_cols:
    df[col] = df[col].astype('category').cat.codes
for col in binary_cols:
    df[col] = df[col].astype('int')
core_cols = ['antibiotics_given', 'vaso_given','creatinine_admission_max', 'bun_admission_max', 'blood_pressure_min','lactate_max','anchor_age','gender','hospital_expire_flag', 'septic_shock', 'sepsis', 'arf','race']
data = df[core_cols].to_numpy()

cg = pc(data, indep_test='mv_fisherz', mvpc=True)
nodes = cg.G.get_nodes()
bk = BackgroundKnowledge()
for i in range(len(nodes)):
    bk.add_forbidden_by_node(nodes[8], nodes[i])
bk.add_forbidden_by_node(nodes[9], nodes[10])

cg_with_background_knowledge = pc(data,indep_test="mv_fisherz",mvpc=True, background_knowledge=bk)
cg_with_background_knowledge.draw_pydot_graph(labels=core_cols)
pyd = GraphUtils.to_pydot(cg_with_background_knowledge.G,labels=core_cols) 
pyd.write_png("graphs/cd_race_binary.png")
# df[core_cols].to_csv("data_processed3.csv", index=False)
