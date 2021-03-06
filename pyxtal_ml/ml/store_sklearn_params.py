import yaml
import numpy as np
from sklearn.gaussian_process.kernels import (RBF, WhiteKernel, Matern, RationalQuadratic,
                                                ExpSineSquared, DotProduct,
                                                ConstantKernel)


default_params = {
        'KNeighborsRegressor':
        {'cv': 10,
            'params': {"n_neighbors":[3,4], "p":[1.0, 2.0], "leaf_size":[30,100]}},
        'KernelRidge':
        {'cv': 10,
            'params': {"alpha": [1e3, 100, 10, 1, 0.1, 1e-2, 1e-3], "gamma": [-5, 1, 5], "kernel": ['rbf', 'laplacian', 'linear']}},
        'GradientBoostingRegressor': 
        {'cv': 10,
            'params': {"learning_rate": [0.01, 0.1, 1, 10], "n_estimators": [100, 500, 1000, 1500, 2500, 3000, 4000, 5000]}},
        'RandomForestRegressor':
        {'cv': 10,
            'params': {"n_estimators": [10, 30, 60, 90, 150, 250]}},
        'SGDRegressor':
        {'cv': 10,
            'params': {"penalty": ['l2', 'elasticnet'], "alpha": [1e5, 1e4, 1e3, 100, 10, 1, 0.1, 1e-2, 1e-3, 1e-4, 1e-5], "learning_rate": ['optimal', 'constant', 'invscaling', 'adaptive']}},
        'SVR':
        {'cv': 10,
            'params': {"gamma": [0.01, 0.1, 1, 10, 100], "epsilon": [1e-2, 1e-1, 1, 1e1, 1e2], "C": [1, 10, 100, 1000, 10000]}},
        'Lasso':
        {'cv': 10,
            'params': {"alpha": [1e3, 100, 10, 1, 0.1, 1e-2, 1e-3]}},
        'ElasticNet':
        {'cv': 10,
            'params': {"alpha": [1e3, 100, 10, 1, 0.1, 1e-2, 1e-3], "l1_ratio": [1, 0.5, 0]}},
        'MLPRegressor':
        {'cv': 10,
            'params': {"hidden_layer_sizes": [(50, 3)], "solver": ['lbfgs'], "learning_rate": ['invscaling']}},
        'GaussianProcessRegressor':
        {'cv': 10,
            'params': {"kernel": [WhiteKernel(), ExpSineSquared(), WhiteKernel()+ExpSineSquared()]}}
        }


with open('sklearn_params.yaml', 'w') as outfile:
    yaml.dump(default_params, outfile, default_flow_style=False)

with open('sklearn_params.yaml', 'r') as stream:
    try:
        data = yaml.load(stream)
    except yaml.YAMLError as exc:
        print(exc)
