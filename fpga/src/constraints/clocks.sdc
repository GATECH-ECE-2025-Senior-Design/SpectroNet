set_time_format -unit ns -decimal_places 3

# ##############################################################################

# Internal Clock
create_clock -name "CLOCK_50" -period 20.000 [get_ports CLOCK_50]

# Other 50MHz clocks from the DE-10
create_clock -name "CLOCK2_50" -period 20.000 [get_ports CLOCK2_50]
create_clock -name "CLOCK3_50" -period 20.000 [get_ports CLOCK3_50]
create_clock -name "CLOCK4_50" -period 20.000 [get_ports CLOCK4_50]

# Clock driven by WM8731 (as a master)
create_clock -name "AUD_BCLK" -period 83.333 [get_ports AUD_BCLK]

# I2C logic generated clock
create_generated_clock -name "I2C_SCLK" -divide_by 500 -source \
    [get_ports CLOCK_50] [get_nets {i2c_master:i2c_master_inst|data_clk}]

# WM8731 Audio Codec 
# create_clock -name "AUD_XCLK" -period "12.000 MHz" [get_ports AUD_XCK]
# create_clock -name "AUD_BCLK" -period "____ MHz" [get_ports AUD_BCLK] #(only if we want to use WM8731 in slave mode)

# ##############################################################################

# Now that we have created the custom clocks which will be base clocks,
# derive_pll_clock is used to calculate all remaining clocks for PLLs
derive_pll_clocks -create_base_clocks
derive_clock_uncertainty

# Ignore output delay for i2c out
set_false_path -to [get_ports {FPGA_I2C_SDAT FPGA_I2C_SCLK}]
# set_output_delay 0 [get_ports {FPGA_I2C_SDAT FPGA_I2C_SCLK}]

# Ignore input delay for i2c in
set_false_path -from [get_ports {FPGA_I2C_SDAT FPGA_I2C_SCLK}]
# set_input_delay 0 [get_ports {FPGA_I2C_SDAT FPGA_I2C_SCLK}]