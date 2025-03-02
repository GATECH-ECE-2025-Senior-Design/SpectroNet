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
  logic                   i_rst_n;

  // Int -> float conversion
  logic [31:0]            aud_data_flt;
  logic [INT_FLT_DELAY:0] aud_data_valid_shift;
  logic                   aud_data_flt_valid;

  // Buffer to FFT
  logic [31:0]            fifo_dout;
  logic                   fifo_dout_valid;
  logic                   fifo_dout_ready;
  logic                   fifo_empty;
  logic                   fifo_full; // open
  
  // FFT
  logic [8:0]             fft_sample_cntr;
  logic                   fft_sop_in;
  logic                   fft_eop_in;
  
  
  ///////////
  // LOGIC //
  ///////////

  assign i_rst_n = ~i_rst;

  // Convert int -> float for FFT core
  int_to_float int_to_float_inst (
    .clk(i_clk),
    .areset(i_rst),
    .a(i_aud_data),
    .q(aud_data_flt)
  );

  // Create valid signal for the int -> float conversion
  always_ff @(posedge i_clk) begin
    if (i_rst == 1) begin
      aud_data_valid_shift <= 0;
    end
    else begin
      aud_data_valid_shift <= {i_aud_data_valid, aud_data_valid_shift[INT_FLT_DELAY:1]};
    end
  end
  assign aud_data_flt_valid = aud_data_valid_shift[0];

  // Buffer the audio data until FFT core is ready
  aud_data_buffer aud_data_buffer_inst (
    .clock(i_clk),                //input, width = 1
    .data (aud_data_flt),         //input, width = DATA_WIDTH
    .rdreq(fifo_dout_ready),      //input, width = 1
    .sclr(i_rst),                 //input, width = 1, synch reset
    .wrreq(fifo_dout_ready),      //input, width = 1
    .q(fifo_dout),                //output, width = DATA_WIDTH
    .usedw(/*fft_sample_cntr*/),      //output, width = ADDR_WIDTH
    .empty(fifo_empty),           //output, width = 1
    .full(fifo_full)              //output, width = 1
  );

  assign fifo_dout_valid = fifo_dout_ready && ~fifo_empty;

  fft_512 fft_512_inst (
    .clk          (i_clk),              //    clk.clk
    .reset_n      (i_rst_n),            //    rst.reset_n
    .sink_valid   (fifo_dout_valid),    //   sink.sink_valid
    .sink_ready   (fifo_dout_ready),    //       .sink_ready
    .sink_error   (),                   //       .sink_error
    .sink_sop     (fft_sop_in),         //       .sink_sop
    .sink_eop     (fft_eop_in),         //       .sink_eop
    .sink_real    (fifo_dout),          //       .sink_real
    .sink_imag    (32'd0),              //       .sink_imag
    .fftpts_in    (10'd512),            //       .fftpts_in
    .source_valid (),                   // source.source_valid
    .source_ready (1'b1),               //       .source_ready
    .source_error (),                   //       .source_error
    .source_sop   (),                   //       .source_sop
    .source_eop   (),                   //       .source_eop
    .source_real  (),                   //       .source_real
    .source_imag  (),                   //       .source_imag
    .fftpts_out   ()                    //       .fftpts_out
  );
  
  // Track samples going into the FFT core & handle SoP, EoP
  always_ff @(posedge i_clk) begin
    if (i_rst == 1) begin
      fft_sample_cntr <= 0;
    end
    else begin
      if (fifo_dout_valid && fifo_dout_ready) begin
        fft_sample_cntr <= fft_sample_cntr + 1;
      end
    end
  end
  // Constant 512 point FFT, could make variable/interleaved later.
  assign fft_sop_in = (fft_sample_cntr == 0) && fifo_dout_valid;
  assign fft_eop_in = (fft_sample_cntr == 511) && fifo_dout_valid;
  
  ///////////
  // DEBUG //
  ///////////
  
  assign o_classify = 10'd1;
  assign o_classify_valid = 1;

endmodule