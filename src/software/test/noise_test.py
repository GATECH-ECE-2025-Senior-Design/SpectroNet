import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import noise_integration



current_directory = os.path.dirname(os.path.realpath(__file__))
datasets_folder = images_folder = os.path.join(current_directory, "../..", "datasets")
digits_folder = os.path.join(datasets_folder, "digits")

os.mkdir(os.path.join(current_directory, "noise_test"))


noise_integration.integrate_noise_for_one_folder(12, 1, False, 880, os.path.join(digits_folder, "01"), os.path.join(current_directory, "noise_test"))
print("noisy digits put into test/noise_test")