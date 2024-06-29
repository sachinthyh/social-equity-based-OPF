# Creating Instance for the Abstract Model
import pickle

# Loading data stored in .pkl files


def load_sets_params(filename):
    with open('Data/Parameters/' + filename + '.pkl', 'rb') as f:
        pkl_data = pickle.load(f)
    return pkl_data


# Names of sets and parameters
set_names = ['B', 'G', 'L', 'A']
param_names = ['gamma', 'mu', 'sigma',
               'ag', 'bg', 'cg',
               'gg', 'bb', 'sl',
               'p_g_max', 'p_g_min', 'q_g_max', 'q_g_min',
               'p_a_max', 'p_a_min', 'q_a_max', 'q_a_min']

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
instance_data = {None: {}}  # Initializing a data dictionary as per Pyomo requirements
create_data_instance_sets(instance_data, sets, set_names)
create_data_instance_params(instance_data, params, param_names)

with open('Data/Instance/instance_data.pkl', 'wb') as file:  # Exporting the data structure for external reference
    pickle.dump(instance_data, file)
