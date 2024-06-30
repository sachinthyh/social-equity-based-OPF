# importing modules and packages
import se_opf_model as se
import data_instance as di
import run_seopf as ropf

# Importing the Data Instance
model = se.model
data = di.instance_data
# Creating Instance
model_instance = se.create_pyomo_instance(model, data)
model_instance.pprint()

