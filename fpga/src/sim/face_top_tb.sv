`timescale 1ns/1ns
module face_top_tb;

  // parameters
  localparam DATA_WIDTH = 32;
  // 800k sample rate to make sims run faster
  // means that the processing logic has 60*32 = 2,000 clock cycles
  localparam real SAMPLE_RATE_HZ = 100 * 8000.0; 
  localparam real SAMPLE_PERIOD_NS = 1_000_000_000 / SAMPLE_RATE_HZ;

  // ports
  reg i_clk;
  reg i_rst;
  reg [DATA_WIDTH-1:0] i_aud_data;
  reg i_aud_data_valid;
  wire [9:0] o_classify;
  wire o_classify_valid;

  // test vectors
  logic [31:0] wave_arr [0:8191];
  logic [12:0] wave_arr_idx;

  // input/output files
  int file1;
  int file2;
  initial begin
    $readmemh("C:/Users/irowd/Downloads/Git/SpectroNet/fpga/src/sim/0_01_0.txt", wave_arr);
    file1 = $fopen("C:/Users/irowd/Downloads/Git/SpectroNet/fpga/src/sim/spec_out.txt", "w");
    file2 = $fopen("C:/Users/irowd/Downloads/Git/SpectroNet/fpga/src/sim/mel_out.txt", "w");
  end
  always_ff @(posedge i_clk) begin
    if (face_top_inst.fft_mag_sq_valid_out) begin
      $fwrite(file1, "%08x\n", face_top_inst.fft_mag_sq_out & 32'hFFFFFFFF);
    end
  end
  always_ff @(posedge i_clk) begin
    if (face_top_inst.mel_data_valid) begin
      $fwrite(file2, "%08x\n", face_top_inst.mel_data_out & 32'hFFFFFFFF);
    end
  end

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

assign i_aud_data = wave_arr[wave_arr_idx];
initial begin
  i_aud_data_valid = 0;
  wave_arr_idx = 0;
  @(negedge i_rst) #10;

  repeat(8192) begin
    #(SAMPLE_PERIOD_NS);

    @(posedge i_clk);
    i_aud_data_valid = 1;

    @(posedge i_clk);
    i_aud_data_valid = 0;
    wave_arr_idx = wave_arr_idx + 1;

  end

  @(posedge face_top_inst.fft_eop_out);
  repeat(2000) // give mel spectrogram processing time
    @(posedge i_clk);
  $fclose(file1);
  $fclose(file2);
  $finish;

end

// initial begin

//   i_aud_data = 0;
//   i_aud_data_valid = 0;
//   @(negedge i_rst) #10;

//   repeat(5) begin
//     repeat(384) begin
//       @(posedge i_clk);
//       i_aud_data = i_aud_data + 1;
//       i_aud_data_valid = 1;
//     end
//     @(posedge i_clk) i_aud_data_valid = 0;
//     repeat(2000) @(posedge i_clk);
//   end

// end

endmodule