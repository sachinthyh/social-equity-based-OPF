import run_seopf as ropf
import dc_opf_model as dc
import se_opf_model as se
import data_instance as di
import pyomo.environ as pe
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
plt.rcParams['text.usetex'] = True

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
p_a_max_5 = np.array([se_instance.p_a_max[a, g] for (a,g) in se_instance.A])

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
    p_gen = np.array([instance.p_gen[x, y].value for (x,y) in instance.G])
    p_a = np.array([instance.p_a[x, y].value for (x,y) in instance.A])
    cost = a**2*p_gen + b*p_gen + c
    utility = gamma*p_a - 0.5*mu*p_a**2
    return p_gen, p_a, cost, utility

default_result_5_bus = calculate_cost_utility(se_instance, a_5, b_5, c_5, gamma_5, mu_5)
default_result_24_bus = calculate_cost_utility(dc_instance, a_24, b_24, c_24, gamma_24, mu_24)
original_5_utility = sum(default_result_5_bus[3])
original_5_cost = sum(default_result_5_bus[2])
original_24_utility = sum(default_result_24_bus[3])
original_24_cost = sum(default_result_24_bus[2])
print('(5utility, 5cost, 24utility, 24cost) = ',original_5_utility, original_5_cost, original_24_utility, original_24_cost)

def calc_sensitivity(model, data, type, percent_from, percent_to, a, b, c, gamma, mu):
    percent = []
    cost = []
    utility = []
    aggr_utility = {}
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
        aggr_utility[i] = np.array([instance.p_a[x, y].value for (x,y) in instance.A])
    return percent, cost, utility, aggr_utility

bus5_sensitivity = calc_sensitivity(se_model, data_5, 'ac', 10, 150, a_5, b_5, c_5, gamma_5, mu_5)

individual_aggr_power_original = bus5_sensitivity[3]
individual_aggr_utility_original = {}
for key in individual_aggr_power_original:
    aggr_p = individual_aggr_power_original[key]
    individual_aggr_utility_original[key] = gamma_5*aggr_p - 0.5*mu_5*aggr_p**2

individual_aggr_utility_max = gamma_5*p_a_max_5 - 0.5*mu_5*p_a_max_5**2
individual_aggr_utility_normalized = {}

for key in individual_aggr_utility_original:
    individual_aggr_utility_normalized[key] = individual_aggr_utility_original[key]/individual_aggr_utility_max*100

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

for key, values in individual_aggr_utility_normalized.items():
    keys = np.full(values.shape, key)
    ax.bar3d(keys, sigma_5, np.zeros_like(values), 1, 1, values, alpha=0.6, shade=True, color='lightgreen')

ax.set_xlabel(r'Percentage SES', fontsize=12)
ax.set_ylabel(r'SES of Each Aggregator', fontsize=12)
ax.set_zlabel(r'Normalized Satisfaction ($\times 10^{-2}$)', fontsize=10)
ax.set_yticks(sigma_5)
plt.savefig('Data/Results/indi_aggr_utility.pdf')
plt.clf()

plt.plot(bus5_sensitivity[0], bus5_sensitivity[1], color='orangered')  # Total cost
plt.xlabel(r'Percentage SES', fontsize=16)
plt.ylabel(r"Total Generation Cost (\$/h)", fontsize=16)
plt.savefig('Data/Results/total_cost_sens.pdf')
plt.clf()

plt.plot(bus5_sensitivity[0], bus5_sensitivity[2], color='springgreen')  # Total utility
plt.xlabel(r'Percentage SES', fontsize=16)
plt.ylabel(r"Total Satisfaction (\$/h)", fontsize=16)
plt.savefig('Data/Results/total_utility_sens.pdf')
plt.clf()

plt.plot(bus5_sensitivity[0], np.array(bus5_sensitivity[2])-np.array(bus5_sensitivity[1]), color='blueviolet')  # Social Welfare
plt.xlabel(r'Percentage SES', fontsize=16)
plt.ylabel(r"Social Welfare (\$/h)", fontsize=16)
plt.savefig('Data/Results/social_welfare_sens.pdf')
plt.clf()
