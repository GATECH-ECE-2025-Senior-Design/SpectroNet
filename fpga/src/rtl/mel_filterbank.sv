module mel_filterbank (
  // system ports
  input logic i_clk,
  input logic i_rst,
  // from FFT buffer
  input  logic        i_fft_buf_trig,
  input  logic [31:0] i_fft_buf_data,
  output logic [7:0]  o_fft_buf_addr,
  // to image buffer
  output logic [31:0] o_mel_data_out,
  output logic        o_mel_valid
);

  ////////////////
  // PARAMETERS //
  ////////////////

  // Mel starting bin index for each FFT sweep
  parameter SWEEP_0_MEL_START = 0;
  parameter SWEEP_1_MEL_START = 9;
  parameter SWEEP_2_MEL_START = 70;
  parameter SWEEP_3_MEL_START = 85;

  /////////////
  // SIGNALS //
  /////////////

  // Filterbank FSM
  enum {IDLE, SWEEP0, SWEEP1, SWEEP2, SWEEP3, OUTPUT} state, next;
  logic new_state;

  // FFT buffer signals
  logic [7:0]   fft_buf_addr_next;
  logic [31:0]  fft_buf_data_r, fft_buf_data_rr;

  // Mel bins memory
  logic [6:0]   mel_bin_addr_wr;
  logic         mel_bin_wr_en;
  logic [31:0]  mel_bin_data_wr;
  logic [6:0]   mel_bin_addr_rd, mel_bin_addr_rd_r, sweep_start;
  logic [31:0]  mel_bin_data_rd, mel_bin_data_rd_mux;

  // Filterbank coefficients
  logic [7:0]   fb_coeffs_idx, fb_coeffs_idx_r;
  logic [95:0]  fb_coeffs_data;

  // Filterbank trigger condition
  logic [7:0] fb_trig_idx;
  logic [3:0] fb_trig_data;
  logic       fb_trig;

  // Multiply-add tree
  logic [31:0]  coeff_0, coeff_1, coeff_2;
  logic         mult_add_valid;

  ///////////
  // LOGIC //
  ///////////

  // FSM next state
  always_ff @(posedge i_clk)
    if (i_rst)  state <= IDLE;
    else        state <= next;
      
  // FSM comb logic
  always_comb begin
    // defaults
    next = state;
    fft_buf_addr_next = o_fft_buf_addr + 1;
    fb_trig = 0;
    sweep_start = 0;

    case(state)
      IDLE:
      begin
        fft_buf_addr_next = 0;
        if (i_fft_buf_trig) begin
          next = SWEEP0;
        end
      end

      SWEEP0:
      begin
        sweep_start = SWEEP_0_MEL_START;
        fb_trig = fb_trig_data[0];
        if (o_fft_buf_addr == 255) begin
          next = SWEEP1;
        end
      end

      SWEEP1:
      begin
        sweep_start = SWEEP_1_MEL_START;
        fb_trig = fb_trig_data[1];
        if (o_fft_buf_addr == 255) begin
          next = SWEEP2;
        end
      end

      SWEEP2:
      begin
        sweep_start = SWEEP_2_MEL_START;
        fb_trig = fb_trig_data[2];
        if (o_fft_buf_addr == 255) begin
          next = SWEEP3;
        end
      end

      SWEEP3:
      begin
        sweep_start = SWEEP_3_MEL_START;
        fb_trig = fb_trig_data[3];
        if (o_fft_buf_addr == 255) begin
          next = OUTPUT;
        end
      end

      OUTPUT:
      begin
        // Not a sweep, but we are outputting the mel bins from 0-95
        sweep_start = 0;
        fb_trig = 1;
        fft_buf_addr_next = 0;
      end
    endcase

    // Mel bin indexing logic
    if (new_state)        
      mel_bin_addr_rd = sweep_start;
    else if (fb_trig) 
      mel_bin_addr_rd = mel_bin_addr_rd_r + 1;
    else                
      mel_bin_addr_rd = mel_bin_addr_rd_r;

    // Coefficient indexing logic
    if (fb_trig) 
      fb_coeffs_idx = fb_coeffs_idx_r + 1;
    else if (state == IDLE || state == OUTPUT) 
      fb_coeffs_idx = 0;
    else 
      fb_coeffs_idx = fb_coeffs_idx_r;

      // this code is truly awful and I must apologize
      if (state == OUTPUT && mel_bin_addr_rd == 95) begin
        next = IDLE;
      end
  end

  // FFT buffer data shift register
  always_ff @(posedge i_clk) begin
    fft_buf_data_r  <= i_fft_buf_data;
    fft_buf_data_rr <= fft_buf_data_r;
  end

  // registers
  always_ff @(posedge i_clk) begin
    if (i_rst) begin
      mel_bin_addr_rd_r <= 0;
      fb_coeffs_idx_r   <= 0;
      new_state         <= 0;
      o_fft_buf_addr    <= 0;
    end
    else begin
      mel_bin_addr_rd_r <= mel_bin_addr_rd;
      fb_coeffs_idx_r   <= fb_coeffs_idx;
      new_state         <= (state != next);
      o_fft_buf_addr    <= fft_buf_addr_next;
    end
  end

  ///////////////
  // INSTANCES //
  ///////////////

  mult_add_tree mult_add_tree_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    .i_valid(mult_add_valid),
    .i_val_0(fft_buf_data_rr), // oldest
    .i_val_1(fft_buf_data_r),
    .i_val_2(i_fft_buf_data), // newest
    .i_coeff_0(coeff_0), // oldest
    .i_coeff_1(coeff_1),
    .i_coeff_2(coeff_2), // newest
    .i_base_val(mel_bin_data_rd_mux),
    .i_base_addr(mel_bin_addr_rd_r),
    .o_wr_data(mel_bin_data_wr),  // to intenal memory
    .o_wr_en(mel_bin_wr_en),      // to internal memory
    .o_wr_addr(mel_bin_addr_wr)   // to internal memory
  );
  // unpack for readability
  assign coeff_2 = fb_coeffs_data[95:64];
  assign coeff_1 = fb_coeffs_data[63:32];
  assign coeff_0 = fb_coeffs_data[31:0];
  // we don't want any writing when the memory is bursted out
  assign mult_add_valid = fb_trig && (state != OUTPUT);
  // during the first sweep, we want the base value to be 0 (reset mel bins)
  assign mel_bin_data_rd_mux = (state == SWEEP0) ? 0 : mel_bin_data_rd;

  // 96 mel bins (fp32)
  mel_bins_mem mel_bins_mem_inst (
    .clock(i_clk),
    .wraddress(mel_bin_addr_wr),
    .wren(mel_bin_wr_en),
    .data(mel_bin_data_wr),
    .rdaddress(mel_bin_addr_rd),
    .q(mel_bin_data_rd)
  );
  // always assigned to out, but we also have a valid signal
  assign o_mel_data_out = mel_bin_data_rd;
  // reads are only valid when we read in the OUTPUT state
  // flopped to match read delay
  always_ff @(posedge i_clk) o_mel_valid <= (state == OUTPUT);

  filterbank_coeffs filterbank_coeffs_inst (
    .clock(i_clk),
    .address(fb_coeffs_idx),
    .q(fb_coeffs_data)
  );

  filterbank_trigs fb_trig_inst (
    .clock(i_clk),
    .address(fb_trig_idx),
    .q(fb_trig_data)
  );
  // we are reading the same indices from the trigger LUT as from the FFT buffer
  assign fb_trig_idx = o_fft_buf_addr;

endmodule