'''
Created for running the SEOPF model
'''
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe
from pyomo.opt import SolverFactory


model = se.model
data = di.instance_data

model_instance = se.create_pyomo_instance(model, data)

def run_opf(model_instance):
    model_instance.t[13].fix(0)  # Fixing the angle of slack bus, selecting bus 13 as the slack bus
    solver_io = 'nl'
    solver = 'ipopt'
    opt = SolverFactory(solver, solver_io=solver_io,
                        options={'max_iter':'5000', 'mu_strategy':'adaptive',
                                 'adaptive_mu_globalization':'kkt-error', 'adaptive_mu_kkterror_red_iters':'5',
                                 'adaptive_mu_restore_previous_iterate':'yes', 'mu_oracle':'probing'})
    return opt.solve(model_instance, tee=True)

results = run_opf(model_instance)

# model_instance.pprint()
