(left_sum == right_sum if i != 1 else pe.Constraint.Skip)

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