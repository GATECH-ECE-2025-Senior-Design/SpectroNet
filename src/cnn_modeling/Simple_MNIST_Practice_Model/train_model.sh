#!/usr/bin/bash
#SBATCH -JTrainingMNISTCNN               # Job name
#SBATCH -N1 --ntasks-per-node=1          # Number of nodes and cores per node required 
#SBATCH --gres=gpu:H100:1                # GPU type (H100) and number of GPUs 
#SBATCH --mem-per-gpu=224GB              # Memory per CPU core, 8 CPUs/GPU 
#SBATCH -t2:00:00                        # Duration of the job (Ex: 1 hour) 
#SBATCH -oReport-%j.out
#SBATCH --mail-type=END,FAIL             # Mail preferences 
#SBATCH --mail-user=jcochran66@gatech.edu # E-mail address for notifications 


module load cuda/11.8
module load anaconda3
conda activate sr_design
cd /home/hice1/jcochran66/code/practice_CNN/PracticeCNN/src
python mnist_cnn.py