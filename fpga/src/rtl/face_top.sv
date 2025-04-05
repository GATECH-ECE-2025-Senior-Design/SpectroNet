module face_top # (
        parameter DATA_WIDTH = 16
    )(
        // Clocks, resets
        input logic i_clk,
        input logic i_rst,
        
        // Inputs
        input logic [DATA_WIDTH-1:0]  i_aud_data,
        input logic                   i_aud_data_valid,
        
        // Outputs
        output logic [9:0]            o_classify,
        output logic                  o_classify_valid
);

  ////////////////
  // PARAMETERS //
  ////////////////
  
  // The IP core doesn't come with a valid out port...
  parameter INT_FLT_DELAY = 2;

  /////////////
  // SIGNALS //
  /////////////

  // Reset
  logic                     i_rst_n;

  // Int -> float conversion
  logic [31:0]              aud_data_pad;
  logic [31:0]              aud_data_flt;
  logic [INT_FLT_DELAY-1:0] aud_data_valid_shift;
  logic                     aud_data_flt_valid;

  // Buffer to FFT
  logic [31:0]              buffer_dout;
  logic                     buffer_dout_valid;
  logic                     buffer_dout_ready;
  logic                     buffer_dout_sop;
  logic                     buffer_dout_eop;

  // FFT
  logic                     fft_err_in; // unused
  logic                     fft_valid_out;
  logic                     fft_err_out;
  logic                     fft_sop_out;
  logic                     fft_eop_out;
  logic [31:0]              fft_real_out;
  logic [31:0]              fft_imag_out;
  logic [9:0]               fft_pts_out;
  
  // FFT (cropped with magnitude)
  logic [31:0] fft_mag_sq_out;
  logic        fft_mag_sq_valid_out;

  // FFT Buffer
  logic [7:0]   fft_buf_wr_cntr;
  logic         fft_buf_trig;
  logic [7:0]   mel_fb_rd_addr;
  logic [31:0]  mel_fb_rd_data;
  
  // Mel filterbank
  logic [31:0]  mel_data_out;
  logic         mel_data_valid;

  ///////////
  // LOGIC //
  ///////////

  assign i_rst_n = ~i_rst;
  assign aud_data_pad = $signed(i_aud_data); // sign ext to 32 bits

  // Convert int -> float for FFT core
  int_to_float int_to_float_inst (
    .clk(i_clk),
    .areset(i_rst),
    .a(aud_data_pad),
    .q(aud_data_flt)
  );

  // Create valid signal for the int -> float conversion
  always_ff @(posedge i_clk) begin
    if (i_rst == 1) begin
      aud_data_valid_shift <= 0;
    end
    else begin
      aud_data_valid_shift <= {i_aud_data_valid, aud_data_valid_shift[INT_FLT_DELAY-1:1]};
    end
  end
  assign aud_data_flt_valid = aud_data_valid_shift[0];

  // Buffers N_FFT samples, zero pads to 512 samples
  wave_buffer_fsm # (
    .N_FFT(384),
    .HOP_LENGTH(64)
  )
  wave_buffer_fsm_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_aud_data(aud_data_flt),
    .i_aud_data_valid(aud_data_flt_valid),
    .o_buf_data(buffer_dout),
    .o_buf_data_valid(buffer_dout_valid),
    .i_buf_data_ready(buffer_dout_ready),
    .o_buf_data_sop(buffer_dout_sop),
    .o_buf_data_eop(buffer_dout_eop)
  );

  // Computes FFT, 384 input samples zero-padded to 512 samples
  fft_512 fft_512_inst (
    .clk          (i_clk),              //    clk.clk
    .reset_n      (i_rst_n),            //    rst.reset_n
    .sink_valid   (buffer_dout_valid),  //   sink.sink_valid
    .sink_ready   (buffer_dout_ready),  //       .sink_ready
    .sink_error   (1'b0),               //       .sink_error
    .sink_sop     (buffer_dout_sop),    //       .sink_sop
    .sink_eop     (buffer_dout_eop),    //       .sink_eop
    .sink_real    (buffer_dout),        //       .sink_real
    .sink_imag    (32'b0),              //       .sink_imag
    .fftpts_in    (10'd512),            //       .fftpts_in
    .source_valid (fft_valid_out),      // source.source_valid
    .source_ready (1'b1),               //       .source_ready
    .source_error (fft_err_out),        //       .source_error
    .source_sop   (fft_sop_out),        //       .source_sop
    .source_eop   (fft_eop_out),        //       .source_eop
    .source_real  (fft_real_out),       //       .source_real
    .source_imag  (fft_imag_out),       //       .source_imag
    .fftpts_out   (fft_pts_out)         //       .fftpts_out
  );

  // Get magnitude from complex output and crop to 1st-256th values (256 bins)
  magnitude_sq_conv magnitude_sq_conv_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_fft_real(fft_real_out),
    .i_fft_imag(fft_imag_out),
    .i_fft_valid(fft_valid_out),
    .i_fft_sop(fft_sop_out),     // use sop as a lazy way to make the state machine
    .o_fft_mag_sq(fft_mag_sq_out),
    .o_fft_valid(fft_mag_sq_valid_out)
  );

  // Buffer 256 frequency bins to the mel filterbank
  fft_buffer fft_buffer_inst (
    .clock(i_clk),
    .aclr(i_rst),
    .wraddress(fft_buf_wr_cntr),
    .wren(fft_mag_sq_valid_out),
    .data(fft_mag_sq_out),
    .rdaddress(mel_fb_rd_addr),
    .q(mel_fb_rd_data)
  );

  // Free-running counter (0-255) to index writes to the FFT buffer
  always_ff @(posedge i_clk)
    if (i_rst) fft_buf_wr_cntr <= 0;
    else if (fft_mag_sq_valid_out) fft_buf_wr_cntr <= fft_buf_wr_cntr + 1;

  // Trigger mel filterbank on reception of 256th FFT bin
  assign fft_buf_trig = (fft_buf_wr_cntr == 255) && fft_mag_sq_valid_out;

  // Read FFT bins from FFT buffer, apply filterbank
  // 256 bins in, 96 bins out
  mel_filterbank  mel_filterbank_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_fft_buf_trig(fft_buf_trig),
    .i_fft_buf_data(mel_fb_rd_data),
    .o_fft_buf_addr(mel_fb_rd_addr),
    .o_mel_data_out(mel_data_out),
    .o_mel_valid(mel_data_valid)
  );

  ///////////
  // DEBUG //
  ///////////
  
  // just to avoid the logic from being optimized out
  assign o_classify = mel_data_out[9:0];
  assign o_classify_valid = mel_data_valid;

endmodule