module uart_tx #(
    parameter DATA_WIDTH = 8,
    parameter BAUD_RATE = 9600,
    parameter CLK_FREQ_MHZ = 100,
    parameter STOP_BITS = 1
  )(
    // SYSTEM
    input logic clk_i,
    input logic rstn_i,

    // DATA
    input logic [DATA_WIDTH-1:0] data_i,
    output logic ready_o, // valid-ready handshake
    input logic valid_i,
    
    output logic data_o
  );

  // CONSTANTS
  localparam BAUD_CYCLES = 1_000_000 * CLK_FREQ_MHZ / BAUD_RATE;

  // ENUMS
  typedef enum {
            IDLE,
            TX
          } State;

  // SIGNALS
  logic [$clog2(BAUD_CYCLES)-1:0] cycle_cnt;
  logic [$clog2(DATA_WIDTH+STOP_BITS):0] bit_cnt;
  logic [DATA_WIDTH+STOP_BITS:0] shift_reg; // {stop bits, data bits, start bit}
  State state;

  // STATE MACHINE
  always_ff @(posedge clk_i)
  begin
    if (rstn_i == 0)
    begin
      state <= IDLE;
      data_o <= 1; // pull TX high for idle
      ready_o <= 0;
      cycle_cnt <= 0;
      bit_cnt <= 0;
      shift_reg <= 0;
    end
    else
    begin
      case(state)

        IDLE:
        begin
          ready_o <= 1; // ready for new data
          if (valid_i == 1)
          begin
            state <= TX;
            shift_reg <= {{STOP_BITS{1'b1}}, data_i, 1'b0}; // concatenate with start and stop bits
            ready_o <= 0; // sending data, can't take input data
          end
        end

        TX:
        begin
          cycle_cnt <= cycle_cnt + 1;
          data_o <= shift_reg[0]; // send LSB
          if (cycle_cnt == BAUD_CYCLES-1)
          begin
            cycle_cnt <= 0;
            bit_cnt <= bit_cnt + 1;
            shift_reg <= shift_reg >> 1;
            if (bit_cnt == (1+DATA_WIDTH+STOP_BITS)-1)
            begin
              state <= IDLE;
              bit_cnt <= 0;
              ready_o <= 1;
            end
          end
        end

      endcase
    end
  end

endmodule