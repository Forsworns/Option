import random
import json
import gym
from gym import spaces
import pandas as pd
import numpy as np
import sys

from utils.BS import bsformula
from policy.delta import DeltaHedge

sys.path.append('../')

MAX_INT = 2147483647

class HedgeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df, df_rate, cfg):
        super(HedgeEnv, self).__init__()
        self.df = df
        self.steps = df.shape[0]
        self.df_rate = df_rate
        self.skip = cfg.skip
        self.b_prior = cfg.b_prior
        self.b_rl = True
        if self.b_prior:
            self.delta_hedger = DeltaHedge()
        self.b_random = cfg.b_random
        self.reset()
        self.reward_range = (-MAX_INT, self.amount*self.option_price)
        # -1 is to sold out the stock or fund
        self.action_space = spaces.Box(low=np.array(
            [-1]), high=np.array([1]), dtype=np.float16)
        self.observation_space = spaces.Box(
            low=-MAX_INT, high=MAX_INT, shape=(self.skip+1, 6), dtype=np.float32)

    def reset(self):
        self.T = random.randint(30, 180)  # option expiration date
        # share of the target assets
        self.amount = random.randint(1, 10) # \times 10000
        self.beginning_step = random.randint(
            self.skip, self.df.shape[0]-self.T-1)
        self.current_step = self.beginning_step
        self.t = 0
        self.sigma = self.df.loc[self.beginning_step:
                                 self.beginning_step+self.T-1, 'close'].std()
        start = self.df.loc[self.beginning_step, 'Date']
        end = self.df.loc[self.beginning_step+self.T, 'Date']
        l_b = self.df_rate['Date'].map(lambda x: x >= start)
        h_b = self.df_rate['Date'].map(lambda x: x < end)
        self.rate = self.df_rate.where(l_b & h_b)['3M'].mean()
        # print("sigma",self.sigma)
        # print("rate",self.rate)
        self.s_0 = self.df.at[self.beginning_step, 'close']
        self.s_T = self.df.at[self.beginning_step+self.T-1, 'close']
        # strike price of the option
        self.s_X = self.s_0 + random.randint(-4, 4)*0.05
        self.option_price, _, _ = bsformula(
            "call", self.s_0, self.s_X, self.rate, self.T/365.0, self.sigma)
        self.balance = self.amount*self.option_price
        self.hold = 0
        return self._next_observation()

    def restart(self):
        # similar to the reset, but do not resample the env, only initialize
        self.beginning_step = random.randint(
            self.skip, self.df.shape[0]-self.T-1)
        self.current_step = self.beginning_step
        self.t = 0
        self.balance = self.amount*self.option_price
        self.hold = 0

    def step(self, action):
        if self.current_step + self.skip < self.T:
            self._take_action(action)
            delay_modifier = (self.current_step / self.T)
            reward = self.balance * delay_modifier
            done = False
        else:
            # at the option exercise date
            self.s_t = self.df.at[self.beginning_step+self.T-1, 'close']
            if self.s_t >= self.s_X:  # the call option won't be carried
                self.balance += self.s_t*self.hold
                self.hold = 0
            reward = self.balance
            done = True
            self.final_reward = reward
        reward /= self.amount
        self.current_step += self.skip
        self.t = self.t + self.skip
        obs = self._next_observation()
        return obs, reward, done, {}

    def _next_observation(self):
        obs_df = self.df.loc[self.current_step-self.skip+1: self.current_step,
                             ['close', 'open', 'high', 'low', 'amount', 'rate']]
        obs = np.array(obs_df)
        obs = np.append(obs, np.array([[
            self.balance,
            self.s_0,
            self.s_X,
            self.T-self.t,
            self.amount,
            self.hold,
        ]]), axis=0)
        # print(obs)
        return obs

    def _take_action(self, action):
        self.s_t = self.df.at[self.current_step, 'close'] # note in rl, the delta hedger view different price 
        if self.b_rl:
            transaction = action[0]*self.amount
            # use delta hedging as a human prior (then it becomes a residual learning problem)
            if self.b_prior:
                delta_action = self.delta_hedger.make_decision(self)
                transaction += delta_action[0][0]
        else:
            transaction = action[0]
        self.hold += transaction
        self.balance -= transaction*self.s_t

    def render(self, mode='human', close=False):
        current_price = self.df.at[self.current_step, 'close']
        date = self.df.at[self.current_step, 'Date']
        print(f'Step: {self.current_step-self.beginning_step}:{self.T}')
        print(f'Date: {date}')
        print(f'Price: {current_price}')
        print(f'strike price:{self.s_X}')
        print(
            f'Shares held: {self.hold}')
