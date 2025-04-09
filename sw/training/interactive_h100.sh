#!/bin/bash
# Interactive SLURM Job Request for an H100 GPU with 30 CPUs

salloc \
  --job-name=Interactive_H100_GPU \
  --nodes=1 \
  --ntasks-per-node=30 \
  --gres=gpu:H100:1 \
  --time=02:00:00 \
  --qos=interactive \
  --output=interactive_h100_%j.out

# Once allocated, you will be dropped into an interactive shell on the allocated node.
# Optionally, load modules and activate environments:

module load anaconda3        # Load Anaconda if using conda environments
conda activate my_env        # Activate your Python environment (replace 'my_env' with your env name)

# You can now run your code interactively, e.g., start a Jupyter Notebook or work directly in the shell
