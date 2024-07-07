'''
Created for running the SEOPF model
'''
import dc_opf_model as dc
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe
from pyomo.opt import SolverFactory


dc_model = dc.model
se_model = se.model
data = di.instance_data

dc_instance = dc.create_pyomo_instance(dc_model, data)
se_instance = se.create_pyomo_instance(se_model, data)

dc_solution = {(v.name, idx): v[idx].value for v in dc_instance.component_objects(pe.Var, active=True) for idx in v}
print(dc_solution)


def run_opf(model_instance):
    model_instance.t[13].fix(0)  # Fixing the angle of slack bus, selecting bus 13 as the slack bus
    solver_io = 'nl'
    solver = 'ipopt'
    opt = SolverFactory(solver, solver_io=solver_io, options={'max_iter':'5000', 'mu_strategy':'adaptive',
                                                              'adaptive_mu_globalization':'kkt-error',
                                                              'adaptive_mu_kkterror_red_iters':'5',
                                                              'adaptive_mu_restore_previous_iterate':'yes',
                                                              'mu_oracle':'probing'})
    return opt.solve(model_instance, tee=True)

def dc_init_opf(dc_instance, se_instance):
    dc_instance.t[13].fix(0)
    solver_io = 'nl'
    solver = 'ipopt'
    optdc = SolverFactory(solver, solver_io=solver_io, options={'max_iter':'5000', 'mu_strategy':'adaptive',
                                                              'adaptive_mu_globalization':'kkt-error',
                                                              'adaptive_mu_kkterror_red_iters':'5',
                                                              'adaptive_mu_restore_previous_iterate':'yes',
                                                              'mu_oracle':'probing'})
    optdc.solve(dc_instance, tee=True)
    dc_solution = {(v.name, idx): v[idx].value for v in dc_instance.component_objects(pe.Var, active=True) for idx in v}

    for v in se_instance.component_objects(pe.Var, active=True):
        for idx in v:
            if (v.name, idx) in dc_solution:
                v[idx].value = dc_solution[(v.name, idx)]

    se_instance.t[13].fix(0)
    optse = SolverFactory(solver, solver_io=solver_io, options={'max_iter':'5000', 'mu_strategy':'adaptive',
                                                              'adaptive_mu_globalization':'kkt-error',
                                                              'adaptive_mu_kkterror_red_iters':'5',
                                                              'adaptive_mu_restore_previous_iterate':'yes',
                                                              'mu_oracle':'probing'})
    '''After adding options for optse, Add code for initializing'''
    return optse.solve(se_instance, tee=True)

results = dc_init_opf(dc_instance)

se_instance.pprint()
