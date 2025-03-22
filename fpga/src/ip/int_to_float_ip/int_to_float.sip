set_global_assignment -entity "int_to_float" -library "lib_int_to_float" -name IP_TOOL_NAME "altera_fp_functions"
set_global_assignment -entity "int_to_float" -library "lib_int_to_float" -name IP_TOOL_VERSION "23.1"
set_global_assignment -entity "int_to_float" -library "lib_int_to_float" -name IP_TOOL_ENV "mwpim"
set_global_assignment -library "lib_int_to_float" -name SPD_FILE [file join $::quartus(sip_path) "int_to_float.spd"]

set_global_assignment -library "lib_int_to_float" -name MISC_FILE [file join $::quartus(sip_path) "int_to_float_sim/int_to_float.vo"]
