import argparse
import gym
import json
import datetime as dt
import matplotlib.pyplot as plt
import pandas as pd

from stable_baselines.common.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import PPO2

from env.hedge_env import HedgeEnv
from utils.configs import parse, ConfigLog
from policy.naive import naked, covered
from policy.delta import DeltaHedge


# 先用BS定期权价，假设只卖出这一种看涨（认购）期权，行权价=现价+strike


if __name__ == "__main__":
    cfg = parse()
    df = pd.read_csv(cfg.data_file)
    df = df.sort_values('Date')
    df_train = df.iloc[:cfg.test_size]
    df_test = df.iloc[cfg.test_size:]
    cfg_log = ConfigLog(cfg)
    

    if cfg.test:
        rl_return = []
        naive_return = []
        delta_return = []
        for i in range(cfg.test_times):
            # rl
            env = DummyVecEnv([lambda: HedgeEnv(df_test,strike,prior)])
            model = PPO2(MlpPolicy, env, verbose=1)
            obs = env.reset()
            for i in range(cfg.option_time):
                action, _states = model.predict(obs)
                obs, rewards, done, info = env.step(action)
                env.render()
            # delta
            for i in range(cfg.option_time):
                action, _states = model.predict(obs)
                obs, rewards, done, info = env.step(action)
                env.render()
            # naive
            naked()
            covered()
        # plot
    else:
        env = DummyVecEnv([lambda: HedgeEnv(df_train,strike,prior)])
        model = PPO2(MlpPolicy, env, verbose=1)
        model.learn(total_timesteps=cfg.timestep)
        model.save()
        cfg_log.dump()

        obs = env.reset()
        for i in range(cfg.option_time):
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)
            env.render()

            
