# Creating Instance for the Abstract Model
import pickle


# Loading data stored in .pkl files
def load_sets_params(filename):
    with open('Data/Parameters/' + filename + '.pkl', 'rb') as f:
        pkl_data = pickle.load(f)
    return pkl_data


# Names of sets and parameters
set_names = ['B', 'G', 'L', 'A', 'Y']
param_names = ['gamma', 'mu', 'sigma',
               'ag', 'bg', 'cg',
               'gg', 'bb', 'sl',
               'p_g_max', 'p_g_min', 'q_g_max', 'q_g_min',
               'p_a_max', 'p_a_min', 'q_a_max', 'q_a_min']
# The set 'GB' and corresponding parameters 'vg' is neglected since those are unnecessary for OPF.

# Loading data stored in Data/Parameters
sets = [load_sets_params(s) for s in set_names]
params = [load_sets_params(p) for p in param_names]


# Function to create the instance for the abstract model
def create_data_instance_sets(data_instance, values, names):
    for value, name in zip(values, names):
        data_instance[None][name] = {None: list(value) if len(value) > 1 else list(name)[0]}


def create_data_instance_params(data_instance, values, names):
    for value, name in zip(values, names):
        data_instance[None][name] = value


# Creating the Data Instance
instance_data_24 = {None: {}}  # Initializing a data dictionary as per Pyomo requirements
create_data_instance_sets(instance_data_24, sets, set_names)
create_data_instance_params(instance_data_24, params, param_names)

with open('Data/Instance/instance_data_24.pkl', 'wb') as file:  # Exporting the data structure for external reference
    pickle.dump(instance_data_24, file)

# IEEE 5-bus Modified System Data
instance_data_5 = {None: {
    'B': {None: [1,2,3,4,5]},
    'G': {None: [(1,1), (1,2), (3,1), (4,1), (5,1)]},
    'A': {None: [(2,1), (2,2), (3,1), (3,2), (4,1), (4,2), (4,3)]},
    'L': {None: [(1,2), (1,4), (1,5), (2,3), (3,4), (4,5)]},
    'Y': {None: [(1,1), (1,2), (1,4), (1,5), (2,2), (2,3), (3,3), (3,4), (4,4), (4,5), (5,5)]},
    'gamma': {(2,1):11.05, (2,2):38.68, (3,1):63.54, (3,2):45.34, (4,1):29.99, (4,2):21.23, (4,3):55.71},
    'mu': {(2,1):0.016, (2,2):0.045, (3,1):0.066, (3,2):0.034, (4,1):0.089, (4,2):0.024, (4,3):0.087},
    'sigma': {(2,1):15, (2,2):85, (3,1):56, (3,2):32, (4,1):100 , (4,2):77, (4,3):105},
    'ag': {(1,1):2, (1,2):2, (3,1):2, (4,1):2, (5,1):2},
    'bg': {(1,1):14, (1,2):15, (3,1):30, (4,1):40, (5,1):10},
    'cg': {(1,1):60, (1,2):35, (3,1):25, (4,1):20, (5,1):50},
    'gg': {(1,1):22.25068569, (1,2):-3.523484021, (1,4):-3.256904638, (1,5):-15.47029703, (2,2):12.69106745,
           (2,3):-9.167583425, (3,3):12.50125013, (3,4):-3.3336667, (4,4):9.924238038, (4,5):-3.3336667,
           (5,5):18.80396373},
    'bb': {(1,1):-222.5068569, (1,2):35.23484021, (1,4):32.56904638, (1,5):154.7029703, (2,2):-126.9106745,
           (2,3):91.67583425, (3,3):-125.0125013, (3,4):33.336667, (4,4):-99.24238038, (4,5):33.336667,
           (5,5):-188.0396373},
    'sl': {(1,2):200, (1,4):100, (1,5):120, (2,3):100, (3,4):150, (4,5):120},
    'p_g_max': {(1,1):40, (1,2):170, (3,1):520, (4,1):200, (5,1):600},
    'p_g_min': {(1,1):0, (1,2):0, (3,1):0, (4,1):0, (5,1):0},
    'q_g_max': {(1,1):30, (1,2):127.5, (3,1):390, (4,1):150, (5,1):450},
    'q_g_min': {(1,1):-30, (1,2):-127.5 , (3,1):-390 , (4,1):-150, (5,1):-450},
    'p_a_max': {(2,1):84.62 , (2,2):338.49, (3,1):211.56, (3,2):211.56, (4,1):324.39, (4,2):105.78, (4,3):133.99},
    'p_a_min': {(2,1):42, (2,2):168, (3,1):105, (3,2):105, (4,1):161, (4,2):52.5, (4,3):66.5},
    'q_a_max': {(2,1):25.69, (2,2):102.78, (3,1):64.24, (3,2):64.24, (4,1):98.48, (4,2):32.12, (4,3):40.68},
    'q_a_min': {(2,1):13.81, (2,2):55.22, (3,1):34.51, (3,2):34.51, (4,1):52.92, (4,2):17.26, (4,3):21.86}
}}