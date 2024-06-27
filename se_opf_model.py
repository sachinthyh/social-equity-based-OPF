# Implementation of Social Equity driven OPF
# importing necessary libraries and packages
import pyomo.environ as pe
# importing data processing file
import data_prep

model = pe.AbstractModel(name="seopf")

# Declaring sets for variables
model.B = pe.Set()  # Set of buses
model.G = pe.Set()  # Set of generators (sub index of buses)
model.D = pe.Set()  # Set of demands (sub index of buses)
model.A = pe.Set()  # Set of aggregators: subsets indexed as (i,j) for each demand bus
model.L = pe.Set()  # Set of lines: indexed as (i,j) where i≠j and preferably, i<j

# Declaring variables
model.v = pe.Var(model.B)  # Bus voltages
model.t = pe.Var(model.B)  # Bus angles
model.p_gen = pe.Var(model.G)  # Generator active power outputs
model.q_gen = pe.Var(model.G)  # Generator reactive power outputs
model.p_a = pe.Var(model.A)  # Aggregator active power demands
model.q_a = pe.Var(model.A)  # Aggregator active power demands
model.p_l = pe.Var(model.L)  # Line power flows

# Declaring parameters
model.gamma = pe.Param(model.A)
model.mu = pe.Param(model.A)  # Utility function coefficients
model.sigma = pe.Param(model.A)  # Weight factors: Socioeconomic Status (SES)
model.a = pe.Param(model.G)
model.b = pe.Param(model.G)
model.c = pe.Param(model.G)  # Generator cost coefficients (quadratic cost function)
model.gg = pe.Param(model.L)  # Line conductances (+self conductance)
model.bb = pe.Param(model.L)  # Line Susceptances (+self susceptance)
model.sl = pe.Param(model.L)  # Line limits
model.v_max = pe.Param(initialize=1.05,mutable=False)  # Global upperbound for bus voltages (p.u.)
model.v_min = pe.Param(initialize=-0.95,mutable=False)  # Global lowerbound for bus voltages (p.u.)
model.p_g_max = pe.Param(model.G)
model.p_g_min = pe.Param(model.G)
model.q_g_max = pe.Param(model.G)
model.q_g_min = pe.Param(model.G)  # Power dispatch limits of generators
model.p_a_max = pe.Param(model.A)
model.p_a_min = pe.Param(model.A)
model.q_a_max = pe.Param(model.A)
model.q_a_min = pe.Param(model.A)  # Power limits of aggregators

# Objective Function
def obj_seopf_rule(model):
    return sum(model.sigma[d,a]*(model.gamma[d,a]*(model.p_a[d,a])**2 - 0.5*model.mu[d,a]*model.p_a[d,a]) \
               - (model.a[g]*(model.p_gen[g])**2 + model.b[g]*model.p_gen[g] + model.c[g]) \
               for (d,a) in model.A for g in model.G)
model.obj_seopf = pe.Objective(rule=obj_seopf_rule)

# Constraints
# Power Flow Equations
def p_eqn_rule(model, i):
    return model.p_gen[model.B[i]] - sum(model.p_a[i,a] for (i,a) in model.A) \
        == model.v[i]*sum(model.v[j]*(model.gg[i,j]*pe.cos(model.t[i] - model.t[j]) \
                                      + model.bb[i,j]*pe.sin(model.t[i] - model.t[j])) \
                          for i in model.B for j in model.B)
model.p_eqn = pe.Constraint(model.B, rule=p_eqn_rule)

def q_eqn_rule(model, i):
    return model.q_gen[model.B[i]] - sum(model.q_a[i, a] for (i, a) in model.A) \
        == model.v[i]*sum(model.v[j]*(model.gg[i, j]*pe.sin(model.t[i] - model.t[j]) \
                                          - model.bb[i, j]*pe.cos(model.t[i] - model.t[j])) \
                            for i in model.B for j in model.B)
model.q_eqn = pe.Constraint(model.B, rule=q_eqn_rule)

# Line Flow Limits
def line_limit_rule(model, i, j):
    return (((model.v[i])**2*model.gg[i] - model.v[i]*model.v[j]*(model.gg[i,j]*pe.cos(model.t[i] - model.t[j]) \
                                                                 + model.bb[i,j]*pe.sin(model.t[i] - model.t[j])))**2 \
            <= (model.sl[i,j])**2) if i < j else None
model.line_limit = pe.Constraint(model.L, rule=line_limit_rule)