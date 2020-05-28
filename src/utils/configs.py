import argparse
from time import time
import json
import os


def parse():
    CSV_NAME = "HX50ETF.csv"  # 华夏上证50ETF净值
    t = time()
    parser = argparse.ArgumentParser(
        description="Option Hedge",
        prog="python ./main.py",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('--test', type=bool, default=False)
    parser.add_argument('--b_prior', type=bool, default=False) # whether use delta hedge as a prior
    parser.add_argument('--b_random', type=bool, default=False) # whether randomly extract data
    parser.add_argument('--timestep', type=int, default=100000)
    parser.add_argument('--test_size', type=int, default=244)  # days to test
    parser.add_argument('--test_times', type=int, default=10)
    parser.add_argument('--skip', type=int, default=5) # for every `skip` days, take an action
    parser.add_argument('--data_file', type=str,
                        default=None)  # stock or index prices
    parser.add_argument('--cfg_file', type=str,
                        default=None)  # to log these args
    parser.add_argument('--model_dir', type=str,
                        default=None)  # to save the models

    parser_args = parser.parse_args()
    root_dir = os.path.dirname(__file__) + '/../../'
    parser_args.data_file = root_dir + 'data/%s' % (CSV_NAME)
    parser_args.SHIBOR = [
        "{}data/SHIBOR{}.xls".format(root_dir, y) for y in range(2015, 2020)]
    parser_args.cfg_file = root_dir + 'results/%d' % (t)
    parser_args.model_dir = root_dir + 'results/model/%d' % (t)
    parser_args.log_dir = root_dir + 'results/log/%d' % (t)
    if not parser_args.test:
        if not os.path.exists(parser_args.model_dir):
            os.makedirs(parser_args.model_dir)
        if not os.path.exists(parser_args.log_dir):
            os.makedirs(parser_args.log_dir)
    return parser_args


class ConfigLog(object):
    def __init__(self, cfg):
        self.cfg = cfg

    def dump(self, cfg_file):
        cfg_file = cfg_file+".json"
        with open(cfg_file, "w") as f:
            json.dump(self.cfg.__dict__, f)

    def load(self, cfg_file):
        try:
            with open(cfg_file, "r") as f:
                self.cfg.__dict__ = json.load(f)
        except FileNotFoundError:
            print("Error! Cannot find cfg for " + cfg_file)
