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
model.gg = pe.Param(model.L)  # Line conductances
model.bb = pe.Param(model.L)  # Line Susceptances
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
