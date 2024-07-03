'''
Created for running the SEOPF model
'''
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe


model = se.model
data = di.instance_data

model_instance = se.create_pyomo_instance(model, data)

def run_opf(model_instance):
    model_instance.t[13].fix(0)  # Fixing the angle of slack bus, selecting bus 13 as the slack bus
    opt = pe.SolverFactory('ipopt')
    opt.solve(model_instance)

run_opf(model_instance)


# run_opf(model_instance)
