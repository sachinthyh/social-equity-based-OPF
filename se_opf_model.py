# Implementation of Social Equity driven OPF
# importing necessary libraries and packages
import pyomo.environ as pe

model = pe.AbstractModel(name="seopf")

# Declaring sets for variables
model.B = pe.Set()  # Set of buses
model.G = pe.Set()  # Set of generators (sub index of buses)
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
model.gamma = pe.Param(model.A, default=set())
model.mu = pe.Param(model.A, default=set())  # Utility function coefficients
model.sigma = pe.Param(model.A, default=set())  # Weight factors: Socioeconomic Status (SES)
model.ag = pe.Param(model.G, default=set())
model.bg = pe.Param(model.G, default=set())
model.cg = pe.Param(model.G, default=set())  # Generator cost coefficients (quadratic cost function)
model.gg = pe.Param(model.L, default=set())  # Line conductances (+self conductance)
model.bb = pe.Param(model.L, default=set())  # Line Susceptances (+self susceptance)
model.sl = pe.Param(model.L, default=set())  # Line limits
model.v_max = pe.Param(initialize=1.05,mutable=False)  # Global upperbound for bus voltages (p.u.)
model.v_min = pe.Param(initialize=-0.95,mutable=False)  # Global lowerbound for bus voltages (p.u.)
model.p_g_max = pe.Param(model.G, default=set())
model.p_g_min = pe.Param(model.G, default=set())
model.q_g_max = pe.Param(model.G, default=set())
model.q_g_min = pe.Param(model.G, default=set())  # Power dispatch limits of generators
model.p_a_max = pe.Param(model.A, default=set())
model.p_a_min = pe.Param(model.A, default=set())
model.q_a_max = pe.Param(model.A, default=set())
model.q_a_min = pe.Param(model.A, default=set())  # Power limits of aggregators

# Objective Function
def obj_seopf_rule(model):
    obj_sum = sum(model.sigma[d,a]*(model.gamma[d,a]*(model.p_a[d,a])**2 - 0.5*model.mu[d,a]*model.p_a[d,a])
                  if ((model.p_a[d,a] >= 0) and (model.p_a[d,a] <= model.gamma[d,a]/model.mu[d,a]))
                  else 0.5*(model.gamma[d,a])**2/model.mu[d,a]
                  for (d,a) in model.A)
    obj_sum -= sum(model.ag[b,g]*(model.p_gen[b,g])**2 + model.bg[b,g]*model.p_gen[b,g] + model.cg[b,g]
               for (b,g) in model.G)
    return obj_sum
model.obj_seopf = pe.Objective(rule=obj_seopf_rule)

# Constraints
# Power Flow Equations
def p_eqn_rule(model, i):
    return ((sum(model.p_gen[i, g]/100 - model.p_a[i, a]/100 for (i, g) in model.G (i, a) in model.A)
            == model.v[i]*sum(model.v[j]*(model.gg[i, j]*pe.cos(model.t[i] - model.t[j])
                                          + model.bb[i, j]*pe.sin(model.t[i] - model.t[j]))
                              for i in model.B for j in model.B))
    if i < j
            else
            (sum(model.p_gen[i, g]/100 - model.p_a[i, a]/100 for (i, g) in model.G(i, a) in model.A)
             == model.v[i] * sum(model.v[j] * (model.gg[j, i] * pe.cos(model.t[i] - model.t[j])
                                               + model.bb[j, i] * pe.sin(model.t[i] - model.t[j]))
                                 for i in model.B for j in model.B))
            )
model.p_eqn = pe.Constraint(model.B, rule=p_eqn_rule)


def q_eqn_rule(model, i):
    return (sum(model.q_gen[i, g]/100 - model.q_a[i, a]/100 for (i, g) in model.G (i, a) in model.A)
            == model.v[i]*sum(model.v[j]*(model.gg[i, j]*pe.sin(model.t[i] - model.t[j])
                                          - model.bb[i, j]*pe.cos(model.t[i] - model.t[j]))
                              for i in model.B for j in model.B))
model.q_eqn = pe.Constraint(model.B, rule=q_eqn_rule)

# Line Flow Limits
def line_limit_rule(model, i, j):
    return (((model.v[i])**2*model.gg[i] - model.v[i]*model.v[j]*(model.gg[i,j]*pe.cos(model.t[i] - model.t[j])
        + model.bb[i,j]*pe.sin(model.t[i] - model.t[j])))**2 <= (model.sl[i,j]/100)**2
    if i < j else pe.Constraint.Skip)
model.line_limit = pe.Constraint(model.L, rule=line_limit_rule)

# Bus Voltage Limits
def bus_voltage_limit_rule(model, i):
    return model.v_min <= model.v[i] <= model.v_max
model.bus_voltage_limit = pe.Constraint(model.B, rule=bus_voltage_limit_rule)

# Generator Dispatch Limits
def gen_p_limit_rule(model, i):
    return model.p_g_min[i] <= model.p_gen[i] <= model.p_g_max[i]
model.gen_p_limit = pe.Constraint(model.G, rule=gen_p_limit_rule)

def gen_q_limit_rule(model, i):
    return model.q_g_min[i] <= model.q_gen[i] <= model.q_g_max[i]
model.gen_q_limit = pe.Constraint(model.G, rule=gen_q_limit_rule)

# Aggregator Power Limits
def agg_p_limit_rule(model, i):
    return model.p_a_min[i] <= model.p_a[i] <= model.p_a_max[i]
model.agg_p_limit = pe.Constraint(model.A, rule=agg_p_limit_rule)

def agg_q_limit_rule(model, i):
    return model.q_a_min[i] <= model.q_a[i] <= model.q_a_max[i]
model.agg_q_limit = pe.Constraint(model.A, rule=agg_q_limit_rule)
