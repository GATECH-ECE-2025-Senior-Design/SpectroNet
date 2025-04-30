module mult_add_tree_tb;

  //Ports
  logic i_clk = 1;
  logic i_rst = 1;
  logic i_valid = 0;
  logic [31:0] i_val_0 = 0;
  logic [31:0] i_val_1 = 0;
  logic [31:0] i_val_2 = 0;
  logic [31:0] i_coeff_0 = 0;
  logic [31:0] i_coeff_1 = 0;
  logic [31:0] i_coeff_2 = 0;
  logic [31:0] i_base_val = 0;
  logic [7:0] i_base_addr = 0;
  logic [31:0] o_wr_data;
  logic o_wr_en;
  logic [7:0] o_wr_addr;

  mult_add_tree  mult_add_tree_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_valid(i_valid),
    .i_val_0(i_val_0),
    .i_val_1(i_val_1),
    .i_val_2(i_val_2),
    .i_coeff_0(i_coeff_0),
    .i_coeff_1(i_coeff_1),
    .i_coeff_2(i_coeff_2),
    .i_base_val(i_base_val),
    .i_base_addr(i_base_addr),
    .o_wr_data(o_wr_data),
    .o_wr_en(o_wr_en),
    .o_wr_addr(o_base_addr)
  );

always #10 i_clk = !i_clk ;

initial begin
  #100 i_rst = 0;
  @(posedge i_clk);
  i_valid = 1;
  // 1
  i_val_0 = 32'h3f800000;
  i_coeff_0 = 32'h3f800000;
  // 2
  i_val_1 = 32'h40000000;
  i_coeff_1 = 32'h40000000;
  // 3
  i_val_2 = 32'h40400000;
  i_coeff_2 = 32'h40400000;
  // 21
  i_base_val = 32'h41a80000;
  // 10
  i_base_addr = 8'h0a;
  @(posedge i_clk);
  i_valid = 0;

  #500 $finish;
end

endmodule