// multiplies 3 values by 3 coefficients,
// calculates the sum of the 3 results and base value
// all operations done in fp32
module mult_add_tree (
  // system ports
  input logic i_clk,
  input logic i_rst,
  // valid signal (gets shift-registered)
  input logic i_valid,
  // values
  input logic [31:0] i_val_0,
  input logic [31:0] i_val_1,
  input logic [31:0] i_val_2,
  // coefficients
  input logic [31:0] i_coeff_0,
  input logic [31:0] i_coeff_1,
  input logic [31:0] i_coeff_2,
  // base value
  input logic [31:0] i_base_val,
  input logic [7:0] i_base_addr,
  // outputs to mel bins
  output logic [31:0] o_wr_data,
  output logic o_wr_en,
  output logic [7:0] o_wr_addr
);

  ////////////////
  // PARAMETERS //
  ////////////////

  // floating point operations
  parameter MULT_DELAY = 2;
  parameter ADD_DELAY = 2;
  parameter FP_DELAY = MULT_DELAY + 2*ADD_DELAY;

  /////////////
  // SIGNALS //
  /////////////

  // valid signal shift register
  logic [FP_DELAY-1:0] mult_add_valid_shift;
  // base value shift register
  logic [31:0] base_val_shift [0:MULT_DELAY-1];
  // address shift register
  logic [7:0] base_addr_shift [0:FP_DELAY-1];

  // intermediate float values
  logic [31:0] mult_result_0;
  logic [31:0] mult_result_1;
  logic [31:0] mult_result_2;  
  logic [31:0] base_val;
  logic [31:0] add_result_0_1;
  logic [31:0] add_result_2_base;

  ///////////
  // LOGIC //
  ///////////

  // valid output shift register
  always_ff @(posedge i_clk)
    if (i_rst)  mult_add_valid_shift <= 0;
    else        mult_add_valid_shift <= {i_valid, mult_add_valid_shift[FP_DELAY-1:1]};
  assign o_wr_en = mult_add_valid_shift[0];

  // base value shift register
  // delay the base value through the parallel multipliers
  // since the base value doesn't get multiplied
  always_ff @(posedge i_clk) begin
    for (int i = 0; i < MULT_DELAY-1; i=i+1) begin
      base_val_shift[i] <= base_val_shift[i+1];
    end
    base_val_shift[MULT_DELAY-1] <= i_base_val;
  end
  assign base_val = base_val_shift[0];

  // address shift register
  // aligned with o_wr_data and o_wr_en to write back to the mel bins
  always_ff @(posedge i_clk) begin
    for (int i = 0; i < FP_DELAY-1; i=i+1) begin
      base_addr_shift[i] <= base_addr_shift[i+1];
    end
    base_addr_shift[FP_DELAY-1] <= i_base_addr;
  end
  assign o_wr_addr = base_addr_shift[0];

  // multiply 3 bins by 3 filter coefficients
  fp_mult fp_mult_0 (
    .clk(i_clk),
    .areset(i_rst),
    .a(i_val_0),
    .b(i_coeff_0),
    .q(mult_result_0)
  );
  fp_mult fp_mult_1 (
    .clk(i_clk),
    .areset(i_rst),
    .a(i_val_1),
    .b(i_coeff_1),
    .q(mult_result_1)
  );
  fp_mult fp_mult_2 (
    .clk(i_clk),
    .areset(i_rst),
    .a(i_val_2),
    .b(i_coeff_2),
    .q(mult_result_2)
  );

  // 4 term adder tree
  fp_add fp_add_0_1 (
    .clk(i_clk),
    .areset(i_rst),
    .a(mult_result_0),
    .b(mult_result_1),
    .q(add_result_0_1)
  );
  fp_add fp_add_2_base (
    .clk(i_clk),
    .areset(i_rst),
    .a(mult_result_2),
    .b(base_val),
    .q(add_result_2_base)
  );
  fp_add fp_add_final (
    .clk(i_clk),
    .areset(i_rst),
    .a(add_result_0_1),
    .b(add_result_2_base),
    .q(o_wr_data)
  );

endmodule