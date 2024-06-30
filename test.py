# Power Flow Equation Fix
def p_eqn_rule(model, i):  # Fixed
    gen_sum = sum(model.p_gen[i, g]/100
                  if (i,g) in model.G
                  else 0 for (i,g) in model.G)
    aggr_sum = sum(-(model.p_a[i, a]/100)
                   if (i,a) in model.A
                   else 0 for (i,a) in model.A)
    left_sum = gen_sum + aggr_sum
    right_sum = sum(model.v[i]*model.v[j]*(model.gg[i, j]*pe.cos(model.t[i] - model.t[j])
                                          + model.bb[i, j]*pe.sin(model.t[i] - model.t[j]))
                               if ((i < j) and ((i,j) in model.Y))
                               else model.v[j]*(model.gg[j, i]*pe.cos(model.t[i] - model.t[j])
                                          + model.bb[j, i]*pe.sin(model.t[i] - model.t[j]))
                    if ((i > j) and ((j,i) in model.Y))
    else 0
                               for i in model.B for j in model.B)
    return (left_sum == right_sum)
model.p_eqn = pe.Constraint(model.B, rule=p_eqn_rule)


def q_eqn_rule(model, i):  # Fixed
    gen_sum = sum(model.q_gen[i, g]/100
                  if (i,g) in model.G
                  else 0 for (i,g) in model.G)
    aggr_sum = sum(-(model.q_a[i, a]/100)
                   if (i,a) in model.A
                   else 0 for (i,a) in model.A)
    left_sum = gen_sum + aggr_sum
    right_sum = sum(model.v[i]*model.v[j]*(model.gg[i, j]*pe.sin(model.t[i] - model.t[j])
                                          - model.bb[i, j]*pe.cos(model.t[i] - model.t[j]))
                               if ((i < j) and ((i,j) in model.Y))
                               else model.v[j]*(model.gg[j, i]*pe.sin(model.t[i] - model.t[j])
                                          - model.bb[j, i]*pe.cos(model.t[i] - model.t[j]))
                    if ((i > j) and ((j,i) in model.Y))
    else 0
                               for i in model.B for j in model.B)
    return (left_sum == right_sum)
model.q_eqn = pe.Constraint(model.B, rule=q_eqn_rule)