#!/bin/bash
#SBATCH --job-name=data_augmentation_for_CNN
#SBATCH --output=output.log
#SBATCH --error=error.log
#SBATCH --ntasks=1                              # Run 60 independent tasks
#SBATCH --cpus-per-task=1                       # Allocate 60 CPUs per task (corresponds to the number of files)
#SBATCH --mem-per-cpu=8G                        # Allocate 4GB per CPU (adjust as needed)
#SBATCH -oReport-%j.out
#SBATCH --mail-type=END,FAIL                    # Mail preferences 
#SBATCH --time=05:00:00                         # Adjust the time as needed



module anaconda3  # Load necessary modules if needed
# conda deactivate
# conda deactivate
# conda deactivate

conda activate sr_design

srun --exclusive python data_augmentation.py