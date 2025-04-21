// ============================================================================
// Copyright (c) 2016 by Terasic Technologies Inc.
// ============================================================================
//
// Permission:
//
//   Terasic grants permission to use and modify this code for use
//   in synthesis for all Terasic Development Boards and Altera Development 
//   Kits made by Terasic.  Other use of this code, including the selling 
//   ,duplication, or modification of any portion is strictly prohibited.
//
// Disclaimer:
//
//   This VHDL/Verilog or C/C++ source code is intended as a design reference
//   which illustrates how these types of functions can be implemented.
//   It is the user's responsibility to verify their design for
//   consistency and functionality through the use of formal
//   verification methods.  Terasic provides no warranty regarding the use 
//   or functionality of this code.
//
// ============================================================================
//           
//  Terasic Technologies Inc
//  9F., No.176, Sec.2, Gongdao 5th Rd, East Dist, Hsinchu City, 30070. Taiwan
//  
//  
//                     web: http://www.terasic.com/  
//                     email: support@terasic.com
//
// ============================================================================
//Date:  Thu Nov  3 15:01:20 2016
// ============================================================================

//`define ENABLE_HSMC
`define ENABLE_HPS

module DE10_Standard_golden_top(

      ///////// CLOCK /////////
      input logic             CLOCK_50, // 50 MHz
      input logic             CLOCK2_50,
      input logic             CLOCK3_50,
      input logic             CLOCK4_50,

      ///////// KEY /////////
      input logic   [ 3: 0]   KEY,

      ///////// SW /////////
      input logic   [ 9: 0]   SW,

      ///////// LED /////////
      output logic  [ 9: 0]   LEDR,

      ///////// Seg7 /////////
      output logic  [ 6: 0]   HEX0,
      output logic  [ 6: 0]   HEX1,
      output logic  [ 6: 0]   HEX2,
      output logic  [ 6: 0]   HEX3,
      output logic  [ 6: 0]   HEX4,
      output logic  [ 6: 0]   HEX5,

      ///////// SDRAM /////////
      output logic            DRAM_CLK,
      output logic            DRAM_CKE,
      output logic  [12: 0]   DRAM_ADDR,
      output logic  [ 1: 0]   DRAM_BA,
      inout  logic  [15: 0]   DRAM_DQ,
      output logic            DRAM_LDQM,
      output logic            DRAM_UDQM,
      output logic            DRAM_CS_N,
      output logic            DRAM_WE_N,
      output logic            DRAM_CAS_N,
      output logic            DRAM_RAS_N,

      ///////// Video-In /////////
      input  logic            TD_CLK27,
      input  logic            TD_HS,
      input  logic            TD_VS,
      input  logic  [ 7: 0]   TD_DATA,
      output logic            TD_RESET_N,

      ///////// VGA /////////
      output logic            VGA_CLK,
      output logic            VGA_HS,
      output logic            VGA_VS,
      output logic  [ 7: 0]   VGA_R,
      output logic  [ 7: 0]   VGA_G,
      output logic  [ 7: 0]   VGA_B,
      output logic            VGA_BLANK_N,
      output logic            VGA_SYNC_N,

      ///////// Audio /////////
      inout  logic            AUD_BCLK,
      output logic            AUD_XCK,
      inout  logic            AUD_ADCLRCK,
      input  logic            AUD_ADCDAT,
      inout  logic            AUD_DACLRCK,
      output logic            AUD_DACDAT,

      ///////// PS2 /////////
      inout logic             PS2_CLK,
      inout logic             PS2_CLK2,
      inout logic             PS2_DAT,
      inout logic             PS2_DAT2,

      ///////// ADC /////////
      output logic            ADC_SCLK,
      input  logic            ADC_DOUT,
      output logic            ADC_DIN,
      output logic            ADC_CONVST,

      ///////// I2C for Audio and Video-In /////////
      output logic            FPGA_I2C_SCLK,
      inout  logic            FPGA_I2C_SDAT,

      ///////// GPIO /////////
      inout logic   [35: 0]   GPIO,

`ifdef ENABLE_HSMC
      ///////// HSMC /////////
      input  logic            HSMC_CLKIN_P1,
      input  logic            HSMC_CLKIN_N1,
      input  logic            HSMC_CLKIN_P2,
      input  logic            HSMC_CLKIN_N2,
      output logic            HSMC_CLKOUT_P1,
      output logic            HSMC_CLKOUT_N1,
      output logic            HSMC_CLKOUT_P2,
      output logic            HSMC_CLKOUT_N2,
      inout  logic  [16: 0]   HSMC_TX_D_P,
      inout  logic  [16: 0]   HSMC_TX_D_N,
      inout  logic  [16: 0]   HSMC_RX_D_P,
      inout  logic  [16: 0]   HSMC_RX_D_N,
      input  logic            HSMC_CLKIN0,
      output logic            HSMC_CLKOUT0,
      inout  logic  [ 3: 0]   HSMC_D,
      output logic            HSMC_SCL,
      inout  logic            HSMC_SDA,
`endif /*ENABLE_HSMC*/

`ifdef ENABLE_HPS
      ///////// HPS /////////
      inout  logic            HPS_CONV_USB_N,
      output logic  [14: 0]   HPS_DDR3_ADDR,
      output logic  [ 2: 0]   HPS_DDR3_BA,
      output logic            HPS_DDR3_CAS_N,
      output logic            HPS_DDR3_CKE,
      output logic            HPS_DDR3_CK_N,
      output logic            HPS_DDR3_CK_P,
      output logic            HPS_DDR3_CS_N,
      output logic  [ 3: 0]   HPS_DDR3_DM,
      inout  logic  [31: 0]   HPS_DDR3_DQ,
      inout  logic  [ 3: 0]   HPS_DDR3_DQS_N,
      inout  logic  [ 3: 0]   HPS_DDR3_DQS_P,
      output logic            HPS_DDR3_ODT,
      output logic            HPS_DDR3_RAS_N,
      output logic            HPS_DDR3_RESET_N,
      input  logic            HPS_DDR3_RZQ,
      output logic            HPS_DDR3_WE_N,
      output logic            HPS_ENET_GTX_CLK,
      inout  logic            HPS_ENET_INT_N,
      output logic            HPS_ENET_MDC,
      inout  logic            HPS_ENET_MDIO,
      input  logic            HPS_ENET_RX_CLK,
      input  logic  [ 3: 0]   HPS_ENET_RX_DATA,
      input  logic            HPS_ENET_RX_DV,
      output logic  [ 3: 0]   HPS_ENET_TX_DATA,
      output logic            HPS_ENET_TX_EN,
      inout  logic  [ 3: 0]   HPS_FLASH_DATA,
      output logic            HPS_FLASH_DCLK,
      output logic            HPS_FLASH_NCSO,
      inout  logic            HPS_GSENSOR_INT,
      inout  logic            HPS_I2C1_SCLK,
      inout  logic            HPS_I2C1_SDAT,
      inout  logic            HPS_I2C2_SCLK,
      inout  logic            HPS_I2C2_SDAT,
      inout  logic            HPS_I2C_CONTROL,
      inout  logic            HPS_KEY,
      inout  logic            HPS_LCM_BK,
      inout  logic            HPS_LCM_D_C,
      inout  logic            HPS_LCM_RST_N,
      output logic            HPS_LCM_SPIM_CLK,
      output logic            HPS_LCM_SPIM_MOSI,
      input  logic            HPS_LCM_SPIM_MISO,
      output logic            HPS_LCM_SPIM_SS,
      inout  logic            HPS_LED,
      inout  logic            HPS_LTC_GPIO,
      output logic            HPS_SD_CLK,
      inout  logic            HPS_SD_CMD,
      inout  logic  [ 3: 0]   HPS_SD_DATA,
      output logic            HPS_SPIM_CLK,
      input  logic            HPS_SPIM_MISO,
      output logic            HPS_SPIM_MOSI,
      output logic            HPS_SPIM_SS,
      inout  logic            HPS_UART_RX, // declared inout for synthesis but use carefully
      inout  logic            HPS_UART_TX, // declared inout for synthesis but use carefully
      input  logic            HPS_USB_CLKOUT,
      inout  logic  [ 7: 0]   HPS_USB_DATA,
      input  logic            HPS_USB_DIR,
      input  logic            HPS_USB_NXT,
      output logic            HPS_USB_STP,
`endif /*ENABLE_HPS*/


      ///////// IR /////////
      output logic            IRDA_TXD,
      input  logic            IRDA_RXD
);

  ////////////////
  // PARAMETERS //
  ////////////////

  parameter ADC_WIDTH = 16;

  /////////////
  // SIGNALS //
  /////////////

  // Internal reset
  logic             rst_s1, rst_s2; // reset synch stages
  logic             sys_rst;
  logic             sys_rst_n;

  // Internal clocks
  logic             clk_adc;  // 12MHz clock for the audio CODEC
  logic             pll_locked;

  // Mic signals
  logic [15:0]      adc_data;
  logic             adc_data_valid;
 
  // I2C signals
  logic             i2c_busy;
  logic [7:0]       i2c_addr;
  logic [7:0]       i2c_data_wr;
  logic [7:0]       i2c_data_rd;  // open
  logic             i2c_ack_err;  // open
  logic             i2c_cmd_valid;

  //  FACE signals -- :(
  logic [9:0]       face_out;
  logic             face_out_valid;

  // Pin borrowing -- credit to https://github.com/truhy/loanio_uart,
  // (different pins for DE10-Standard than DE10-Nano)
  logic [66:0] loanio_oe;     // Pin direction: 0 = input, 1 = output
  logic [66:0] loanio_in;	    // Read port from pins: 1 = high, 0 = low
  logic [66:0] loanio_out;    // Write port to pins: 1 = high, 0 = low

  // UART signals
  logic uart_rx, uart_tx;
  
  // HPS reset
  logic hps_rst_n;

  ///////////
  // Logic //
  ///////////

  // resets
  assign sys_rst_n = rst_s2 && hps_rst_n;
  assign sys_rst = ~sys_rst_n;
  
  // uart
  assign uart_rx = loanio_in[49];
  assign loanio_out[50] = uart_tx;

  // HPS pins
  assign loanio_oe[48:0] = 0;   // default unused pins to input
  assign loanio_oe[49] = 0;     // UART RX is an input
  assign loanio_oe[50] = 1;     // UART TX is an output
  assign loanio_oe[66:51] = 0;  // default unused pins to input
  
  // 2 flop sync the reset from an active low KEY[0]
  always_ff @(posedge CLOCK_50) begin
    rst_s2 <= rst_s1;
    rst_s1 <= KEY[0];
  end

  // PLL for the CODEC clock
  pll_main pll_main_inst (
    .refclk(CLOCK_50),
    .rst(sys_rst),
    .outclk_0(clk_adc),
    .locked(pll_locked)
  );
  assign AUD_XCK = clk_adc;

  // Mic input --> 16 bit audio out.
  // Can be configured to 24 bit via I2C.
  // 32 bit configuration is just zero-padded 24 bit.
  adc_interface # (
    .ADC_WIDTH(ADC_WIDTH)
  )
  adc_interface_inst (
    .i_adc_wclk(AUD_ADCLRCK),
    .i_adc_bclk(AUD_BCLK),
    .i_adc_dat(AUD_ADCDAT),
    .i_poll_clk(AUD_XCK), // 12MHz, changed from CLOCK_50
    .o_adc_dat(adc_data),
    .o_sample_rdy(adc_data_valid)
  );

  // State Machine to Configure WM8731
  i2c_oneshot_ctrl  i2c_oneshot_ctrl_inst (
    .resetn(sys_rst_n),
    .clk(CLOCK_50),
    .i2c_busy(i2c_busy),
    .tx_addr(i2c_addr),
    .tx_byte(i2c_data_wr),
    .comm_en(i2c_cmd_valid)
  );

  // I2C Master for WM8731 Control
  i2c_master # (
    .input_clk(50_000_000),
    .bus_clk(100_000)
  )
  i2c_master_inst (
    .clk(CLOCK_50),
    .reset_n(sys_rst_n),
    .ena(i2c_cmd_valid),
    .addr(i2c_addr[7:1]),
    .rw(1'b0), // write only
    .data_wr(i2c_data_wr),
    .busy(i2c_busy),
    .data_rd(i2c_data_rd),  // open
    .ack_error(i2c_ack_err),  // open
    .sda(FPGA_I2C_SDAT),
    .scl(FPGA_I2C_SCLK)
  );
  
  // FPGA Audio Classification Engine
  face_top #(
    .DATA_WIDTH(ADC_WIDTH)
  )
  face_top_inst (
    .i_clk(CLOCK_50),
    .i_rst(sys_rst),
    .i_aud_data(adc_data),
    .i_aud_data_valid(adc_data_valid),
    .o_classify(face_out),
    .o_classify_valid(face_out_valid)
  );

  ///////////
  // DEBUG //
  ///////////
  
  // Display raw audio as four 7-segs
  hex_disp  hex_disp_3_inst (
    .hex_val(adc_data[15:12]),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX3)
  );

  hex_disp  hex_disp_2_inst (
    .hex_val(adc_data[11:8]),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX2)
  );

  hex_disp  hex_disp_1_inst (
    .hex_val(adc_data[7:4]),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX1)
  );

  hex_disp  hex_disp_0_inst (
    .hex_val(adc_data[3:0]),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX0)
  );

  // Displaying mel energies to prevent it from being optimized out
  hex_disp  hex_disp_5_inst (
    .hex_val(face_out[7:4]),
    .cs(CLOCK_50),
    .free(face_out_valid),
    .resetn(sys_rst_n),
    .segments(HEX5)
  );
  
  hex_disp  hex_disp_4_inst (
    .hex_val(face_out[3:0]),
    .cs(CLOCK_50),
    .free(face_out_valid),
    .resetn(sys_rst_n),
    .segments(HEX4)
  );

  // UART + FIFO for mel energy output
  uart_debug uart_debug_inst (
    .i_clk(i_clk),
    .i_rst(sys_rst),
    .i_data(face_out[7:0]), // mel energy exponents
    .i_data_valid(face_out_valid),
    .i_uart_rx(uart_rx), // unused
    .o_uart_tx(uart_tx) // stream out mel energy exponents
  );
  
  // for UART-USB bridge pin borrowing
  hps u0 (
      .clk_clk                          (CLOCK_50),                   //               clk.clk
      .hps_0_h2f_loan_io_in             (loanio_in),                  // hps_0_h2f_loan_io.in
      .hps_0_h2f_loan_io_out            (loanio_out),                 //                  .out
      .hps_0_h2f_loan_io_oe             (loanio_oe),                  //                  .oe
      .hps_0_h2f_reset_reset_n          (hps_rst_n),                    //   hps_0_h2f_reset.reset_n
      .hps_io_hps_io_gpio_inst_LOANIO49 (HPS_UART_RX),                //            hps_io.hps_io_gpio_inst_LOANIO61
      .hps_io_hps_io_gpio_inst_LOANIO50 (HPS_UART_TX),                //                  .hps_io_gpio_inst_LOANIO62
      .memory_mem_a                     (HPS_DDR3_ADDR),              //            memory.mem_a
      .memory_mem_ba                    (HPS_DDR3_BA),                //                  .mem_ba
      .memory_mem_ck                    (HPS_DDR3_CK_P),              //                  .mem_ck
      .memory_mem_ck_n                  (HPS_DDR3_CK_N),              //                  .mem_ck_n
      .memory_mem_cke                   (HPS_DDR3_CKE),               //                  .mem_cke
      .memory_mem_cs_n                  (HPS_DDR3_CS_N),              //                  .mem_cs_n
      .memory_mem_ras_n                 (HPS_DDR3_RAS_N),             //                  .mem_ras_n
      .memory_mem_cas_n                 (HPS_DDR3_CAS_N),             //                  .mem_cas_n
      .memory_mem_we_n                  (HPS_DDR3_WE_N),              //                  .mem_we_n
      .memory_mem_reset_n               (HPS_DDR3_RESET_N),           //                  .mem_reset_n
      .memory_mem_dq                    (HPS_DDR3_DQ),                //                  .mem_dq
      .memory_mem_dqs                   (HPS_DDR3_DQS_P),             //                  .mem_dqs
      .memory_mem_dqs_n                 (HPS_DDR3_DQS_N),             //                  .mem_dqs_n
      .memory_mem_odt                   (HPS_DDR3_ODT),               //                  .mem_odt
      .memory_mem_dm                    (HPS_DDR3_DM),                //                  .mem_dm
      .memory_oct_rzqin                 (HPS_DDR3_RZQ),               //                  .oct_rzqin
      .reset_reset_n                    (hps_rst_n)                     //             reset.reset_n
  );

endmodule
