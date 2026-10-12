import math

NODES = (-2.8569700139, -1.35562618, 0., 1.35562618, 2.8569700139)
WEIGHTS = (.0112574113, .2220759220, .5333333334, .2220759220, .0112574113)

def sigmoid(x):
    return 1. / (1. + math.exp(-max(-35., min(35., x))))

def logistic_integral(z, variance):
    scale = math.sqrt(max(0., variance))
    return sum(w*sigmoid(z+scale*x) for x,w in zip(NODES,WEIGHTS))

true_param = -3.0
print(f"Base sigmoid(-3.0) = {sigmoid(true_param):.4f}")
print(f"Integral with var 0.5 = {logistic_integral(true_param, 0.5):.4f}")
print(f"Integral with var 2.0 = {logistic_integral(true_param, 2.0):.4f}")
print(f"Integral with var 5.0 = {logistic_integral(true_param, 5.0):.4f}")
