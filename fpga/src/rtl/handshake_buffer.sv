// Buffers a valid-ready handshake signal.
// Use to enable handshaking while using block RAM.
module handshake_buffer #(
    parameter OPT_WIDTH = 1
  )(
    // System signals
    input logic i_clk,
    input logic i_rst,

    // Sender signals
    input logic   i_valid_sndr,
    output logic  o_ready_sndr,

    // Receiver signals
    output logic  o_valid_rcvr,
    input logic   i_ready_rcvr,

    // Optional signals (use if the handshake has associated data)
    input logic   [OPT_WIDTH-1:0] i_opt,
    output logic  [OPT_WIDTH-1:0] o_opt
);

// Successful ready-valid handshake
logic handshake_sndr;
logic handshake_rcvr;
assign handshake_sndr = o_ready_sndr && i_valid_sndr;
assign handshake_rcvr = i_ready_rcvr && o_valid_rcvr;

// Sender ready logic
always_ff @(posedge i_clk)
  if (i_rst) o_ready_sndr <= 0;
  // (No valid at buffer awaiting handshake) || (Handshake being completed from buffer-rcvr)
  else o_ready_sndr <= !o_valid_rcvr || handshake_rcvr;

// Receiver valid logic
always_ff @(posedge i_clk) 
  if (i_rst) o_valid_rcvr <= 0;
  // (Handshake being completed from sndr-buffer) || (Valid at buffer awaiting handshake)
  else o_valid_rcvr <= handshake_sndr || (o_valid_rcvr && !i_ready_rcvr);

// Optional signal logic
always_ff @(posedge i_clk)
  if (i_rst) o_opt <= 0;
  else if (handshake_sndr) o_opt <= i_opt;
  // doesn't affect function -- just for debugging
  else if (handshake_rcvr) o_opt <= 0;

endmodule