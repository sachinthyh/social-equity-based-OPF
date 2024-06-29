# importing data processing file
import data_instance as di
import se_opf_model as se
import json

# Creating the Data Instance
data = {None:{}} # Initializing a data dictionary as per Pyomo requirements
di.create_data_instance_sets(data, di.sets, di.set_names)
di.create_data_instance_params(data, di.params, di.param_names)

print(data)