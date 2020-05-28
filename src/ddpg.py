import argparse
import gym
import json
import datetime as dt
import matplotlib.pyplot as plt

from stable_baselines.ddpg.policies import MlpPolicy
from stable_baselines.common.vec_env import DummyVecEnv
from stable_baselines import DDPG
from stable_baselines.common.callbacks import CheckpointCallback, EvalCallback

from env.hedge_env import HedgeEnv
from utils.configs import parse, ConfigLog
from utils.util import load_data
from policy.naive import naked, covered
from policy.delta import DeltaHedge


# 先用BS定期权价，假设只卖出这一种看涨（认购）期权，行权价=现价+strike
TIME = 1590585091 # plain
TIME = 1590586392 # prior
EPISODE = 90000
# TEST_MODEL = f"../results/model/{TIME}/best_model.zip"
TEST_MODEL = f"../results/model/{TIME}/rl_model_{EPISODE}_steps.zip"
CFG_FILE = f"./.results/{TIME}.json"

if __name__ == "__main__":
    cfg = parse()
    cfg_log = ConfigLog(cfg)

    # test & train
    if cfg.test:
        cfg_log.load(CFG_FILE)
        # load data
        df_train, df_test, df_rate = load_data(cfg)
        rl_returns = []
        naked_returns = []
        covered_returns = []
        delta_returns = []
        env = DummyVecEnv([lambda: HedgeEnv(df_test, df_rate, cfg)])
        T = env.get_attr('T')[0]
        model = DDPG(MlpPolicy, env, verbose=1)
        model.load(TEST_MODEL)
        delta = DeltaHedge()
        for i in range(cfg.test_times):
            # rl
            env.set_attr("b_rl",True)
            obs = env.reset()  # every time, create a new transaction
            naked_returns.append(naked(env))
            covered_returns.append(covered(env))
            for i in range(T):
                action, _states = model.predict(obs)
                obs, rewards, done, info = env.step(action)
                # env.render()
            rl_returns.append(env.get_attr('final_reward')[0])
            env.env_method('restart')  # only trace back to the initial state
            env.set_attr("b_rl",False)
            # delta
            for i in range(T):
                action = delta.make_decision(env)
                obs, rewards, done, info = env.step(action)
                # env.render()
            delta_returns.append(env.get_attr('final_reward')[0])
        print("naked:",naked_returns)
        print("covered:",covered_returns)
        print("rl:",rl_returns)
        print("delta:",delta_returns)

    else:
        # load data
        df_train, df_test, df_rate = load_data(cfg)
        env = DummyVecEnv([lambda: HedgeEnv(df_train, df_rate, cfg)])
        T = env.get_attr('T')[0]
        checkpoint_callback = CheckpointCallback(
            save_freq=cfg.timestep/10, save_path=cfg.model_dir)
        eval_callback = EvalCallback(env, best_model_save_path=cfg.model_dir,
                                     log_path=cfg.log_dir, eval_freq=cfg.timestep/10, deterministic=True, render=False)
        model = DDPG(MlpPolicy, env, verbose=1)
        model.learn(total_timesteps=cfg.timestep, callback=[
                    checkpoint_callback, eval_callback])
        cfg_log.dump(cfg.cfg_file)

        obs = env.reset()
        for i in range(T):
            action, _states = model.predict(obs)
            obs, rewards, done, info = env.step(action)
            env.render()
            
