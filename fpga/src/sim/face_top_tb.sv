
module face_top_tb;

  // Parameters
  localparam  DATA_WIDTH = 16;

  //Ports
  reg i_clk;
  reg i_rst;
  reg [DATA_WIDTH-1:0] i_aud_data;
  reg i_aud_data_valid;
  wire [9:0] o_classify;
  wire o_classify_valid;

  face_top # (
    .DATA_WIDTH(DATA_WIDTH)
  )
  face_top_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_aud_data(i_aud_data),
    .i_aud_data_valid(i_aud_data_valid),
    .o_classify(o_classify),
    .o_classify_valid(o_classify_valid)
  );

initial begin
  i_clk = 0;
  forever begin
    #10 i_clk = ~i_clk;
  end
end

initial begin
  i_rst = 1;
  #100 i_rst = 0;
end

initial begin
  i_aud_data = 0;
  i_aud_data_valid = 0;
  @(negedge i_rst) #10;
  forever begin
    @(posedge i_clk);
    i_aud_data = i_aud_data + 1;
    i_aud_data_valid = ~i_aud_data_valid;
  end
end

endmodule