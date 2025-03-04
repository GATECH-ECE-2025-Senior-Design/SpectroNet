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
//`define ENABLE_HPS

module DE10_Standard_golden_top(

      ///////// CLOCK /////////
      input              CLOCK_50, // 50 MHz
      input              CLOCK2_50,
      input              CLOCK3_50,
      input              CLOCK4_50,

      ///////// KEY /////////
      input    [ 3: 0]   KEY,

      ///////// SW /////////
      input    [ 9: 0]   SW,

      ///////// LED /////////
      output   [ 9: 0]   LEDR,

      ///////// Seg7 /////////
      output   [ 6: 0]   HEX0,
      output   [ 6: 0]   HEX1,
      output   [ 6: 0]   HEX2,
      output   [ 6: 0]   HEX3,
      output   [ 6: 0]   HEX4,
      output   [ 6: 0]   HEX5,

      ///////// SDRAM /////////
      output             DRAM_CLK,
      output             DRAM_CKE,
      output   [12: 0]   DRAM_ADDR,
      output   [ 1: 0]   DRAM_BA,
      inout    [15: 0]   DRAM_DQ,
      output             DRAM_LDQM,
      output             DRAM_UDQM,
      output             DRAM_CS_N,
      output             DRAM_WE_N,
      output             DRAM_CAS_N,
      output             DRAM_RAS_N,

      ///////// Video-In /////////
      input              TD_CLK27,
      input              TD_HS,
      input              TD_VS,
      input    [ 7: 0]   TD_DATA,
      output             TD_RESET_N,

      ///////// VGA /////////
      output             VGA_CLK,
      output             VGA_HS,
      output             VGA_VS,
      output   [ 7: 0]   VGA_R,
      output   [ 7: 0]   VGA_G,
      output   [ 7: 0]   VGA_B,
      output             VGA_BLANK_N,
      output             VGA_SYNC_N,

      ///////// Audio /////////
      inout              AUD_BCLK,
      output             AUD_XCK,
      inout              AUD_ADCLRCK,
      input              AUD_ADCDAT,
      inout              AUD_DACLRCK,
      output             AUD_DACDAT,

      ///////// PS2 /////////
      inout              PS2_CLK,
      inout              PS2_CLK2,
      inout              PS2_DAT,
      inout              PS2_DAT2,

      ///////// ADC /////////
      output             ADC_SCLK,
      input              ADC_DOUT,
      output             ADC_DIN,
      output             ADC_CONVST,

      ///////// I2C for Audio and Video-In /////////
      output             FPGA_I2C_SCLK,
      inout              FPGA_I2C_SDAT,

      ///////// GPIO /////////
      inout    [35: 0]   GPIO,

`ifdef ENABLE_HSMC
      ///////// HSMC /////////
      input              HSMC_CLKIN_P1,
      input              HSMC_CLKIN_N1,
      input              HSMC_CLKIN_P2,
      input              HSMC_CLKIN_N2,
      output             HSMC_CLKOUT_P1,
      output             HSMC_CLKOUT_N1,
      output             HSMC_CLKOUT_P2,
      output             HSMC_CLKOUT_N2,
      inout    [16: 0]   HSMC_TX_D_P,
      inout    [16: 0]   HSMC_TX_D_N,
      inout    [16: 0]   HSMC_RX_D_P,
      inout    [16: 0]   HSMC_RX_D_N,
      input              HSMC_CLKIN0,
      output             HSMC_CLKOUT0,
      inout    [ 3: 0]   HSMC_D,
      output             HSMC_SCL,
      inout              HSMC_SDA,
`endif /*ENABLE_HSMC*/

`ifdef ENABLE_HPS
      ///////// HPS /////////
      inout              HPS_CONV_USB_N,
      output   [14: 0]   HPS_DDR3_ADDR,
      output   [ 2: 0]   HPS_DDR3_BA,
      output             HPS_DDR3_CAS_N,
      output             HPS_DDR3_CKE,
      output             HPS_DDR3_CK_N,
      output             HPS_DDR3_CK_P,
      output             HPS_DDR3_CS_N,
      output   [ 3: 0]   HPS_DDR3_DM,
      inout    [31: 0]   HPS_DDR3_DQ,
      inout    [ 3: 0]   HPS_DDR3_DQS_N,
      inout    [ 3: 0]   HPS_DDR3_DQS_P,
      output             HPS_DDR3_ODT,
      output             HPS_DDR3_RAS_N,
      output             HPS_DDR3_RESET_N,
      input              HPS_DDR3_RZQ,
      output             HPS_DDR3_WE_N,
      output             HPS_ENET_GTX_CLK,
      inout              HPS_ENET_INT_N,
      output             HPS_ENET_MDC,
      inout              HPS_ENET_MDIO,
      input              HPS_ENET_RX_CLK,
      input    [ 3: 0]   HPS_ENET_RX_DATA,
      input              HPS_ENET_RX_DV,
      output   [ 3: 0]   HPS_ENET_TX_DATA,
      output             HPS_ENET_TX_EN,
      inout    [ 3: 0]   HPS_FLASH_DATA,
      output             HPS_FLASH_DCLK,
      output             HPS_FLASH_NCSO,
      inout              HPS_GSENSOR_INT,
      inout              HPS_I2C1_SCLK,
      inout              HPS_I2C1_SDAT,
      inout              HPS_I2C2_SCLK,
      inout              HPS_I2C2_SDAT,
      inout              HPS_I2C_CONTROL,
      inout              HPS_KEY,
      inout              HPS_LCM_BK,
      inout              HPS_LCM_D_C,
      inout              HPS_LCM_RST_N,
      output             HPS_LCM_SPIM_CLK,
      output             HPS_LCM_SPIM_MOSI,
      input              HPS_LCM_SPIM_MISO,
      output             HPS_LCM_SPIM_SS,
      inout              HPS_LED,
      inout              HPS_LTC_GPIO,
      output             HPS_SD_CLK,
      inout              HPS_SD_CMD,
      inout    [ 3: 0]   HPS_SD_DATA,
      output             HPS_SPIM_CLK,
      input              HPS_SPIM_MISO,
      output             HPS_SPIM_MOSI,
      output             HPS_SPIM_SS,
      input              HPS_UART_RX,
      output             HPS_UART_TX,
      input              HPS_USB_CLKOUT,
      inout    [ 7: 0]   HPS_USB_DATA,
      input              HPS_USB_DIR,
      input              HPS_USB_NXT,
      output             HPS_USB_STP,
`endif /*ENABLE_HPS*/


      ///////// IR /////////
      output             IRDA_TXD,
      input              IRDA_RXD
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
  logic             clk_400k; // currently unused 400kHz clock
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

  //  FACE signals

  logic [9:0]       face_out;
  logic             face_out_valid;



  ///////////
  // Logic //
  ///////////

  assign sys_rst = ~sys_rst_n;
  assign sys_rst_n = rst_s2;

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
    .outclk_2(clk_400k),
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

  // Display for other values
  hex_disp  hex_disp_04_inst (
    .hex_val(4'b0000),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX4)
  );

  hex_disp  hex_disp_5_inst (
    .hex_val(4'b0000),
    .cs(CLOCK_50),
    .free(adc_data_valid),
    .resetn(sys_rst_n),
    .segments(HEX5)
  );
  
  // Display classification on 10 LEDs
  always_ff @(posedge CLOCK_50) begin
    if (sys_rst == 1) begin
      LEDR <= 0;
    end
    else begin
      LEDR[9:2] <= '0;
      LEDR[0] <= adc_data_valid;
      LEDR[1] <= AUD_XCK;
      /*
      if (face_out_valid == 1) begin
        LEDR <= face_out;
      end
      */
    end
  end

endmodule
