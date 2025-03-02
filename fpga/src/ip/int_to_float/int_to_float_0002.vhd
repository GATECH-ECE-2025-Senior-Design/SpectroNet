-- ------------------------------------------------------------------------- 
-- High Level Design Compiler for Intel(R) FPGAs Version 23.1std (Release Build #993)
-- Quartus Prime development tool and MATLAB/Simulink Interface
-- 
-- Legal Notice: Copyright 2024 Intel Corporation.  All rights reserved.
-- Your use of  Intel Corporation's design tools,  logic functions and other
-- software and  tools, and its AMPP partner logic functions, and any output
-- files any  of the foregoing (including  device programming  or simulation
-- files), and  any associated  documentation  or information  are expressly
-- subject  to the terms and  conditions of the  Intel FPGA Software License
-- Agreement, Intel MegaCore Function License Agreement, or other applicable
-- license agreement,  including,  without limitation,  that your use is for
-- the  sole  purpose of  programming  logic devices  manufactured by  Intel
-- and  sold by Intel  or its authorized  distributors. Please refer  to the
-- applicable agreement for further details.
-- ---------------------------------------------------------------------------

-- VHDL created from int_to_float_0002
-- VHDL created on Sat Mar  1 17:38:08 2025


library IEEE;
use IEEE.std_logic_1164.all;
use IEEE.NUMERIC_STD.all;
use IEEE.MATH_REAL.all;
use std.TextIO.all;
use work.dspba_library_package.all;

LIBRARY altera_mf;
USE altera_mf.altera_mf_components.all;
LIBRARY altera_lnsim;
USE altera_lnsim.altera_lnsim_components.altera_syncram;
LIBRARY lpm;
USE lpm.lpm_components.all;

entity int_to_float_0002 is
    port (
        a : in std_logic_vector(31 downto 0);  -- sfix32
        q : out std_logic_vector(31 downto 0);  -- float32_m23
        clk : in std_logic;
        areset : in std_logic
    );
end int_to_float_0002;

architecture normal of int_to_float_0002 is

    attribute altera_attribute : string;
    attribute altera_attribute of normal : architecture is "-name AUTO_SHIFT_REGISTER_RECOGNITION OFF; -name PHYSICAL_SYNTHESIS_REGISTER_DUPLICATION ON; -name MESSAGE_DISABLE 10036; -name MESSAGE_DISABLE 10037; -name MESSAGE_DISABLE 14130; -name MESSAGE_DISABLE 14320; -name MESSAGE_DISABLE 15400; -name MESSAGE_DISABLE 14130; -name MESSAGE_DISABLE 10036; -name MESSAGE_DISABLE 12020; -name MESSAGE_DISABLE 12030; -name MESSAGE_DISABLE 12010; -name MESSAGE_DISABLE 12110; -name MESSAGE_DISABLE 14320; -name MESSAGE_DISABLE 13410; -name MESSAGE_DISABLE 113007";
    
    signal GND_q : STD_LOGIC_VECTOR (0 downto 0);
    signal VCC_q : STD_LOGIC_VECTOR (0 downto 0);
    signal signX_uid6_fxpToFPTest_b : STD_LOGIC_VECTOR (0 downto 0);
    signal xXorSign_uid7_fxpToFPTest_b : STD_LOGIC_VECTOR (31 downto 0);
    signal xXorSign_uid7_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal yE_uid8_fxpToFPTest_a : STD_LOGIC_VECTOR (32 downto 0);
    signal yE_uid8_fxpToFPTest_b : STD_LOGIC_VECTOR (32 downto 0);
    signal yE_uid8_fxpToFPTest_o : STD_LOGIC_VECTOR (32 downto 0);
    signal yE_uid8_fxpToFPTest_q : STD_LOGIC_VECTOR (32 downto 0);
    signal y_uid9_fxpToFPTest_in : STD_LOGIC_VECTOR (31 downto 0);
    signal y_uid9_fxpToFPTest_b : STD_LOGIC_VECTOR (31 downto 0);
    signal maxCount_uid11_fxpToFPTest_q : STD_LOGIC_VECTOR (5 downto 0);
    signal inIsZero_uid12_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal msbIn_uid13_fxpToFPTest_q : STD_LOGIC_VECTOR (7 downto 0);
    signal expPreRnd_uid14_fxpToFPTest_a : STD_LOGIC_VECTOR (8 downto 0);
    signal expPreRnd_uid14_fxpToFPTest_b : STD_LOGIC_VECTOR (8 downto 0);
    signal expPreRnd_uid14_fxpToFPTest_o : STD_LOGIC_VECTOR (8 downto 0);
    signal expPreRnd_uid14_fxpToFPTest_q : STD_LOGIC_VECTOR (8 downto 0);
    signal expFracRnd_uid16_fxpToFPTest_q : STD_LOGIC_VECTOR (32 downto 0);
    signal sticky_uid20_fxpToFPTest_qi : STD_LOGIC_VECTOR (0 downto 0);
    signal sticky_uid20_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal nr_uid21_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal rnd_uid22_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal expFracR_uid24_fxpToFPTest_a : STD_LOGIC_VECTOR (34 downto 0);
    signal expFracR_uid24_fxpToFPTest_b : STD_LOGIC_VECTOR (34 downto 0);
    signal expFracR_uid24_fxpToFPTest_o : STD_LOGIC_VECTOR (34 downto 0);
    signal expFracR_uid24_fxpToFPTest_q : STD_LOGIC_VECTOR (33 downto 0);
    signal fracR_uid25_fxpToFPTest_in : STD_LOGIC_VECTOR (23 downto 0);
    signal fracR_uid25_fxpToFPTest_b : STD_LOGIC_VECTOR (22 downto 0);
    signal expR_uid26_fxpToFPTest_b : STD_LOGIC_VECTOR (9 downto 0);
    signal udf_uid27_fxpToFPTest_a : STD_LOGIC_VECTOR (11 downto 0);
    signal udf_uid27_fxpToFPTest_b : STD_LOGIC_VECTOR (11 downto 0);
    signal udf_uid27_fxpToFPTest_o : STD_LOGIC_VECTOR (11 downto 0);
    signal udf_uid27_fxpToFPTest_n : STD_LOGIC_VECTOR (0 downto 0);
    signal expInf_uid28_fxpToFPTest_q : STD_LOGIC_VECTOR (7 downto 0);
    signal ovf_uid29_fxpToFPTest_a : STD_LOGIC_VECTOR (11 downto 0);
    signal ovf_uid29_fxpToFPTest_b : STD_LOGIC_VECTOR (11 downto 0);
    signal ovf_uid29_fxpToFPTest_o : STD_LOGIC_VECTOR (11 downto 0);
    signal ovf_uid29_fxpToFPTest_n : STD_LOGIC_VECTOR (0 downto 0);
    signal excSelector_uid30_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal fracZ_uid31_fxpToFPTest_q : STD_LOGIC_VECTOR (22 downto 0);
    signal fracRPostExc_uid32_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal fracRPostExc_uid32_fxpToFPTest_q : STD_LOGIC_VECTOR (22 downto 0);
    signal udfOrInZero_uid33_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal excSelector_uid34_fxpToFPTest_q : STD_LOGIC_VECTOR (1 downto 0);
    signal expZ_uid37_fxpToFPTest_q : STD_LOGIC_VECTOR (7 downto 0);
    signal expR_uid38_fxpToFPTest_in : STD_LOGIC_VECTOR (7 downto 0);
    signal expR_uid38_fxpToFPTest_b : STD_LOGIC_VECTOR (7 downto 0);
    signal expRPostExc_uid39_fxpToFPTest_s : STD_LOGIC_VECTOR (1 downto 0);
    signal expRPostExc_uid39_fxpToFPTest_q : STD_LOGIC_VECTOR (7 downto 0);
    signal outRes_uid40_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal zs_uid42_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_qi : STD_LOGIC_VECTOR (0 downto 0);
    signal vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal zs_uid47_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (15 downto 0);
    signal vCount_uid49_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal cStage_uid52_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vCount_uid56_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal cStage_uid59_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal zs_uid61_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (3 downto 0);
    signal vCount_uid63_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal cStage_uid66_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal zs_uid68_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (1 downto 0);
    signal vCount_uid70_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal cStage_uid73_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vCount_uid77_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (0 downto 0);
    signal cStage_uid80_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (31 downto 0);
    signal vCount_uid82_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (5 downto 0);
    signal vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_a : STD_LOGIC_VECTOR (7 downto 0);
    signal vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_b : STD_LOGIC_VECTOR (7 downto 0);
    signal vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_o : STD_LOGIC_VECTOR (7 downto 0);
    signal vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_c : STD_LOGIC_VECTOR (0 downto 0);
    signal vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_s : STD_LOGIC_VECTOR (0 downto 0);
    signal vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q : STD_LOGIC_VECTOR (5 downto 0);
    signal l_uid17_fxpToFPTest_merged_bit_select_in : STD_LOGIC_VECTOR (1 downto 0);
    signal l_uid17_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (0 downto 0);
    signal l_uid17_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (0 downto 0);
    signal rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (15 downto 0);
    signal rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (15 downto 0);
    signal rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (7 downto 0);
    signal rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (23 downto 0);
    signal rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (3 downto 0);
    signal rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (27 downto 0);
    signal rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (1 downto 0);
    signal rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (29 downto 0);
    signal rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (0 downto 0);
    signal rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (30 downto 0);
    signal fracRnd_uid15_fxpToFPTest_merged_bit_select_in : STD_LOGIC_VECTOR (30 downto 0);
    signal fracRnd_uid15_fxpToFPTest_merged_bit_select_b : STD_LOGIC_VECTOR (23 downto 0);
    signal fracRnd_uid15_fxpToFPTest_merged_bit_select_c : STD_LOGIC_VECTOR (6 downto 0);
    signal redist0_fracRnd_uid15_fxpToFPTest_merged_bit_select_b_1_q : STD_LOGIC_VECTOR (23 downto 0);
    signal redist1_y_uid9_fxpToFPTest_b_1_q : STD_LOGIC_VECTOR (31 downto 0);
    signal redist2_signX_uid6_fxpToFPTest_b_2_q : STD_LOGIC_VECTOR (0 downto 0);

begin


    -- VCC(CONSTANT,1)
    VCC_q <= "1";

    -- signX_uid6_fxpToFPTest(BITSELECT,5)@0
    signX_uid6_fxpToFPTest_b <= STD_LOGIC_VECTOR(a(31 downto 31));

    -- redist2_signX_uid6_fxpToFPTest_b_2(DELAY,97)
    redist2_signX_uid6_fxpToFPTest_b_2 : dspba_delay
    GENERIC MAP ( width => 1, depth => 2, reset_kind => "ASYNC" )
    PORT MAP ( xin => signX_uid6_fxpToFPTest_b, xout => redist2_signX_uid6_fxpToFPTest_b_2_q, clk => clk, aclr => areset );

    -- expInf_uid28_fxpToFPTest(CONSTANT,27)
    expInf_uid28_fxpToFPTest_q <= "11111111";

    -- expZ_uid37_fxpToFPTest(CONSTANT,36)
    expZ_uid37_fxpToFPTest_q <= "00000000";

    -- rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select(BITSELECT,93)@1
    rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b <= vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q(31 downto 31);
    rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c <= vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q(30 downto 0);

    -- GND(CONSTANT,0)
    GND_q <= "0";

    -- cStage_uid80_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,79)@1
    cStage_uid80_lzcShifterZ1_uid10_fxpToFPTest_q <= rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c & GND_q;

    -- rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select(BITSELECT,92)@1
    rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b <= vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q(31 downto 30);
    rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c <= vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q(29 downto 0);

    -- zs_uid68_lzcShifterZ1_uid10_fxpToFPTest(CONSTANT,67)
    zs_uid68_lzcShifterZ1_uid10_fxpToFPTest_q <= "00";

    -- cStage_uid73_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,72)@1
    cStage_uid73_lzcShifterZ1_uid10_fxpToFPTest_q <= rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c & zs_uid68_lzcShifterZ1_uid10_fxpToFPTest_q;

    -- rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select(BITSELECT,91)@1
    rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b <= vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q(31 downto 28);
    rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c <= vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q(27 downto 0);

    -- zs_uid61_lzcShifterZ1_uid10_fxpToFPTest(CONSTANT,60)
    zs_uid61_lzcShifterZ1_uid10_fxpToFPTest_q <= "0000";

    -- cStage_uid66_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,65)@1
    cStage_uid66_lzcShifterZ1_uid10_fxpToFPTest_q <= rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c & zs_uid61_lzcShifterZ1_uid10_fxpToFPTest_q;

    -- rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select(BITSELECT,90)@1
    rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b <= vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q(31 downto 24);
    rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c <= vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q(23 downto 0);

    -- cStage_uid59_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,58)@1
    cStage_uid59_lzcShifterZ1_uid10_fxpToFPTest_q <= rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c & expZ_uid37_fxpToFPTest_q;

    -- rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select(BITSELECT,89)@1
    rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b <= vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q(31 downto 16);
    rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c <= vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q(15 downto 0);

    -- zs_uid47_lzcShifterZ1_uid10_fxpToFPTest(CONSTANT,46)
    zs_uid47_lzcShifterZ1_uid10_fxpToFPTest_q <= "0000000000000000";

    -- cStage_uid52_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,51)@1
    cStage_uid52_lzcShifterZ1_uid10_fxpToFPTest_q <= rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_c & zs_uid47_lzcShifterZ1_uid10_fxpToFPTest_q;

    -- zs_uid42_lzcShifterZ1_uid10_fxpToFPTest(CONSTANT,41)
    zs_uid42_lzcShifterZ1_uid10_fxpToFPTest_q <= "00000000000000000000000000000000";

    -- xXorSign_uid7_fxpToFPTest(LOGICAL,6)@0
    xXorSign_uid7_fxpToFPTest_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((31 downto 1 => signX_uid6_fxpToFPTest_b(0)) & signX_uid6_fxpToFPTest_b));
    xXorSign_uid7_fxpToFPTest_q <= a xor xXorSign_uid7_fxpToFPTest_b;

    -- yE_uid8_fxpToFPTest(ADD,7)@0
    yE_uid8_fxpToFPTest_a <= STD_LOGIC_VECTOR("0" & xXorSign_uid7_fxpToFPTest_q);
    yE_uid8_fxpToFPTest_b <= STD_LOGIC_VECTOR("00000000000000000000000000000000" & signX_uid6_fxpToFPTest_b);
    yE_uid8_fxpToFPTest_o <= STD_LOGIC_VECTOR(UNSIGNED(yE_uid8_fxpToFPTest_a) + UNSIGNED(yE_uid8_fxpToFPTest_b));
    yE_uid8_fxpToFPTest_q <= yE_uid8_fxpToFPTest_o(32 downto 0);

    -- y_uid9_fxpToFPTest(BITSELECT,8)@0
    y_uid9_fxpToFPTest_in <= STD_LOGIC_VECTOR(yE_uid8_fxpToFPTest_q(31 downto 0));
    y_uid9_fxpToFPTest_b <= STD_LOGIC_VECTOR(y_uid9_fxpToFPTest_in(31 downto 0));

    -- redist1_y_uid9_fxpToFPTest_b_1(DELAY,96)
    redist1_y_uid9_fxpToFPTest_b_1 : dspba_delay
    GENERIC MAP ( width => 32, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => y_uid9_fxpToFPTest_b, xout => redist1_y_uid9_fxpToFPTest_b_1_q, clk => clk, aclr => areset );

    -- vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,43)@0 + 1
    vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_qi <= "1" WHEN y_uid9_fxpToFPTest_b = zs_uid42_lzcShifterZ1_uid10_fxpToFPTest_q ELSE "0";
    vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_delay : dspba_delay
    GENERIC MAP ( width => 1, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_qi, xout => vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_q, clk => clk, aclr => areset );

    -- vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest(MUX,45)@1
    vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_s, redist1_y_uid9_fxpToFPTest_b_1_q, zs_uid42_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q <= redist1_y_uid9_fxpToFPTest_b_1_q;
            WHEN "1" => vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q <= zs_uid42_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- vCount_uid49_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,48)@1
    vCount_uid49_lzcShifterZ1_uid10_fxpToFPTest_q <= "1" WHEN rVStage_uid48_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b = zs_uid47_lzcShifterZ1_uid10_fxpToFPTest_q ELSE "0";

    -- vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest(MUX,52)@1
    vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid49_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_s, vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q, cStage_uid52_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q <= vStagei_uid46_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN "1" => vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q <= cStage_uid52_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- vCount_uid56_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,55)@1
    vCount_uid56_lzcShifterZ1_uid10_fxpToFPTest_q <= "1" WHEN rVStage_uid55_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b = expZ_uid37_fxpToFPTest_q ELSE "0";

    -- vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest(MUX,59)@1
    vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid56_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_s, vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q, cStage_uid59_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q <= vStagei_uid53_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN "1" => vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q <= cStage_uid59_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- vCount_uid63_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,62)@1
    vCount_uid63_lzcShifterZ1_uid10_fxpToFPTest_q <= "1" WHEN rVStage_uid62_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b = zs_uid61_lzcShifterZ1_uid10_fxpToFPTest_q ELSE "0";

    -- vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest(MUX,66)@1
    vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid63_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_s, vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q, cStage_uid66_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q <= vStagei_uid60_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN "1" => vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q <= cStage_uid66_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- vCount_uid70_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,69)@1
    vCount_uid70_lzcShifterZ1_uid10_fxpToFPTest_q <= "1" WHEN rVStage_uid69_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b = zs_uid68_lzcShifterZ1_uid10_fxpToFPTest_q ELSE "0";

    -- vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest(MUX,73)@1
    vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid70_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_s, vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q, cStage_uid73_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q <= vStagei_uid67_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN "1" => vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q <= cStage_uid73_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- vCount_uid77_lzcShifterZ1_uid10_fxpToFPTest(LOGICAL,76)@1
    vCount_uid77_lzcShifterZ1_uid10_fxpToFPTest_q <= "1" WHEN rVStage_uid76_lzcShifterZ1_uid10_fxpToFPTest_merged_bit_select_b = GND_q ELSE "0";

    -- vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest(MUX,80)@1
    vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_s <= vCount_uid77_lzcShifterZ1_uid10_fxpToFPTest_q;
    vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_combproc: PROCESS (vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_s, vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q, cStage_uid80_lzcShifterZ1_uid10_fxpToFPTest_q)
    BEGIN
        CASE (vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_s) IS
            WHEN "0" => vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_q <= vStagei_uid74_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN "1" => vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_q <= cStage_uid80_lzcShifterZ1_uid10_fxpToFPTest_q;
            WHEN OTHERS => vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- fracRnd_uid15_fxpToFPTest_merged_bit_select(BITSELECT,94)@1
    fracRnd_uid15_fxpToFPTest_merged_bit_select_in <= vStagei_uid81_lzcShifterZ1_uid10_fxpToFPTest_q(30 downto 0);
    fracRnd_uid15_fxpToFPTest_merged_bit_select_b <= fracRnd_uid15_fxpToFPTest_merged_bit_select_in(30 downto 7);
    fracRnd_uid15_fxpToFPTest_merged_bit_select_c <= fracRnd_uid15_fxpToFPTest_merged_bit_select_in(6 downto 0);

    -- sticky_uid20_fxpToFPTest(LOGICAL,19)@1 + 1
    sticky_uid20_fxpToFPTest_qi <= "1" WHEN fracRnd_uid15_fxpToFPTest_merged_bit_select_c /= "0000000" ELSE "0";
    sticky_uid20_fxpToFPTest_delay : dspba_delay
    GENERIC MAP ( width => 1, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => sticky_uid20_fxpToFPTest_qi, xout => sticky_uid20_fxpToFPTest_q, clk => clk, aclr => areset );

    -- nr_uid21_fxpToFPTest(LOGICAL,20)@2
    nr_uid21_fxpToFPTest_q <= not (l_uid17_fxpToFPTest_merged_bit_select_c);

    -- l_uid17_fxpToFPTest_merged_bit_select(BITSELECT,88)@2
    l_uid17_fxpToFPTest_merged_bit_select_in <= STD_LOGIC_VECTOR(expFracRnd_uid16_fxpToFPTest_q(1 downto 0));
    l_uid17_fxpToFPTest_merged_bit_select_b <= STD_LOGIC_VECTOR(l_uid17_fxpToFPTest_merged_bit_select_in(1 downto 1));
    l_uid17_fxpToFPTest_merged_bit_select_c <= STD_LOGIC_VECTOR(l_uid17_fxpToFPTest_merged_bit_select_in(0 downto 0));

    -- rnd_uid22_fxpToFPTest(LOGICAL,21)@2
    rnd_uid22_fxpToFPTest_q <= l_uid17_fxpToFPTest_merged_bit_select_b or nr_uid21_fxpToFPTest_q or sticky_uid20_fxpToFPTest_q;

    -- maxCount_uid11_fxpToFPTest(CONSTANT,10)
    maxCount_uid11_fxpToFPTest_q <= "100000";

    -- vCount_uid82_lzcShifterZ1_uid10_fxpToFPTest(BITJOIN,81)@1
    vCount_uid82_lzcShifterZ1_uid10_fxpToFPTest_q <= vCount_uid44_lzcShifterZ1_uid10_fxpToFPTest_q & vCount_uid49_lzcShifterZ1_uid10_fxpToFPTest_q & vCount_uid56_lzcShifterZ1_uid10_fxpToFPTest_q & vCount_uid63_lzcShifterZ1_uid10_fxpToFPTest_q & vCount_uid70_lzcShifterZ1_uid10_fxpToFPTest_q & vCount_uid77_lzcShifterZ1_uid10_fxpToFPTest_q;

    -- vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest(COMPARE,83)@1
    vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_a <= STD_LOGIC_VECTOR("00" & maxCount_uid11_fxpToFPTest_q);
    vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_b <= STD_LOGIC_VECTOR("00" & vCount_uid82_lzcShifterZ1_uid10_fxpToFPTest_q);
    vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_o <= STD_LOGIC_VECTOR(UNSIGNED(vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_a) - UNSIGNED(vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_b));
    vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_c(0) <= vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_o(7);

    -- vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest(MUX,85)@1 + 1
    vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_s <= vCountBig_uid84_lzcShifterZ1_uid10_fxpToFPTest_c;
    vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_clkproc: PROCESS (clk, areset)
    BEGIN
        IF (areset = '1') THEN
            vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
        ELSIF (clk'EVENT AND clk = '1') THEN
            CASE (vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_s) IS
                WHEN "0" => vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q <= vCount_uid82_lzcShifterZ1_uid10_fxpToFPTest_q;
                WHEN "1" => vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q <= maxCount_uid11_fxpToFPTest_q;
                WHEN OTHERS => vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q <= (others => '0');
            END CASE;
        END IF;
    END PROCESS;

    -- msbIn_uid13_fxpToFPTest(CONSTANT,12)
    msbIn_uid13_fxpToFPTest_q <= "10011110";

    -- expPreRnd_uid14_fxpToFPTest(SUB,13)@2
    expPreRnd_uid14_fxpToFPTest_a <= STD_LOGIC_VECTOR("0" & msbIn_uid13_fxpToFPTest_q);
    expPreRnd_uid14_fxpToFPTest_b <= STD_LOGIC_VECTOR("000" & vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q);
    expPreRnd_uid14_fxpToFPTest_o <= STD_LOGIC_VECTOR(UNSIGNED(expPreRnd_uid14_fxpToFPTest_a) - UNSIGNED(expPreRnd_uid14_fxpToFPTest_b));
    expPreRnd_uid14_fxpToFPTest_q <= expPreRnd_uid14_fxpToFPTest_o(8 downto 0);

    -- redist0_fracRnd_uid15_fxpToFPTest_merged_bit_select_b_1(DELAY,95)
    redist0_fracRnd_uid15_fxpToFPTest_merged_bit_select_b_1 : dspba_delay
    GENERIC MAP ( width => 24, depth => 1, reset_kind => "ASYNC" )
    PORT MAP ( xin => fracRnd_uid15_fxpToFPTest_merged_bit_select_b, xout => redist0_fracRnd_uid15_fxpToFPTest_merged_bit_select_b_1_q, clk => clk, aclr => areset );

    -- expFracRnd_uid16_fxpToFPTest(BITJOIN,15)@2
    expFracRnd_uid16_fxpToFPTest_q <= expPreRnd_uid14_fxpToFPTest_q & redist0_fracRnd_uid15_fxpToFPTest_merged_bit_select_b_1_q;

    -- expFracR_uid24_fxpToFPTest(ADD,23)@2
    expFracR_uid24_fxpToFPTest_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((34 downto 33 => expFracRnd_uid16_fxpToFPTest_q(32)) & expFracRnd_uid16_fxpToFPTest_q));
    expFracR_uid24_fxpToFPTest_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR("0000000000000000000000000000000000" & rnd_uid22_fxpToFPTest_q));
    expFracR_uid24_fxpToFPTest_o <= STD_LOGIC_VECTOR(SIGNED(expFracR_uid24_fxpToFPTest_a) + SIGNED(expFracR_uid24_fxpToFPTest_b));
    expFracR_uid24_fxpToFPTest_q <= expFracR_uid24_fxpToFPTest_o(33 downto 0);

    -- expR_uid26_fxpToFPTest(BITSELECT,25)@2
    expR_uid26_fxpToFPTest_b <= STD_LOGIC_VECTOR(expFracR_uid24_fxpToFPTest_q(33 downto 24));

    -- expR_uid38_fxpToFPTest(BITSELECT,37)@2
    expR_uid38_fxpToFPTest_in <= expR_uid26_fxpToFPTest_b(7 downto 0);
    expR_uid38_fxpToFPTest_b <= expR_uid38_fxpToFPTest_in(7 downto 0);

    -- ovf_uid29_fxpToFPTest(COMPARE,28)@2
    ovf_uid29_fxpToFPTest_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((11 downto 10 => expR_uid26_fxpToFPTest_b(9)) & expR_uid26_fxpToFPTest_b));
    ovf_uid29_fxpToFPTest_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR("0000" & expInf_uid28_fxpToFPTest_q));
    ovf_uid29_fxpToFPTest_o <= STD_LOGIC_VECTOR(SIGNED(ovf_uid29_fxpToFPTest_a) - SIGNED(ovf_uid29_fxpToFPTest_b));
    ovf_uid29_fxpToFPTest_n(0) <= not (ovf_uid29_fxpToFPTest_o(11));

    -- inIsZero_uid12_fxpToFPTest(LOGICAL,11)@2
    inIsZero_uid12_fxpToFPTest_q <= "1" WHEN vCountFinal_uid86_lzcShifterZ1_uid10_fxpToFPTest_q = maxCount_uid11_fxpToFPTest_q ELSE "0";

    -- udf_uid27_fxpToFPTest(COMPARE,26)@2
    udf_uid27_fxpToFPTest_a <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR("00000000000" & GND_q));
    udf_uid27_fxpToFPTest_b <= STD_LOGIC_VECTOR(STD_LOGIC_VECTOR((11 downto 10 => expR_uid26_fxpToFPTest_b(9)) & expR_uid26_fxpToFPTest_b));
    udf_uid27_fxpToFPTest_o <= STD_LOGIC_VECTOR(SIGNED(udf_uid27_fxpToFPTest_a) - SIGNED(udf_uid27_fxpToFPTest_b));
    udf_uid27_fxpToFPTest_n(0) <= not (udf_uid27_fxpToFPTest_o(11));

    -- udfOrInZero_uid33_fxpToFPTest(LOGICAL,32)@2
    udfOrInZero_uid33_fxpToFPTest_q <= udf_uid27_fxpToFPTest_n or inIsZero_uid12_fxpToFPTest_q;

    -- excSelector_uid34_fxpToFPTest(BITJOIN,33)@2
    excSelector_uid34_fxpToFPTest_q <= ovf_uid29_fxpToFPTest_n & udfOrInZero_uid33_fxpToFPTest_q;

    -- expRPostExc_uid39_fxpToFPTest(MUX,38)@2
    expRPostExc_uid39_fxpToFPTest_s <= excSelector_uid34_fxpToFPTest_q;
    expRPostExc_uid39_fxpToFPTest_combproc: PROCESS (expRPostExc_uid39_fxpToFPTest_s, expR_uid38_fxpToFPTest_b, expZ_uid37_fxpToFPTest_q, expInf_uid28_fxpToFPTest_q)
    BEGIN
        CASE (expRPostExc_uid39_fxpToFPTest_s) IS
            WHEN "00" => expRPostExc_uid39_fxpToFPTest_q <= expR_uid38_fxpToFPTest_b;
            WHEN "01" => expRPostExc_uid39_fxpToFPTest_q <= expZ_uid37_fxpToFPTest_q;
            WHEN "10" => expRPostExc_uid39_fxpToFPTest_q <= expInf_uid28_fxpToFPTest_q;
            WHEN "11" => expRPostExc_uid39_fxpToFPTest_q <= expInf_uid28_fxpToFPTest_q;
            WHEN OTHERS => expRPostExc_uid39_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- fracZ_uid31_fxpToFPTest(CONSTANT,30)
    fracZ_uid31_fxpToFPTest_q <= "00000000000000000000000";

    -- fracR_uid25_fxpToFPTest(BITSELECT,24)@2
    fracR_uid25_fxpToFPTest_in <= expFracR_uid24_fxpToFPTest_q(23 downto 0);
    fracR_uid25_fxpToFPTest_b <= fracR_uid25_fxpToFPTest_in(23 downto 1);

    -- excSelector_uid30_fxpToFPTest(LOGICAL,29)@2
    excSelector_uid30_fxpToFPTest_q <= inIsZero_uid12_fxpToFPTest_q or ovf_uid29_fxpToFPTest_n or udf_uid27_fxpToFPTest_n;

    -- fracRPostExc_uid32_fxpToFPTest(MUX,31)@2
    fracRPostExc_uid32_fxpToFPTest_s <= excSelector_uid30_fxpToFPTest_q;
    fracRPostExc_uid32_fxpToFPTest_combproc: PROCESS (fracRPostExc_uid32_fxpToFPTest_s, fracR_uid25_fxpToFPTest_b, fracZ_uid31_fxpToFPTest_q)
    BEGIN
        CASE (fracRPostExc_uid32_fxpToFPTest_s) IS
            WHEN "0" => fracRPostExc_uid32_fxpToFPTest_q <= fracR_uid25_fxpToFPTest_b;
            WHEN "1" => fracRPostExc_uid32_fxpToFPTest_q <= fracZ_uid31_fxpToFPTest_q;
            WHEN OTHERS => fracRPostExc_uid32_fxpToFPTest_q <= (others => '0');
        END CASE;
    END PROCESS;

    -- outRes_uid40_fxpToFPTest(BITJOIN,39)@2
    outRes_uid40_fxpToFPTest_q <= redist2_signX_uid6_fxpToFPTest_b_2_q & expRPostExc_uid39_fxpToFPTest_q & fracRPostExc_uid32_fxpToFPTest_q;

    -- xOut(GPOUT,4)@2
    q <= outRes_uid40_fxpToFPTest_q;

END normal;
