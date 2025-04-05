import librosa
import numpy as np
import struct

# This script generates .mif files to be used as lookup-tables
# for the mel filterbank.
# Questasim behaves weirdly with simulating .mif based ROMs,
# so just convert .mif to .hex using Quartus and use that for the ROM.

n_fft = 512  # 512 samples per FFT
n_mels = 96  # 96 output bins
sr = 8000

# create filterbank
mel_filter = librosa.filters.mel(sr=sr, n_fft=n_fft, n_mels=n_mels)

# remove DC bin (first column) to match 256 input bins
mel_filter = mel_filter[:, 1:]  # Shape (96, 256)
print(f"Shape: {mel_filter.shape}")

# array of shape (96, 12)
# each element is the tuple (coeff, input bin idx)
mel_bin_eqns = []

# print each mel bin as a function of the input bins
for mel_idx in range(n_mels):
    terms = [
        # grab (coeff, input bin idx)
        (mel_filter[mel_idx, bin_idx], bin_idx)
        for bin_idx in range(256)
        if mel_filter[mel_idx, bin_idx] > 0  # only if nonzero
    ]
    
    # zero-pad until 12 elements
    # the most coefficients per mel bin is 12 in our case
    while len(terms) < 12:
       next_bin_idx = terms[-1][1] + 1
       terms.append((0.0, next_bin_idx))

    # add equation for this mel index to array of equations
    mel_bin_eqns.append(terms)

    # print equation for this mel index (debug)
    equation_terms = [f"{coeff:.6f}*b{bin_idx}" for coeff, bin_idx in terms]
    print(f"m{mel_idx} = " + " + ".join(equation_terms))

# convert to np array
mel_bin_eqns = np.array(mel_bin_eqns)

# Interleaved splitting into four (96, 3, 2) arrays
mel_bin_eqns_0 = mel_bin_eqns[:, 0:3, :]
mel_bin_eqns_1 = mel_bin_eqns[:, 3:6, :]
mel_bin_eqns_2 = mel_bin_eqns[:, 6:9, :]
mel_bin_eqns_3 = mel_bin_eqns[:, 9:12, :]

# debug
# print(mel_bin_eqns_0.shape)
# for mel_idx in range(n_mels):
#     equation_terms = [
#         f"{mel_bin_eqns_0[mel_idx, i, 0]:.6f}*b{int(mel_bin_eqns_0[mel_idx, i, 1])}"
#         for i in range(3)
#     ]
#     equation = f"m{mel_idx} = " + " + ".join(equation_terms)
#     print(equation)

# find index of first valid equation (that isn't just all coefficients to 0)
def find_first_nonzero(mel_bin_eqns_x):
    for idx in range(mel_bin_eqns_x.shape[0]):
        if np.any(mel_bin_eqns_x[idx, :, 0] != 0):
            return idx
    return -1 # if no equations are valid?

# starting indices
first_nonzero_0 = find_first_nonzero(mel_bin_eqns_0)
first_nonzero_1 = find_first_nonzero(mel_bin_eqns_1)
first_nonzero_2 = find_first_nonzero(mel_bin_eqns_2)
first_nonzero_3 = find_first_nonzero(mel_bin_eqns_3)

# debug
print()
print(f"bank 0: {first_nonzero_0}")
print(f"bank 1: {first_nonzero_1}")
print(f"bank 2: {first_nonzero_2}")
print(f"bank 3: {first_nonzero_3}")

# slice out invalid equations
mel_bin_eqns_0 = mel_bin_eqns_0[first_nonzero_0:, :, :]
mel_bin_eqns_1 = mel_bin_eqns_1[first_nonzero_1:, :, :]
mel_bin_eqns_2 = mel_bin_eqns_2[first_nonzero_2:, :, :]
mel_bin_eqns_3 = mel_bin_eqns_3[first_nonzero_3:, :, :]

# FFT index triggers (trigger at last index of equation)
# triggers[x][y] is whether the filterbank computation is triggered
# when the x-th FFT bin is read during the y-th sweep
triggers = np.zeros((256, 4), dtype=int)
for mel_bin_eqn in mel_bin_eqns_0:
    triggers[int(mel_bin_eqn[2][1])][3] = 1
for mel_bin_eqn in mel_bin_eqns_1:
    triggers[int(mel_bin_eqn[2][1])][2] = 1
for mel_bin_eqn in mel_bin_eqns_2:
    triggers[int(mel_bin_eqn[2][1])][1] = 1
for mel_bin_eqn in mel_bin_eqns_3:
    triggers[int(mel_bin_eqn[2][1])][0] = 1

# debug
with np.printoptions(threshold=np.inf):
    print(triggers)

# convert trigger values for 4 sweeps into hex values
trigger_hex_vals = [hex(int("".join(map(str, row)), 2))[2:].upper() for row in triggers]

# debug
for i, h in enumerate(trigger_hex_vals):
    print(f"Row {i}: {h}")

# determine how deep RAM needs to be to hold filterbank (3 words wide)
print()
ram_depth = 96*4 - first_nonzero_0 - first_nonzero_1 - first_nonzero_2 - first_nonzero_3
print(f"RAM depth: {ram_depth}")

# create filterbank coefficients (3 words wide, 220 words deep)
mel_filterbank = np.concatenate((mel_bin_eqns_0, mel_bin_eqns_1, mel_bin_eqns_2, mel_bin_eqns_3))
print()
print(f"RAM shape: {mel_filterbank.shape}")

# convert each equation to a hex string 
# 3 coefficients, 32 bit float -> 96 bits, or 24 characters
hex_strings = []
for mel_filter in mel_filterbank:
    coeffs = mel_filter[:, 0] # 3 coeffs
    hex_string = ''.join(struct.pack('>f', coeff).hex().upper() for coeff in coeffs)  # Convert to hex
    hex_strings.append(hex_string)

# print first hex string
print()
print(hex_strings[0])
print(len(hex_strings))

# write the hex strings of coefficients to a .mif file
filterbank_file = "filterbank_coeffs.mif"
with open(filterbank_file, "w") as f1:
    # metadata
    f1.write("-- This .mif file was generated using filterbank.py\n\n")
    f1.write("WIDTH=96;\nDEPTH=220;\n\n")
    f1.write("ADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\n\n")
    # fill memory
    f1.write("CONTENT BEGIN\n")
    for idx, hex_string in enumerate(hex_strings):
        f1.write(f"\t{format(idx, '02X')} : {hex_string};\n")
    f1.write("END;")

# write the hex strings of trigger conditions to a .mif file
fb_trigger_file = "filterbank_trigs.mif"
with open(fb_trigger_file, "w") as f2:
    # metadata
    f2.write("-- This .mif file was generated using filterbank.py\n\n")
    f2.write("WIDTH=4;\nDEPTH=256;\n\n")
    f2.write("ADDRESS_RADIX=HEX;\nDATA_RADIX=HEX;\n\n")
    # fill memory
    f2.write("CONTENT BEGIN\n")
    for idx, trigger_hex in enumerate(trigger_hex_vals):
        f2.write(f"\t{format(idx, '02X')} : {trigger_hex};\n")
    f2.write("END;")
