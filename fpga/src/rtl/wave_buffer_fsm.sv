// Buffers data to send to FFT core.
// Parameterized samples per DFT & hop length.
module wave_buffer_fsm # (
        parameter N_FFT = 384,
        parameter HOP_LENGTH = 64
    )(
        // Clocks, resets
        input logic i_clk,
        input logic i_rst,

        // Inputs
        input logic [31:0]            i_aud_data,
        input logic                   i_aud_data_valid,

        // Outputs
        output logic [31:0]           o_buf_data,
        output logic                  o_buf_data_valid,
        input logic                   i_buf_data_ready,
        
        // Avalon-ST
        output logic                  o_buf_data_sop,
        output logic                  o_buf_data_eop
);

////////////////
// PARAMETERS //
////////////////

parameter TRIG_BITS = $clog2(HOP_LENGTH);
parameter ZERO_PAD = 2 ** $clog2(N_FFT) - N_FFT;
parameter ZERO_PAD_BITS = $clog2(ZERO_PAD);

/////////////
// SIGNALS //
/////////////

// Buffer signals
logic [8:0]   wr_ptr;
logic [8:0]   rd_ptr;
logic [31:0]  buffer_data;

// Buffer must collect N_FFT samples before output can be valid
logic       buffer_sat_trig;
logic       buffer_sat_latch;
logic       buffer_sat;

// Trigger a N_FFT sample dump to the FFT core (only if buffer_ready)
logic [TRIG_BITS-1:0] buffer_trig_cntr, buffer_trig_cntr_next;
logic                 buffer_trig;

// Output FSM
enum {IDLE, TRANSMIT, Z_PAD} state, next;
logic [8:0] rd_ptr_start;
logic [8:0] rd_ptr_stop;
logic [8:0] rd_ptr_next;
logic       xmit_fsm_sop;
logic       xmit_fsm_eop;
logic [ZERO_PAD_BITS-1:0] zero_pad_cntr, zero_pad_cntr_next;

// Handshake buffer signals
logic       xmit_fsm_ready;
logic       xmit_fsm_valid;
logic [1:0] xmit_fsm_sop_eop;
logic [1:0] buffer_sop_eop;

///////////////
// INSTANCES //
///////////////

wave_buffer wave_buffer_inst (
	.clock(i_clk),
	.data(i_aud_data),
	.rdaddress(rd_ptr),
	.wraddress(wr_ptr),
	.wren(i_aud_data_valid),
	.q(buffer_data)
);

handshake_buffer #(
  .OPT_WIDTH(2)
) handshake_buffer_inst (
    .i_clk(i_clk),
    .i_rst(i_rst),
    // sender is the wave buffer
    .i_valid_sndr(xmit_fsm_valid),
    .o_ready_sndr(xmit_fsm_ready),
    // receiver is the fft core
    .o_valid_rcvr(o_buf_data_valid),
    .i_ready_rcvr(i_buf_data_ready),
    // sop and eop signals
    .i_opt(xmit_fsm_sop_eop),
    .o_opt(buffer_sop_eop)
  );

///////////
// LOGIC //
///////////

// New sample logic
always_ff @(posedge i_clk)
  if (i_rst == 1) wr_ptr <= 0;
  // Free-running: wraps from 511 -> 0
  else if (i_aud_data_valid == 1) wr_ptr <= wr_ptr + 1;

// Buffer saturation logic
always_ff @(posedge i_clk)
  // Need to fill buffer to N_FFT after a reset for a full window
  if (i_rst == 1) buffer_sat_latch <= 0;
  // This is latched intentionally (only care about hop size after)
  else if (buffer_sat_trig) buffer_sat_latch <= 1;
// Reception of N_FFT-th signal
assign buffer_sat_trig = (wr_ptr == (N_FFT-1) && i_aud_data_valid);
assign buffer_sat = buffer_sat_trig || buffer_sat_latch;

// Buffer trigger logic
always_ff @(posedge i_clk)
    if (i_rst == 1) buffer_trig_cntr <= 0;
    // Free-running: wraps from HOP_LENGTH-1 -> 0
    else if (i_aud_data_valid) buffer_trig_cntr <= buffer_trig_cntr_next;
// To make the counter wrap to 0 after HOP_LENGTH-1
assign buffer_trig_cntr_next = (buffer_trig_cntr == HOP_LENGTH-1) ? 0 : buffer_trig_cntr + 1;
// Reception of HOP_LENGTH-th signal
assign buffer_trig = (buffer_trig_cntr == (HOP_LENGTH-1) && i_aud_data_valid);

// Transmit FSM
always_ff @(posedge i_clk)
  if (i_rst == 1) state <= IDLE;
  else state <= next;

// FSM comb logic
always_comb begin
  // defaults
  xmit_fsm_sop = 0;
  xmit_fsm_eop = 0;
  zero_pad_cntr_next = 0;
  next = state;
  o_buf_data = 0;
  rd_ptr_next = wr_ptr - N_FFT + 1;

  case(state)
    IDLE:
    begin
      xmit_fsm_valid = 0;
      // buffer trigger & valid
      if (buffer_sat && buffer_trig) next = TRANSMIT;
    end

    TRANSMIT:
    begin
      xmit_fsm_valid = 1;
      o_buf_data = buffer_data;
      // read pointer logic
      if (xmit_fsm_ready) rd_ptr_next = rd_ptr + 1;
      else                rd_ptr_next = rd_ptr;
      // start of packet
      if (rd_ptr == rd_ptr_start) xmit_fsm_sop = 1;
      // final handshake
      if ((rd_ptr == rd_ptr_stop) && xmit_fsm_ready) next = Z_PAD;
    end

    Z_PAD:
    begin
      xmit_fsm_valid = 1;
      // band-aid solution -- keep buffer_data for the first handshake so last sample doesn't drop
      if (zero_pad_cntr == 0) o_buf_data = buffer_data;
      // count to ZERO_PAD samples
      zero_pad_cntr_next = zero_pad_cntr + 1;
      // end of packet
      if (zero_pad_cntr == ZERO_PAD-1) xmit_fsm_eop = 1;
      // final handshake
      if ((zero_pad_cntr == ZERO_PAD-1) && xmit_fsm_ready) next = IDLE;
    end
  endcase
end

// register read pointers
always_ff @(posedge i_clk)
  if (i_rst == 1) begin
    rd_ptr <= 0;
    rd_ptr_start <= 0;
    rd_ptr_stop <= 0;
  end
  else begin
    rd_ptr <= rd_ptr_next;
    // latch start & stop pointers to the IDLE state
    if (state == IDLE) begin
      rd_ptr_start <= rd_ptr_next;
      rd_ptr_stop <= wr_ptr;
    end
  end

  // array packing/unpacking for sop & eop signals
  assign xmit_fsm_sop_eop = {xmit_fsm_sop, xmit_fsm_eop};
  assign o_buf_data_sop = buffer_sop_eop[1];
  assign o_buf_data_eop = buffer_sop_eop[0];

  // register zero padding counter
  always_ff @(posedge i_clk)
    if (i_rst)  zero_pad_cntr <= 0;
    else        zero_pad_cntr <= zero_pad_cntr_next;

endmodule