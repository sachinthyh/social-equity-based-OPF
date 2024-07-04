# Implementation of Social Equity driven OPF
# importing necessary libraries and packages
import pyomo.environ as pe

model = pe.AbstractModel(name="seopf")

# Declaring sets for variables
model.B = pe.Set()  # Set of buses
model.G = pe.Set()  # Set of generators (sub index of buses)
model.A = pe.Set()  # Set of aggregators: subsets indexed as (i,j) for each demand bus
model.L = pe.Set()  # Set of lines: indexed as (i,j) where i≠j and preferably, i<j
model.Y = pe.Set()  # Set of Admittances
model.GB = pe.Set()  # Set of generator buses

# Declaring variables
model.v = pe.Var(model.B)  # Bus voltages
model.t = pe.Var(model.B)  # Bus angles
model.p_gen = pe.Var(model.G)  # Generator active power outputs
model.q_gen = pe.Var(model.G)  # Generator reactive power outputs
model.p_a = pe.Var(model.A)  # Aggregator active power demands
model.q_a = pe.Var(model.A)  # Aggregator active power demands

# Declaring parameters
model.gamma = pe.Param(model.A)
model.mu = pe.Param(model.A)  # Utility function coefficients
model.sigma = pe.Param(model.A)  # Weight factors: Socioeconomic Status (SES)
model.ag = pe.Param(model.G)
model.bg = pe.Param(model.G)
model.cg = pe.Param(model.G)  # Generator cost coefficients (quadratic cost function)
model.gg = pe.Param(model.Y)  # Line conductances (+diagonal conductance)
model.bb = pe.Param(model.Y)  # Line susceptances (+diagonal susceptance)
model.sl = pe.Param(model.L)  # Line limits
model.v_max = pe.Param(initialize=1.05)  # Global upperbound for bus voltages (p.u.)
model.v_min = pe.Param(initialize=0.95)  # Global lowerbound for bus voltages (p.u.)
model.p_g_max = pe.Param(model.G)
model.p_g_min = pe.Param(model.G)
model.q_g_max = pe.Param(model.G)
model.q_g_min = pe.Param(model.G)  # Power dispatch limits of generators
model.p_a_max = pe.Param(model.A)
model.p_a_min = pe.Param(model.A)
model.q_a_max = pe.Param(model.A)
model.q_a_min = pe.Param(model.A)  # Power limits of aggregators
model.vg = pe.Param(model.GB)  # Voltages at generator buses

# Objective Function
def obj_seopf_rule(model):
    obj_sum = sum(model.sigma[d, a]*(model.gamma[d, a] * model.p_a[d, a] - 0.5*model.mu[d, a]*(model.p_a[d, a])**2)
                  for (d, a) in model.A)
    obj_sum -= sum(model.ag[b, g]*(model.p_gen[b, g])**2 + model.bg[b, g]*model.p_gen[b, g] + model.cg[b, g]
                   for (b, g) in model.G)
    return obj_sum
model.obj_seopf = pe.Objective(rule=obj_seopf_rule, sense=pe.maximize)

# Constraints
# Power Flow Equations
def p_eqn_rule(model, i):
    left_sum = sum(model.p_gen[b, g]/100
                  for (b,g) in model.G
                  if (b == i))
    left_sum += sum(-(model.p_a[b, a]/100)
                   for (b,a) in model.A
                   if (b == i))
    right_sum = sum(model.v[i]*model.v[j]*(model.gg[b, j]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[b, j]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b < j) and ((b,j) in model.Y) and (b == i))
    right_sum += sum(model.v[i]*model.v[j]*(model.gg[j, b]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[j, b]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b > j) and ((j,b) in model.Y) and (b == i))
    right_sum += sum(model.v[i]*model.v[j]*(model.gg[j, b]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[j, b]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b == j) and ((b,j) in model.Y) and (b == i))
    return (left_sum == right_sum if i !=13 else pe.Constraint.Skip)
model.p_eqn = pe.Constraint(model.B, rule=p_eqn_rule)

def q_eqn_rule(model, i):
    left_sum = sum(model.q_gen[b, g]/100
                  for (b,g) in model.G
                  if (b == i))
    left_sum += sum(-(model.q_a[b, a]/100)
                   for (b,a) in model.A
                   if (b == i))
    right_sum = sum(model.v[i]*model.v[j]*(model.gg[b, j]*pe.sin(model.t[b] - model.t[j])
                                           - model.bb[b, j]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b < j) and ((b,j) in model.Y) and (b == i))
    right_sum += sum(model.v[i]*model.v[j]*(model.gg[j, b]*pe.sin(model.t[b] - model.t[j])
                                          - model.bb[j, b]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b > j) and ((j,b) in model.Y) and (b == i))
    right_sum += sum(model.v[i]*model.v[j]*(model.gg[j, b]*pe.sin(model.t[b] - model.t[j])
                                          - model.bb[j, b]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b == j) and ((b,j) in model.Y) and (b == i))
    return (left_sum == right_sum if i != 13 else pe.Constraint.Skip)
model.q_eqn = pe.Constraint(model.B, rule=q_eqn_rule)

# Line Flow Limits
def line_limit_rule(model, i, j):
    return (((model.v[i])**2*model.gg[i, i] + model.v[i]*model.v[j]*(model.gg[i, j]*pe.cos(model.t[i] - model.t[j])
        + model.bb[i, j]*pe.sin(model.t[i] - model.t[j])))**2 <= (model.sl[i, j]/100)**2
    if (i < j) and ((i,j) in model.Y)
    else ((model.v[i])**2*model.gg[i, i] + model.v[i]*model.v[j]*(model.gg[j, i]*pe.cos(model.t[i] - model.t[j])
        + model.bb[j, i]*pe.sin(model.t[i] - model.t[j])))**2 <= (model.sl[j, i]/100)**2
    if (i > j) and ((j,i) in model.Y)
    else pe.Constraint.Skip)
model.line_limit = pe.Constraint(model.B*model.B, rule=line_limit_rule)

# Bus Voltage Limits
def bus_voltage_limit_rule(model, i):
    return (0.95, model.v[i], 1.05) # Global limits (0.95, 1.05) in p.u.
model.bus_voltage_limit = pe.Constraint(model.B, rule=bus_voltage_limit_rule)

# Generator Dispatch Limits
def gen_p_limit_rule(model, i, j):
    return (model.p_g_min[i, j], model.p_gen[i, j], model.p_g_max[i, j])
model.gen_p_limit = pe.Constraint(model.G, rule=gen_p_limit_rule)

def gen_q_limit_rule(model, i, j):
    return (model.q_g_min[i, j], model.q_gen[i, j], model.q_g_max[i, j])
model.gen_q_limit = pe.Constraint(model.G, rule=gen_q_limit_rule)

# Aggregator Power Limits
def agg_p_limit_rule(model, i, j):
    return (model.p_a_min[i, j], model.p_a[i, j], model.p_a_max[i, j])
model.agg_p_limit = pe.Constraint(model.A, rule=agg_p_limit_rule)

def agg_q_limit_rule(model, i, j):
    return (model.q_a_min[i, j], model.q_a[i, j], model.q_a_max[i, j])
model.agg_q_limit = pe.Constraint(model.A, rule=agg_q_limit_rule)


def create_pyomo_instance(model, data):  # Creting the instance for the abstract model.
    return model.create_instance(data)


'''
# Piecewise implementation (Not compatible with Pyomo as of 06/20/2024)
def obj_seopf_rule(model):
    obj_sum = sum(model.sigma[d,a]*(model.gamma[d,a]*(model.p_a[d,a])**2 - 0.5*model.mu[d,a]*model.p_a[d,a])
                  for (d, a) in model.A
                  if ((model.p_a[d,a]) <= model.gamma[d,a]/model.mu[d,a]))
    obj_sum += sum(0.5*(model.gamma[d,a])**2/model.mu[d,a]
                   for (d, a) in model.A
                   if ((model.p_a[d,a]) > model.gamma[d,a]/model.mu[d,a]))
    obj_sum -= sum(model.ag[b,g]*(model.p_gen[b,g])**2 + model.bg[b,g]*model.p_gen[b,g] + model.cg[b,g]
               for (b,g) in model.G)
    return obj_sum
model.obj_seopf = pe.Objective(rule=obj_seopf_rule)
'''