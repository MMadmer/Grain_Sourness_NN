# Grain_Sourness_NN
Neural networks for analyzing the percentage of weeds in the grain flow. Also with noise filtering support

Using NN
------------------------------------------
Launch launcher.py to start
Launch adc_reader before measurements

Raw signal viewer
------------------------------------------
Launch Plot_of_Seed/Seeds/viewer/viewer.py 
to see saved raw signals

How to create a sample
------------------------------------------
Put raw data to proc_N folders
Launch sample_filter.py
Launch sample_creating.py

How to train a neural network
------------------------------------------
Launch mlp_NeuroNet.py to start MLP
training
Launch reg_NeuroNet.py to start 
linear regression training

How to use trained data
------------------------------------------
Put your trained neural network from logs
into the_best folder
