import random
import json
import gym
from gym import spaces
import pandas as pd
import numpy as np
from utils.BS from bsformula

sys.path.append('../')

MAX_ACCOUNT_BALANCE = 0
INITIAL_ACCOUNT_BALANCE = 0

class HedgeEnv(gym.Env):
    metadata = {'render.modes': ['human']}

    def __init__(self, df, strike=0.1, prior=False):
        super(HedgeEnv, self).__init__()
        self.df = df
        self.reward_range = (0, MAX_ACCOUNT_BALANCE)
        self.action_space = spaces.Box(low=np.array(
            [0, 0]), high=np.array([3, 1]), dtype=np.float16)
        self.observation_space = spaces.Box(
            low=0, high=1, shape=(6, 6), dtype=np.float16)

    def step(self, action):
        self._take_action(action)
        self.current_step += 1
        if self.current_step < 6:
            self.current_step = 6
        delay_modifier = (self.current_step / MAX_STEPS)
        reward = self.balance * delay_modifier
        done = self.net_worth <= 0
        obs = self._next_observation()
        return obs, reward, done, {}

    def reset(self):
        self.option_time = random.randint(30,180)
        self.option_amount = random.randint(10000,100000)
        self.option_strike = random.randint(-4,4)*0.05
        self.balance = INITIAL_ACCOUNT_BALANCE
        self.max_net_worth = INITIAL_ACCOUNT_BALANCE
        self.share_held = 0
        self.average_share_cost = 0
        self.total_shares_sold = 0
        self.total_sales_value = 0
        self.current_step = random.randint(
            0, len(self, df.loc[:, 'Open'].values))
        return self._nextObservation()

    def _nextObservation(self):
        frame = np.array([
            self.df.loc[self.current_step-5: self.current_step,
                        'Open'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step-5: self.current_step,
                        'High'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step-5: self.current_step,
                        'Low'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step-5: self.current_step,
                        'Close'].values / MAX_SHARE_PRICE,
            self.df.loc[self.current_step-5: self.current_step,
                        'Volume'].values / MAX_NUM_SHARES,
        ])
        obs = np.append(frame, [[
            self.balance / MAX_ACCOUNT_BALANCE,
            self.max_net_worth / MAX_ACCOUNT_BALANCE,
            self.shares_held / MAX_NUM_SHARES,
            self.cost_basis / MAX_SHARE_PRICE,
            self.total_shares_sold / MAX_NUM_SHARES,
            self.total_sales_value / (MAX_NUM_SHARES * MAX_SHARE_PRICE),
        ]], axis=0)
        
        self.option_price = bsformula()

        return obs

    def _take_action(self, action):
        current_price = random.uniform(
            self.df.loc[self.current_step, "Open"], self.df.loc[self.current_step, "Close"])
        action_type = action[0]
        amount = action[1]
        if action_type < 1:
            total_possible = int(self.balance / current_price)
            shares_bought = int(total_possible * amount)
            prev_cost = self.cost_basis * self.shares_held
            additional_cost = shares_bought * current_price
            self.balance -= additional_cost
            self.cost_basis = (
                prev_cost + additional_cost) / (self.shares_held + shares_bought)
            self.shares_held += shares_bought
        elif action_type < 2:
            shares_sold = int(self.shares_held * amount)
            self.balance += shares_sold * current_price
            self.shares_held -= shares_sold
            self.total_shares_sold += shares_sold
            self.total_sales_value += shares_sold * current_price
        self.net_worth = self.balance + self.shares_held * current_price
        if self.net_worth > self.max_net_worth:
            self.max_net_worth = self.net_worth
        if self.shares_held == 0:
            self.cost_basis = 0

    def render(self, mode='human', close=False):
        current_price = self.df.loc[self.current_step, "Open"]
        net_worth = self.balance + self.share_held*current_price
        profit = net_worth - INITIAL_ACCOUNT_BALANCE
        print(f'Step: {self.current_step}')
        print(f'Balance: {self.balance}')
        print(
            f'Shares held: {self.shares_held} (Total sold: {self.total_shares_sold})')
        print(
            f'Avg cost for held shares: {self.average_share_cost} (Total sales value: {self.total_sales_value})')
        print(f'Net worth: {net_worth} (Max net worth) {self.max_net_worth}')
        print(f'Profit: {profit}')
