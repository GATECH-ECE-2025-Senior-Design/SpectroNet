set_global_assignment -entity "ADC_controller" -library "lib_ADC_controller" -name IP_TOOL_NAME "Qsys"
set_global_assignment -entity "ADC_controller" -library "lib_ADC_controller" -name IP_TOOL_VERSION "23.1"
set_global_assignment -entity "ADC_controller" -library "lib_ADC_controller" -name IP_TOOL_ENV "Qsys"
set_global_assignment -library "lib_ADC_controller" -name SPD_FILE [file join $::quartus(sip_path) "../ADC_controller.spd"]
set_global_assignment -library "lib_ADC_controller" -name MISC_FILE [file join $::quartus(sip_path) "../../ADC_controller.qsys"]

set_global_assignment -library "lib_ADC_controller" -name MISC_FILE [file join $::quartus(sip_path) "ADC_controller.v"]
set_global_assignment -library "lib_ADC_controller" -name MISC_FILE [file join $::quartus(sip_path) "submodules/altera_up_avalon_adv_adc.v"]
set_global_assignment -library "lib_ADC_controller" -name MISC_FILE [file join $::quartus(sip_path) "submodules/ADC_controller_adc_mega_0.v"]
