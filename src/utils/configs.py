import argparse
from time import time
import json
import os


def parse():
    CSV_NAME = "HX50ETF.csv" # 华夏上证50ETF净值
    t = time()
    parser = argparse.ArgumentParser(
        description="Option Hedge",
        prog="python ./main.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--test', type=bool, default=False)
    parser.add_argument('--prior', type=bool, default=False)
    parser.add_argument('--timestep', type=int, default=10000) 
    parser.add_argument('--test_size', type=int, default=244) # days to test
    parser.add_argument('--test_times', type=int, default=2) 
    # parser.add_argument('--option_time', type=int, default=90) # option time
    # parser.add_argument('--option_amount', type=int, default=10000) # option amount
    # parser.add_argument('--option_strike', type=float, default=0.1) # strike price = option_strike + now
    parser.add_argument('--data_file', type=str, default=None) # stock or index prices 
    parser.add_argument('--cfg_dir', type=str, default=None) # to log these args
    parser.add_argument('--model_dir', type=str, default=None) # to save the models

    root_dir = os.path.dirname(__file__) + '/../../'
    data_file = root_dir + 'data/%s.csv' % (CSV_NAME)
    cfg_dir = root_dir + 'results/cfg/cfg%d' % (t)
    model_dir = root_dir + 'results/model/model%d' % (t)
    if not os.path.exists(cfg_dir):
        os.makedirs(cfg_dir)
    if not os.path.exists(model_dir):
        os.makedirs(model_dir)
    
    parser_args = parser.parse_args()
    return parser_args


class ConfigLog(object):
    def __init__(self, cfg, cost=None):
        self.cfg = cfg
        if cost is not None:
            self.cfg.update({'cost': cost})

    def dump(self, para_dir):
        t = int(time())
        cfg_file = "{}/{}.json".format(para_dir, t)
        with open(cfg_file, "w") as f:
            json.dump(self.cfg, f)

    def load(self, cfg_file):
        try:
            with open(d_cfg_file, "r") as f:
                self.cfg = json.load(f)
        except FileNotFoundError:
            print("Error! Cannot find cfg for " + cfg_file)

