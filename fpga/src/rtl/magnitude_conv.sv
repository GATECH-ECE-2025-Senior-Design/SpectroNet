module magnitude_conv (
  // system ports
  input logic i_clk,
  input logic i_rst,
  // inputs from fft core
  input logic [31:0] i_fft_real,
  input logic [31:0] i_fft_imag,
  input logic i_fft_valid,
  input logic i_fft_sop,
  // outputs to fft buffer
  output logic [31:0] o_fft_abs,
  output logic o_fft_valid
);

  ////////////////
  // PARAMETERS //
  ////////////////

  // The IP core doesn't come with a valid out port...
  parameter MAG_CONV_DELAY = 10;

  /////////////
  // SIGNALS //
  /////////////

  // delay for complex to magnitude conversion
  logic [MAG_CONV_DELAY-1:0] fft_conv_valid_shift;
  logic fft_conv_valid_next;

  // for dropping frequency bins 
  // (cut out bins 0, 257-511, keep bins 1-256)
  logic [7:0] fft_bin_cntr;
  logic [7:0] fft_bin_cntr_r;
  logic       fft_bin_valid;

  // a simple state machine
  enum {DROP, KEEP} state, next;
  
  ///////////
  // LOGIC //
  ///////////

  // FSM
  always_ff @(posedge i_clk)
    if (i_rst)  state <= DROP;
    else        state <= next;

  // FSM comb logic
  always_comb begin
    // defaults
    next = state;

    case(state)
      DROP:
      begin
        fft_bin_valid = 0;
        fft_bin_cntr = 0;
        if (i_fft_valid && i_fft_sop) next = KEEP; // drops the 0th sample (DC)
      end

      KEEP:
      begin
        fft_bin_valid = 1;
        // counter logic
        if (i_fft_valid)  fft_bin_cntr = fft_bin_cntr_r + 1;
        else              fft_bin_cntr = fft_bin_cntr_r;
        if (fft_bin_cntr == 0) next = DROP; // collects 256 samples (1-256)
      end
    endcase
  end

  // register fft bin counter
  always_ff @(posedge i_clk)
    if (i_rst)  fft_bin_cntr_r <= 0;
    else        fft_bin_cntr_r <= fft_bin_cntr;

  complex_magnitude complex_magnitude_inst (
    .clk(i_clk),
    .areset(i_rst),
    .a(i_fft_real),
    .b(i_fft_imag),
    .c(32'd0), // No 2D hypotenuse IP, so just using 3D...
    .q(o_fft_abs)
  );

  // input has to be valid and bin has to be valid
  assign fft_conv_valid_next = i_fft_valid && fft_bin_valid;
  // valid output shift register
  always_ff @(posedge i_clk)
    if (i_rst)  fft_conv_valid_shift <= 0;
    else        fft_conv_valid_shift <= {fft_conv_valid_next, fft_conv_valid_shift[MAG_CONV_DELAY-1:1]};
  // align valid output with magnitude converter output
  assign o_fft_valid = fft_conv_valid_shift[0];
  
endmodule