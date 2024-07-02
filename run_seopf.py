'''
Created for running the SEOPF model
'''
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe


model = se.model
data = di.instance_data

def run_opf(model, data):
    model_instance = se.create_pyomo_instance(model, data)
    # Fixing the voltage and angle of slack bus
    model_instance.v[1].fix(1.05)
    model_instance.t[1].fix(0)
    opt = pe.SolverFactory('ipopt')
    return opt.solve(model_instance)


model_instance = se.create_pyomo_instance(model, data)

# Fixing the voltage and angle of slack bus
model_instance.v[1].fix(1.05)
model_instance.t[1].fix(0)
model_instance.pprint()

# run_opf(model, data)
