# Importing dependencies
import pandas as pd
import numpy as np
import pickle

# Creating required pandas dataframes
df_gen_raw = pd.read_csv('Data/ieee24rts_generators.csv', index_col=False)
df_line_raw = pd.read_csv('Data/ieee24rts_lines.csv', index_col=False)
df_load_raw = pd.read_csv('Data/ieee24rts_loads.csv', index_col=False)
df_aggr_raw = pd.read_csv('Data/ieee24rts_aggrs.csv', index_col=False)
df_aggr_final = pd.read_csv('Data/ieee24rts_aggregators.csv', index_col=False)
df_aggr_final["Bus"] = df_aggr_raw["Bus"]
df_aggr_final.insert(0, "Bus", df_aggr_final.pop("Bus"))
df_bus_raw = pd.read_csv('Data/ieee24rts_buses.csv', index_col=False)

set_names = ['B', 'G', 'A', 'L', 'GB']

param_names_gen = ['ag', 'bg', 'cg', 'p_g_max', 'p_g_min', 'q_g_max', 'q_g_min']
param_names_gen_col_names = ['a', 'b', 'c', 'Pmax', 'Pmin', 'Qmax', 'Qmin']  # DataFrame column names

param_names_line = ['gg', 'bb', 'sl']
param_names_line_col_names = ['gg', 'bb', 'Smax']

param_names_aggr = ['gamma', 'mu', 'sigma', 'p_a_max', 'p_a_min', 'q_a_max', 'q_a_min']
param_names_aggr_col_names = ['Gamma', 'Mu', 'Sigma', 'Pmax', 'Pmin', 'Qmax', 'Qmin']

param_names_genbus = ['vg']
param_names_genbus_col_names = ['Vg']  # This is needed for usual power flow analysis. Not necessary for OPF.

# All parameter names in a single list
dict_names = sum([param_names_gen, param_names_line, param_names_aggr, param_names_genbus], [])



# Set creation B, G, A, L, GB
B = []
for i in range(1, 25):  # 24 bus system
    B.append(i)

G = []
for i in df_gen_raw.index:
    gen = (df_gen_raw.loc[i, 'Bus'], df_gen_raw.loc[i, 'Generator'])
    G.append(gen)

A = []
for i in df_aggr_final.index:
    agg = (df_aggr_final.loc[i, 'Bus'], df_aggr_final.loc[i, 'Aggregator'])
    A.append(agg)

# Including double-circuit lines. May be identified by as duplicates, hence be dropped by sets and other issues.
L = []
for i in df_line_raw.index:
    line = (df_line_raw.loc[i, 'From'], df_line_raw.loc[i, 'To'])
    L.append(line)

# Generator Buses
df_genbus = df_gen_raw.drop_duplicates(subset=['Bus']).reset_index(drop=True)

GB = []
for i in df_genbus.index:
    bus = df_genbus.loc[i, 'Bus']
    GB.append(bus)

double_lines = []
for line in L:  # Combining double-circuit lines for analyses
    if L.count(line) != 1:
        double_lines.append(line)
double_lines = list(set(double_lines))

L = list(dict.fromkeys(L))  # Dropping duplicates corresponding to double-circuits

indexset = [B, G, A, L, GB]

cplx = 1j  # Sqrt of 1
admittance = np.divide(1, (df_line_raw['r'] + df_line_raw['x']*cplx))
df_line_raw['gg'] = -np.real(admittance)
df_line_raw['bb'] = -np.imag(admittance)

for i in df_line_raw.index:  # Combining double-circuit lines to single lines
    for double_line in double_lines:
        if (double_line[0] == df_line_raw.loc[i, 'From']) and (double_line[1] == df_line_raw.loc[i, 'To']):
            df_line_raw.loc[i, 'r'] = 0.5*df_line_raw.loc[i, 'r']
            df_line_raw.loc[i, 'x'] = 0.5*df_line_raw.loc[i, 'x']
            df_line_raw.loc[i, 'Smax'] = 2*df_line_raw.loc[i, 'Smax']
            df_line_raw.loc[i, 'gg'] = 2*df_line_raw.loc[i, 'gg']
            df_line_raw.loc[i, 'bb'] = 2*df_line_raw.loc[i, 'bb']

df_line_raw = df_line_raw.drop_duplicates()  # Dropping duplicate rows

# Dealing with the leakage conductances and leakage susceptances. i.e., gg[i, i] and bb[i, i]
df_self_conductance = df_line_raw.groupby("From")['gg'].sum().reset_index()

dictselfgg = dict()
for index, row in df_self_conductance.iterrows():
    dictselfgg[int(row['From'])] = -row['gg']

df_self_conductance = df_line_raw.groupby("To")['gg'].sum().reset_index()

for index, row in df_self_conductance.iterrows():
    key = row['To']
    value = -row['gg']

    if key not in dictselfgg:
        dictselfgg[key] = value
    else:
        dictselfgg[key] += value

df_self_susceptance = df_line_raw.groupby("From")['bb'].sum().reset_index()

dictselfbb = dict()
for index, row in df_self_susceptance.iterrows():
    dictselfbb[int(row['From'])] = -row['bb']

df_self_susceptance = df_line_raw.groupby("To")['bb'].sum().reset_index()

for index, row in df_self_susceptance.iterrows():
    key = row['To']
    value = -row['bb']

    if key not in dictselfbb:
        dictselfbb[key] = value
    else:
        dictselfbb[key] += value

# Adding leakage conductance and susceptance values to G(i,i) and B(i,i) elements
for index, row in df_bus_raw.iterrows():
    for key in dictselfgg:
        if row['Bus'] == key:
            dictselfgg[key] += row['Gs']
            dictselfbb[key] += row['Bs']

# Final G(i,i) and B(i,i)
selfgg = {(key, key): value for key, value in dictselfgg.items()}
selfbb = {(key, key): value for key, value in dictselfbb.items()}

def dict_gen(df, firstindex, secondindex, paramname):  # Creating dict-like structures to hold parameters
    return df.pivot_table(index=firstindex, columns=secondindex, values=paramname).stack().to_dict()


def pickle_gen(paramname, param):  # Exporting sets and dictionaries as pickle files (.pkl)
    with open('Data/Parameters/' + paramname + '.pkl', 'wb') as filepush:
        pickle.dump(param, filepush)


# Lists of dictionaries
dicts_gen = [dict_gen(df_gen_raw, 'Bus', 'Generator', paramname)
             for paramname in param_names_gen_col_names]

dicts_line = [dict_gen(df_line_raw, 'From', 'To', paramname)
              for paramname in param_names_line_col_names]

dicts_aggr = [dict_gen(df_aggr_final, 'Bus', "Aggregator", paramname)
              for paramname in param_names_aggr_col_names]

dicts_genbus = [{df_genbus.loc[i, 'Bus'] : df_genbus.loc[i, 'Vg'] for i in range(len(df_genbus['Bus']))}]

# Concatenating all lists into one
dicts = sum([dicts_gen, dicts_line, dicts_aggr, dicts_genbus], [])

# Exporting sets (index)
for i in range(len(set_names)):
    pickle_gen(set_names[i], indexset[i])

# Exporting dictionaries
for i in range(len(dict_names)):
    pickle_gen(dict_names[i], dicts[i])

# Importing conductance and susceptance dictionaries, in which the diagonal elements were missing.
with open('Data/Parameters/gg.pkl', 'rb') as f:
    gg_old = pickle.load(f)

with open('Data/Parameters/bb.pkl', 'rb') as f:
    bb_old = pickle.load(f)

gg_old.update(selfgg)
bb_old.update(selfbb)
gg_new = dict(sorted(gg_old.items()))
bb_new = dict(sorted(bb_old.items()))

# Set of Admittances
Y = list(gg_new.keys())

# Exporting final conductance and susceptance dictionaries, along with the set of admittances
with open('Data/Parameters/gg.pkl', 'wb') as f:
    pickle.dump(gg_new, f)

with open('Data/Parameters/bb.pkl', 'wb') as f:
    pickle.dump(bb_new, f)

with open('Data/Parameters/Y.pkl', 'wb') as f:
    pickle.dump(Y, f)




# Optional Code for Aggregator Data Synthesis
# Synthesizing Aggregator Load Proportions
'''
# This is a multiline comment. Uncomment if necessary
aggr_prop = []
for i in df_load_raw.index:
    temp = []
    for j in range(0, df_load_raw.loc[i, 'Aggr']):
        if j != df_load_raw.loc[i, 'Aggr'] - 1:
            temp.append(np.random.uniform(0.2,0.45))
        else:
            temp.append(1-sum(temp))
    aggr_prop.append(temp)
aggr_prop = [i for aggr in aggr_prop for i in aggr]
df_aggr_raw["Pnom"] = np.ceil(aggr_prop*df_aggr_raw["P"]).astype(int)
df_aggr_raw["Qnom"] = np.ceil(aggr_prop*df_aggr_raw["Q"]).astype(int)
df_aggr_raw.drop(['P', 'Q'], axis=1, inplace=True)
# Setting critical load and normal operation load for aggregators
df_aggr_raw["Pmax"] = np.ceil(1.15*df_aggr_raw["Pnom"]).astype(int)
df_aggr_raw["Pmin"] = np.floor(.7*df_aggr_raw["Pnom"]).astype(int)
df_aggr_raw["Qmax"] = np.ceil(1.15*df_aggr_raw["Qnom"]).astype(int)
df_aggr_raw["Qmin"] = np.floor(0.7*df_aggr_raw["Qnom"]).astype(int)
df_aggr_raw.drop(["Pnom", "Qnom"], axis=1, inplace=True)
df_aggr_raw.to_csv('Data/aggr_raw_limits.csv', index=False)
'''
# Synthesizing Socioeconomic Scores of Aggregators
'''
# This is a multiline comment. Uncomment if necessary
df_aggr_raw = pd.read_csv('Data/aggr_raw_limits.csv', index_col=0)
df_aggr_raw
randses = np.random.randint(10, 110, size=len(df_aggr_raw["Mu"]), dtype=int)
randses
df_aggr_raw["Sigma"] = randses
df_aggr_raw.to_csv('Data/ieee24rts_aggregators.csv', index=False)
'''
