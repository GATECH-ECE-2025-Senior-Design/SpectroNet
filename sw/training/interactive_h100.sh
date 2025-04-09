#!/bin/bash
# Interactive SLURM Job Request for an H100 GPU with 30 CPUs

salloc --job-name=Interactive_H100_GPU \
       --nodes=1 \
       --ntasks-per-node=30 \
       --gres=gpu:H100:1 \
       --time=02:00:00 \
       --qos=interactive

# When the allocation is complete, you'll receive a shell on a GPU-enabled node.

# Load the Anaconda module.
module load anaconda3

# Activate the base environment (since that's the only available one).
conda activate base

# Now, verify that the H100 GPU is available.
nvidia-smi
