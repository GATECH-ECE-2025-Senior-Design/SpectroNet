module hex_disp
(
    input logic [3:0] hex_val,
    input logic cs,
    input logic free,
    input logic resetn,
    
    output logic [6:0] segments
);

    logic [3:0] latched_hex;
    logic [3:0] hex_d;

    always_ff @(posedge cs, negedge resetn) begin
        if (resetn == '0)
            latched_hex <= 4'b0000; 
        else begin
            latched_hex <= hex_val;
        end
    end

    always_comb begin
        case(free) 
            '0: hex_d = latched_hex;
            '1: hex_d = hex_val;
        endcase

        case(hex_d)
            4'b0000: segments = 7'b1000000;
            4'b0001: segments = 7'b1111001;
            4'b0010: segments = 7'b0100100;
            4'b0011: segments = 7'b0110000;
            4'b0100: segments = 7'b0011001;
            4'b0101: segments = 7'b0010010;
            4'b0110: segments = 7'b0000010;
            4'b0111: segments = 7'b1111000;
            4'b1000: segments = 7'b0000000;
            4'b1001: segments = 7'b0010000;
            4'b1010: segments = 7'b0001000;
            4'b1011: segments = 7'b0000011;
            4'b1100: segments = 7'b1000110;
            4'b1101: segments = 7'b0100001;
            4'b1110: segments = 7'b0000110;
            4'b1111: segments = 7'b0001110;
            default: segments = 7'b0111111;
        endcase
    end

endmodule