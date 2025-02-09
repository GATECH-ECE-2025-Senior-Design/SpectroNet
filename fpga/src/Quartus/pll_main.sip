set_global_assignment -entity "pll_main" -library "lib_pll_main" -name IP_TOOL_NAME "altera_pll"
set_global_assignment -entity "pll_main" -library "lib_pll_main" -name IP_TOOL_VERSION "23.1"
set_global_assignment -entity "pll_main" -library "lib_pll_main" -name IP_TOOL_ENV "mwpim"
set_global_assignment -library "lib_pll_main" -name SPD_FILE [file join $::quartus(sip_path) "pll_main.spd"]

set_global_assignment -library "lib_pll_main" -name MISC_FILE [file join $::quartus(sip_path) "pll_main_sim/pll_main.vo"]
