set_global_assignment -entity "complex_magnitude" -library "lib_complex_magnitude" -name IP_TOOL_NAME "altera_fp_functions"
set_global_assignment -entity "complex_magnitude" -library "lib_complex_magnitude" -name IP_TOOL_VERSION "23.1"
set_global_assignment -entity "complex_magnitude" -library "lib_complex_magnitude" -name IP_TOOL_ENV "mwpim"
set_global_assignment -library "lib_complex_magnitude" -name SPD_FILE [file join $::quartus(sip_path) "complex_magnitude.spd"]

set_global_assignment -library "lib_complex_magnitude" -name MISC_FILE [file join $::quartus(sip_path) "complex_magnitude_sim/complex_magnitude_memoryC0_uid193_sqrtTables_lutmem.hex"]
set_global_assignment -library "lib_complex_magnitude" -name MISC_FILE [file join $::quartus(sip_path) "complex_magnitude_sim/complex_magnitude_memoryC1_uid196_sqrtTables_lutmem.hex"]
set_global_assignment -library "lib_complex_magnitude" -name MISC_FILE [file join $::quartus(sip_path) "complex_magnitude_sim/complex_magnitude_memoryC2_uid199_sqrtTables_lutmem.hex"]
set_global_assignment -library "lib_complex_magnitude" -name MISC_FILE [file join $::quartus(sip_path) "complex_magnitude_sim/complex_magnitude.vo"]
