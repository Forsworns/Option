import numpy as np
from utils.BS import delta
from stable_baselines.common.vec_env import DummyVecEnv
import sys

sys.path.append('../')


class DeltaHedge(object):
    def __init__(self):
        pass

    def make_decision(self, env):
        if isinstance(env,DummyVecEnv):
            s_0 = env.get_attr('s_t')[0]
            X = env.get_attr('s_X')[0] 
            r = env.get_attr('rate')[0] 
            sigma = env.get_attr('sigma')[0] 
            amount = env.get_attr('amount')[0] 
            hold = env.get_attr('hold')[0]
            t = (env.get_attr('T')[0] - env.get_attr('t')[0])/365.0
        else:
            s_0 = env.s_t
            X = env.s_X 
            r = env.rate 
            sigma = env.sigma 
            amount = env.amount 
            hold = env.hold
            t = (env.T - env.t)/365.0  
        new_delta = delta("call", s_0, X, r, t, sigma, 0)
        action = amount*new_delta - hold
        return [np.array([action])]


if __name__ == '__main__':
    pass
