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

# LATEST PQ OKAY
def p_eqn_rule(model, i):  # Fully fixed
    left_sum = sum(model.p_gen[b, g]/100
                  for (b,g) in model.G
                  if (b == i))
    left_sum += sum(-(model.p_a[b, a]/100)
                   for (b,a) in model.A
                   if (b == i))
    right_sum = model.v[i]*sum(model.v[j]*(model.gg[b, j]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[b, j]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b < j) and ((b,j) in model.Y) and (b == i))
    right_sum += model.v[i]*sum(model.v[j]*(model.gg[j, b]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[j, b]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b > j) and ((j,b) in model.Y) and (b == i))
    right_sum += model.v[i]*sum(model.v[j]*(model.gg[j, b]*pe.cos(model.t[b] - model.t[j])
                                          + model.bb[j, b]*pe.sin(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b == j) and ((b,j) in model.Y) and b == i)
    return left_sum == right_sum
model.p_eqn = pe.Constraint(model.B, rule=p_eqn_rule)

def q_eqn_rule(model, i):  # Fully fixed
    left_sum = sum(model.q_gen[b, g]/100
                  for (b,g) in model.G
                  if (b == i))
    left_sum += sum(-(model.q_a[b, a]/100)
                   for (b,a) in model.A
                   if (b == i))
    right_sum = model.v[i]*sum(model.v[j]*(model.gg[b, j]*pe.sin(model.t[b] - model.t[j])
                                          - model.bb[b, j]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b < j) and ((b,j) in model.Y) and (b == i))
    right_sum += model.v[i]*sum(model.v[j]*(model.gg[j, b]*pe.sin(model.t[b] - model.t[j])
                                          - model.bb[j, b]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b > j) and ((j,b) in model.Y) and (b == i))
    right_sum += model.v[i]*sum(model.v[j]*(model.gg[j, b]*pe.sin(model.t[b] - model.t[j])
                                          - model.bb[j, b]*pe.cos(model.t[b] - model.t[j]))
                               for (b,j) in model.B*model.B
                               if (b == j) and ((b,j) in model.Y) and b == i)
    return left_sum == right_sum
model.q_eqn = pe.Constraint(model.B, rule=q_eqn_rule)