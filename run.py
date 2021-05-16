"""
File:     run.py
Author:   Edward Hanson (edward.t.hanson@duke.edu)
Desc:     Runs the PhotonicAccelerator system
"""

from PhotonicAccelerator import PhotonicAccelerator, read_config
import configparser as cp
import os
import argparse

parser = argparse.ArgumentParser(description="Neurophos Photonic Subsys")
parser.add_argument("--config", type=str, default="default.cfg", help="Simulation configuration file, loaded from acc_cfgs/")
args = parser.parse_args()

def main():
    
    config = cp.ConfigParser()
    cwd = os.getcwd()
    config_path = os.path.join(cwd, "acc_cfgs", args.config)
    config.read(config_path)

    acc = PhotonicAccelerator(config_path)

    model_cfg = config.get("simulation", "model_cfg")
    model_cfg = os.path.join(cwd, "model_cfgs", model_cfg)
    skip_resid = int(config.get("simulation", "skip_resid"))
    
    # load CNN dimensions
    layer_name, in_obj_size, out_obj_size, in_channels, out_channels, kernel_size, stride = read_config(model_cfg, skip_resid)

    for layer_idx in range(len(layer_name)):
        print()
        print("Processing layer: {}".format(layer_name[layer_idx]))

        # configure accelerator with current layer dimensions
        acc.load_layer(in_obj_size[layer_idx], out_obj_size[layer_idx], in_channels[layer_idx], out_channels[layer_idx], kernel_size[layer_idx], stride[layer_idx])

        # update and apply FSM state until 'done' signal is reached
        acc.update_state(True)
        cycle = 0
        while not acc.done:
            acc.apply_latch()
            acc.update_state()
            cycle += 1
        print("Cycle count = {}".format(cycle))

    print()
    cycles = acc.summary()


if __name__ == "__main__":
    main()
