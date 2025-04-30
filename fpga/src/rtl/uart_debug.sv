module uart_debug (
  // system ports  
  input logic i_clk,
  input logic i_rst,
  // data ports
  input logic [7:0] i_data,
  input logic i_data_valid,
  // uart ports
  input logic i_uart_rx,
  output logic o_uart_tx
);

// signals

logic uart_fifo_empty;
logic uart_fifo_read;

logic [7:0] uart_tx_data;
logic uart_tx_ready, uart_tx_valid;

logic rst_n;

// logic

assign rst_n = !i_rst;
assign uart_fifo_read = uart_tx_ready && !uart_fifo_empty;
assign uart_tx_valid = uart_fifo_read;

// instances

uart_fifo	uart_fifo_inst (
  .clock (i_clk),
  .wrreq (i_data_valid),
  .data (i_data),
  .rdreq (uart_fifo_read),
  .q (uart_tx_data),
  .empty (uart_fifo_empty)
);

uart_tx # (
    .DATA_WIDTH(8),
    .BAUD_RATE(115200),
    .CLK_FREQ_MHZ(50),
    .STOP_BITS(1)
  )
  uart_tx_inst (
    .clk_i(i_clk),
    .rstn_i(rst_n),
    .data_i(uart_tx_data),
    .ready_o(uart_tx_ready),
    .valid_i(uart_tx_valid),
    .data_o(o_uart_tx)
  );

endmodule