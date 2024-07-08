import run_seopf as ropf
import dc_opf_model as dc
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe
import numpy as np
import matplotlib.pyplot as plt


dc_model = dc.model
se_model = se.model
data_24 = di.instance_data_24
data_5 = di.instance_data_5

dc_instance = dc.create_pyomo_instance(dc_model, data_24)
dc_instance.t[13].fix(0)  # Fixing the angle of slack bus, selecting bus 13 as the slack bus for 24-bus case

se_instance = se.create_pyomo_instance(se_model, data_5)
se_instance.t[1].fix(0)  # Fixing the angle of slack bus, selecting bus 1 as the slack bus for 5-bus case

# Extracting parameter values of generators and aggregators
a_5 = np.array([se_instance.ag[b, g] for (b,g) in se_instance.G])
b_5 = np.array([se_instance.bg[b, g] for (b,g) in se_instance.G])
c_5 = np.array([se_instance.cg[b, g] for (b,g) in se_instance.G])
gamma_5 = np.array([se_instance.gamma[a, g] for (a,g) in se_instance.A])
mu_5 = np.array([se_instance.mu[a, g] for (a,g) in se_instance.A])
sigma_5 = np.array([se_instance.sigma[a, g] for (a,g) in se_instance.A])

a_24 = np.array([dc_instance.ag[b, g] for (b,g) in dc_instance.G])
b_24 = np.array([dc_instance.bg[b, g] for (b,g) in dc_instance.G])
c_24 = np.array([dc_instance.cg[b, g] for (b,g) in dc_instance.G])
gamma_24 = np.array([dc_instance.gamma[a, g] for (a,g) in dc_instance.A])
mu_24 = np.array([dc_instance.mu[a, g] for (a,g) in dc_instance.A])
sigma_24 = np.array([dc_instance.sigma[a, g] for (a,g) in dc_instance.A])

# Default case results (with original SES weights)
results_5 = ropf.run_opf(se_instance)
results_24 = ropf.run_opf(dc_instance)

def calculate_cost_utility(instance, a, b, c, gamma, mu):
    p_gen = np.array([instance.p_gen[b, g].value for (b,g) in instance.G])
    p_a = np.array([instance.p_a[b, g].value for (b,g) in instance.A])
    cost = a**2*p_gen + b*p_gen + c
    utility = gamma*p_a - 0.5*mu*p_a**2
    return p_gen, p_a, cost, utility

a = calculate_cost_utility(se_instance, a_5, b_5, c_5, gamma_5, mu_5)

def calc_sensitivity_total(model, data, type, percent_from, percent_to, a, b, c, gamma, mu):
    percent = []
    cost = []
    utility = []
    for i in range(percent_from, percent_to + 1, 2):
        if type == 'dc':
            instance = dc.create_pyomo_instance(model, data)
            instance.t[13].fix(0)
        elif type == 'ac':
            instance = se.create_pyomo_instance(model, data)
            instance.t[1].fix(0)
        instance.x.value = i/100
        ropf.run_opf(instance)
        cost_utility = calculate_cost_utility(instance, a, b, c, gamma, mu)
        cost.append(sum(cost_utility[2]))
        utility.append(sum(cost_utility[3]))
        percent.append(i)
    return percent, cost, utility

bus5_total_sensitivity = calc_sensitivity_total(se_model, data_5, 'ac', 10, 200, a_5, b_5, c_5, gamma_5, mu_5)


plt.plot(bus5_total_sensitivity[0], bus5_total_sensitivity[1])
plt.show()

plt.plot(bus5_total_sensitivity[0], bus5_total_sensitivity[2])
plt.show()

plt.plot(bus5_total_sensitivity[0], np.array(bus5_total_sensitivity[2])-np.array(bus5_total_sensitivity[1]))
plt.show()