import sys
import os
import numpy as np
import matplotlib.pyplot as plt 
from datetime import datetime
import argparse
from utils import epsilon_calc
from glob import glob
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--policy", default="TD3")                  # Policy name (TD3, DDPG or OurDDPG)
parser.add_argument("--env", default="HalfCheetahMuJoCoEnv-v0") # OpenAI gym environment name
parser.add_argument("--prioritized_replay", default=False, action='store_true')		# Include this flag to use prioritized replay buffer
parser.add_argument("--use_rank", default=False, action="store_true")               # Include this flag to use rank-based probabilities
parser.add_argument("--use_hindsight", default=False, action="store_true")          # Include this flag to use HER
parser.add_argument("--custom_env", default=False, action="store_true")             # our custom environment name
parser.add_argument("--reacher_epsilon_bounds", default=[2e-2, 2e-2], nargs=2, type=float, help="upper and lower epsilon bounds")
parser.add_argument("--k", default=1, type=int)                                     # k number of augmentations for HER
parser.add_argument("--decay_type", default="linear", help="'linear' or 'exp' epsilon decay")
args, unknown = parser.parse_known_args()
if unknown:
    print("WARNING: unknown arguments:", unknown)

eps_bounds = args.reacher_epsilon_bounds
exp_descriptors = [
    args.policy, 'CustomReacher' if args.custom_env else args.env,
    f"{'rank' if args.use_rank else 'proportional'}PER" if args.prioritized_replay else '', 
    'HER' if args.use_hindsight else '',
    f"{args.decay_type}decay-eps{f'{eps_bounds[0]}-{eps_bounds[1]}' if eps_bounds[0] != eps_bounds[1] else f'{eps_bounds[0]}'}" if args.custom_env else "",
    f"k{args.k}",
]
exp_descriptors = [x for x in exp_descriptors if len(x) > 0]
file_name = "_".join(exp_descriptors)       # file name root (minus timestamp)
graph_title = " ".join(exp_descriptors)


if not os.path.exists("./plots"):
    os.makedirs("./plots")

files = []
for f in glob(f"{sys.path[0]}/final_results/{file_name}*"):
    if f.endswith("npy"):
        files.append(f)
files.sort(reverse=True)        # most recent -> least recent
file_to_load = files[0]         # just use the most recent one; we can add options later
outfile_stem = f"./plots/{Path(file_to_load).stem}"      # output file stem, with timestamp

eval_freq = 5000

results = np.load(file_to_load)

x = np.arange(0, len(results) * eval_freq, eval_freq)
if args.custom_env:
    # plot original reward curve
    plt.fill_between(x, results[:, 2] - results[:, 3], results[:, 2] + results[:, 3], alpha=0.5)
    plt.plot(x, results[:, 2])
    plt.plot(x, [18] * len(x))
    plt.xlabel("Timesteps")
    plt.ylabel("Original Returns")
    plt.title(f"{graph_title} Original Rewards")
    plt.savefig(f"{outfile_stem}_original_rewards.png", bbox_inches='tight')
    print("Output to:", f"{outfile_stem}_original_rewards.png")
    plt.clf()

    # plot epsilon
    plt.plot(x, results[:, 4])
    plt.xlabel("Timesteps")
    plt.ylabel("Epsilon")
    plt.title(f"{graph_title} Epsilon Values")
    plt.savefig(f"{outfile_stem}_epsilon.png", bbox_inches='tight')
    print("Output to:", f"{outfile_stem}_epsilon.png")
    plt.clf()

plt.fill_between(x, results[:, 0] - results[:, 1], results[:, 0] + results[:, 1], alpha=0.5)
plt.plot(x, results[:, 0])
plt.xlabel("Timesteps")
plt.ylabel("Returns")
plt.title(f"{graph_title} Rewards")
plt.savefig(f"{outfile_stem}.png", bbox_inches='tight')
print("Output to:", f"{outfile_stem}.png")
plt.show()