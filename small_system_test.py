import se_opf_model as se
import pyomo.environ as pe
from pyomo.opt import SolverFactory

# IEEE 5-bus System Data (modified)
instance_data = {None: {
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
    'sl': {(1,2):400, (1,4):1000, (1,5):1000, (2,3):1000, (3,4):1000, (4,5):240},
    'p_g_max': {(1,1):100, (1,2):170, (3,1):520, (4,1):200, (5,1):600},
    'p_g_min': {(1,1):40, (1,2):110, (3,1):104, (4,1):40, (5,1):120},
    'q_g_max': {(1,1):30, (1,2):127.5, (3,1):390, (4,1):150, (5,1):450},
    'q_g_min': {(1,1):-30, (1,2):-127.5 , (3,1):-390 , (4,1):-150, (5,1):-450},
    'p_a_max': {(2,1):84.62 , (2,2):338.49, (3,1):211.56, (3,2):211.56, (4,1):324.39, (4,2):105.78, (4,3):133.99},
    'p_a_min': {(2,1):42, (2,2):168, (3,1):105, (3,2):105, (4,1):161, (4,2):52.5, (4,3):66.5},
    'q_a_max': {(2,1):25.69, (2,2):102.78, (3,1):64.24, (3,2):64.24, (4,1):98.48, (4,2):32.12, (4,3):40.68},
    'q_a_min': {(2,1):13.81, (2,2):55.22, (3,1):34.51, (3,2):34.51, (4,1):52.92, (4,2):17.26, (4,3):21.86}
}}

model = se.model

model_instance = se.create_pyomo_instance(model, instance_data)

def run_opf(model_instance):
    model_instance.t[1].fix(0)  # Fixing the angle of slack bus, selecting bus 13 as the slack bus
    solver_io = 'nl'
    solver = 'ipopt'
    opt = SolverFactory(solver, solver_io=solver_io,
                        options={'max_iter':'5000', 'mu_strategy':'adaptive',
                                 'adaptive_mu_globalization':'kkt-error', 'adaptive_mu_kkterror_red_iters':'5',
                                 'adaptive_mu_restore_previous_iterate':'yes', 'mu_oracle':'probing'})
    return opt.solve(model_instance, tee=True)

results = run_opf(model_instance)
# model_instance.pprint()