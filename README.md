# SAP-1 Architecture in Logisim

## Table of Contents
Click on the Table of Contents below to directly go to the sections:
- [Video Tutorial](#video-tutorial)
- [Project Overview](#project-overview)
- [Objectives](#objectives)
- [Key Features](#key-features)

- [Architecture and Functional Block Analysis](#architecture-and-functional-block-analysis)
  - [System Architecture Overview](#system-architecture-overview)
  - [Register Implementation (A, B)](#register-implementation-a-b)
  - [Program Counter (PC) Implementation](#program-counter-pc-implementation)
  - [Memory System and Address Register](#memory-system-and-address-register)
  - [Instruction Register and Opcode Decoder](#instruction-register-and-opcode-decoder)
  - [Arithmetic Logic Unit (ALU) Implementation](#arithmetic-logic-unit-alu-implementation)
  - [Boot/Loader Counter and Phase Generation](#bootloader-counter-and-phase-generation)

- [Control System Design](#control-system-design)
  - [Timing Control Generator](#timing-control-generator)
  - [Automatic Operation Control Logic](#automatic-operation-control-logic)
  - [Manual/Loader Operation Control](#manualloader-operation-control)

- [Instruction Set Architecture](#instruction-set-architecture)
  - [Instruction Encoding Scheme](#instruction-encoding-scheme)
  - [Assembler](#assembler)

- [Operation](#operation)
  - [Fetch–Decode–Execute Cycle](#fetchdecodeexecute-cycle)
  - [Running the CPU in Manual Mode](#running-the-cpu-in-manual-mode)
  - [Running the CPU in Automatic Mode (JMP + ADD Program)](#running-the-cpu-in-automatic-mode-jmp--add-program)

- [Future Improvement](#future-improvement)
- [Conclusion](#conclusion)

## Video Tutorial
Watch the complete demonstration of the **SAP-1 CPU with Control Sequencer (Manual and Automatic Modes)** implemented in **Logisim Evolution**.  
Click the image below to watch the video on YouTube:

[![SAP-1 CPU Tutorial](https://img.youtube.com/vi/_WnzsczYcdg/0.jpg)](https://youtu.be/_WnzsczYcdg)

## Project Overview

This project implements an **enhanced 8-bit SAP-1 computer** in **Logisim Evolution** with **hardwired control** and an extended instruction set (`LDA`, `LDB`, `ADD`, `SUB`, `STA`, `JMP`, `HLT`).  
It supports **Automatic Mode** (fetch–decode–execute cycle) and **Manual/Loader Mode** for program transfer.  
A **control sequencer** manages the bus and timing, while a **web-based assembler** converts assembly code into Logisim-compatible images.  
Test programs verified correct instruction execution and memory operations, making it a **reliable educational framework** for learning processor architecture.

## Objectives

- Develop an improved **SAP-1 (8-bit)** computer in **Logisim Evolution** for teaching and system-level analysis.  
- Implement a classical **single-bus architecture** with **8-bit data path**, **4-bit address space (16 bytes)**, and a **hardwired control sequencer** managing the fetch–decode–execute cycle.  
- Support **Automatic Mode** (six-stage ring counter `T1–T6` with opcode decoder) and **Manual/Loader Mode** for safe program loading into RAM.  
- Design a datapath with **dual 8-bit registers** (A and B), **ripple-carry ALU** (`ADD/SUB`), **4-bit program counter** (increment/load), **Memory Address Register (MAR)**, **16×8 SRAM**, and **Instruction Register** (opcode + operand) while enforcing **strict single-driver bus operation**.

## Key Features

- **8-bit CPU Architecture:** Implements the classic SAP-1 design with 8-bit data and address buses.  
- **Manual & Automatic Modes:** Allows step-by-step instruction execution and fully automatic program run.  
- **Register Set:** Includes **A and B registers** for ALU operations and temporary storage.  
- **Program Counter (PC):** Automatically increments to fetch the next instruction from memory.  
- **Memory System:** Combines **ROM for program storage** and an **Address Register** for accessing memory.  
- **Instruction Register & Opcode Decoder:** Separates instructions into opcode and operand for proper ALU operations.  
- **Arithmetic Logic Unit (ALU):** Performs **addition and subtraction** on the accumulator.  
- **Control Logic:** Features **Timing Control Generator** and phase-based operation sequencing.  
- **Expandable Instruction Set:** Supports basic instructions like **LDA, ADD, SUB, STA, OUT, HLT**.  
- **Educational Tool:** Perfect for learning CPU architecture, instruction cycles, and control logic using **Logisim visualization**.

## Architecture and Functional Block Analysis

### System Architecture Overview
The processor architecture uses a **unified single-bus design** with an **8-bit datapath** controlled by tri-state sources. Bus arbitration ensures that only **one driver** is active during each T-state, with possible drivers including `pc_out`, `sram_rd`, `ins_reg_out_en`, `a_out`, `b_out`, `alu_out`, and `sh_out`. Bus listener components such as `mar_in_en`, `ins_reg_in_en`, `a_in`, `b_in`, and `sram_wr` allow selective data capture when required.

![Automatic Mode Control Sequencer](images/cs.jpg)  
**Figure 1:** Automatic mode operation of the control sequencer showing fetch–decode–execute sequencing.  

![Manual/Loader Mode Control Sequencer](images/cs_manual.jpg)  
**Figure 2:** Manual/Loader mode operation of the control sequencer showing secure program loading with debug and handshake signals.  

### Register Implementation (A, B)

The **A and B registers** use `reg_gp` modules to store **8-bit data**. They have three interfaces:

1. **Input:** Connected to the system bus; controlled by `a_in` and `b_in` signals.  
2. **Output:** Drives the bus via tri-state logic using `a_out` and `b_out`.  
3. **Internal:** Provides direct access to the **ALU** through `reg_int_out` without using the bus.

![A/B Register Subsystem](images/ins_reg.jpg)  
**Figure 3:** A/B register subsystem with input, output, and internal interfaces.  

### Program Counter (PC) Implementation

The **Program Counter (PC)** supports **dual modes** for sequential execution and program flow control:

- **Increment Mode:** At timing state `T3`, when `pc_en = 1`, the PC updates as `PC ← PC + 1`, enabling sequential instruction progression.  
- **Jump Mode:** During a `JMP` instruction at timing state `T4`, when `jump_en = 1`, the lower nibble of the Instruction Register (IR) is placed on the bus and loaded into the PC for direct program control transfer.  

**Bus Interface:** At timing state `T1`, when `pc_out = 1`, the current PC value is driven onto the system bus and loaded into the **Memory Address Register (MAR)** to start the instruction fetch cycle.



![Program Counter Direct Load](images/lda_ldb_sum.jpg)  
**Figure 5:** Program Counter direct load and sequential functionality. 

### Memory System and Address Register

The memory subsystem includes a **4-bit Memory Address Register (MAR)** which captures addresses from the system bus under the control of `mar_in_en`.

- **Instruction Fetching:** During the `T1` phase, `pc_out` and `mar_in_en` load the Program Counter value into the MAR for instruction fetch.  
- **Operand Addressing:** During `T4` of `LDA`, `LDB`, `STA`, or `JMP` instructions, `ins_reg_out_en` together with `mar_in_en` transfers the operand address (`IR[3:0]`) into the MAR.

The **SRAM** operates in two modes:  
- **Read Mode:** When `sram_rd = 1`, the value at `RAM[MAR]` is placed on the bus during `T2` (instruction fetch) and `T5` (LDA/LDB).  
- **Write Mode:** When `sram_wr = 1`, the data on the bus is written into `RAM[MAR]` during `T5` of the `STA` instruction.

![Memory Element](images/data_in_sram.jpg)  
**Figure 6:** Register-based memory element showing `data_in`, `wr_en`, `rd_en`, clock, and chip select (`cs`) signals. Output to the bus is via `data_out`.  


### Instruction Register and Opcode Decoder

The **Instruction Register (IR)** has a dual role for **instruction storage** and **operand handling**:

1. **Instruction Loading:** During `T2`, signals `sram_rd = 1` and `ins_reg_in_en = 1` transfer `IR ← M[MAR]`, capturing the instruction from memory.  
2. **Opcode Handling:** The upper nibble `IR[7:4]` goes to the **opcode decoder** (`ins_tab`), generating one-hot control signals for the decoded instruction.  
3. **Operand Handling:** The lower nibble `IR[3:0]` can be placed onto the system bus when `ins_reg_out_en = 1` (typically during `T4`) to provide operand addresses or target values for memory and jump instructions.

The **opcode decoder (`ins_tab`)** implements a **4-to-16 decoding scheme**, producing one-hot signals such as `insLDA`, `insLDB`, `insADD`, `insSUB`, `insSTA`, `insJMP`, `insHLT`, with unused outputs reserved for future instructions.


### Arithmetic Logic Unit (ALU) Implementation

The **ALU subsystem** performs **8-bit arithmetic** with the following features:

- **Input Sources:** Operands come directly from `A.reg_int_out` and `B.reg_int_out`, bypassing the bus.  
- **Operation Control:** `alu_sub = 1` selects subtraction (`A − B`); otherwise, addition (`A + B`) is performed.  
- **Execution Protocol:** During `T4`, with `a_out = 1`, `b_out = 1`, `alu_out = 1`, and `a_in = 1`, the ALU executes `A ← A ± B` in one step.  
- **Architectural Design:** Ripple-carry adder with mode control; simple hardware with linear carry propagation delay.  
- **Bus Interface:** ALU output drives the system bus only when `alu_out = 1` via tri-state logic.

![ALU Implementation](images/alu.jpg)  
**Figure 9:** ALU implementation with ripple-carry architecture and tri-state bus interface.  

### Boot/Loader Counter and Phase Generation

The **boot/loader subsystem (`ins_loader`)** securely transfers program data from ROM to RAM in **Manual/Loader mode**:

1. **Functional Role:** Loads programs from ROM to RAM when `debug = 1`, disabling normal fetch-execute logic.  
2. **Input Interface:** Accepts `clk`, `bc_reset` (counter reset), `bc_en` (count enable), and `debug` for mode selection.  
3. **Address Sequencing:** Uses a 4-bit `CTR4` counter for upward counting, producing addresses `bc_address[3:0]` for systematic RAM writes.  
4. **Phase Control:** Generates two non-overlapping clock phases (`Φ` and `¬Φ`) via a D flip-flop with feedback inversion to synchronize data transfer and prevent contention.

![Boot/Loader Subsystem](images/add_load.jpg)  
**Figure 10:** Boot/loader subsystem with sequential address generation and dual-phase clocking.  

## Control System Design

The **control unit** translates instructions into precisely timed control pulses to:  
1. Ensure exclusive bus driver activation.  
2. Enable appropriate latch operations during each T-state.  

Key components include:  
- **Ring Counter (RC):** Generates timing states T1–T6.  
- **Opcode Decoder:** Produces activation lines for instruction-specific micro-operations.  
- **Mode Control Inputs:** `debug` (manual/loader selection), `i1/i2` (loader handshake) defining CPU mode (~debug with loader masking via ~i2).  

The control sequencer operates in two paradigms:  
- **Automatic Execution Mode:** Optimized for fetch–decode–execute cycles.  
- **Manual/Loader Mode:** Optimized for safe program loading and debugging.  

Both modes maintain **strict signal integrity** and **timing synchronization**.

![Manual Mode Control Sequencer](images/cs_manual.jpg)  
**Figure 11:** SAP-1 Manual Mode control sequencer  

The **Manual Mode** sequencer provides a simplified execution pathway, supporting only the ADD instruction for *step-wise verification* and *manual debugging*.  

![Automatic Mode Control Sequencer](images/cs.jpg)  
**Figure 12:** SAP-1 Automatic Mode control sequencer 

The **Automatic Mode** sequencer manages the full fetch–decode–execute cycle for ADD, SUB, and JMP instructions using **ring counter timing** combined with **opcode decoding**, ensuring **efficient bus utilization** and **precise timing**.

## Timing Control Generator

A **ring counter** generates six phases (T1–T6) to orchestrate the fetch–decode–execute cycle, ensuring deterministic micro-operation sequencing.

### Universal Fetch Sequence

For every instruction:  
- **T1:** PC output enabled and captured by MAR (MAR ← PC).  
- **T2:** Memory read initiated (`sram_rd`) and IR loaded (IR ← M[MAR]).  
- **T3:** PC incremented (PC ← PC + 1).

![Timing Control Generator](images/pc.jpg)  
**Figure 13:** Six-phase ring counter  

### Representative Execute Sequences

- **LDA addr:**  
  - T4: Operand address (IR[3:0]) placed on bus and loaded into MAR.  
  - T5: Memory value read and latched into A (A ← M[MAR]).  
- **ADD:**  
  - T4: A and B outputs drive ALU; result fed back to A (`alu_sub = 0`).  
- **SUB:**  
  - T4: Similar to ADD with subtraction (`alu_sub = 1`).  
- **JMP addr:**  
  - T4: Operand placed on bus and loaded into PC (PC ← IR[3:0]).

## Automatic Operation Control Logic

Automatic operation uses:  
- **c_en = CPU ~debug**  
 

These signals coordinate the fetch–decode–execute cycle for deterministic micro-operation execution.


**Fetch Control Equations**

| Signal          | Equation                                                       |
|-----------------|----------------------------------------------------------------|
| pc_out          | T1                                                          |
| mar_in_en       | (T1) \| (T4 & (insLDA \| insLDB \| insSTA \| insJMP)) |
| sram_rd         | (T2) \| (T5& (insLDA \| insLDB))                     |
| ins_reg_in_en   | T2                                                         |
| pc_en           | T3                                                        |

**ALU and Register Control Equations**

| Signal  | Equation                                              |
|---------|------------------------------------------------------|
| alu_out | T4 & (insADD \| insSUB)                          |
| alu_sub | T4 & insSUB                                      |
| a_in    | (T5 & insLDA) \| (T4  & (insADD \| insSUB))   |
| b_in    | T5 & insLDB                                      |
| a_out   | (T4 & (insADD \| insSUB)) \| (T5 & insSTA)   |
| b_out   | T4 & (insADD \| insSUB)                          |

## Manual/Loader Operation Control

In **Manual/Loader Mode**, `debug = 1` masks normal CPU fetch–decode–execute operations.  

Program transfer follows a **handshake protocol**:  
- **i1:** Enables address placement into MAR.  
- **i2:** Activates SRAM write operations.  

This ensures **safe memory loading** without bus contention.

## Instruction Set Architecture

### Instruction Encoding Scheme
The instruction encoding system utilizes *upper nibble = IR[7:4]* for opcode specification and *lower nibble* for 4-bit operand/address when required.

---

#### Table 1: Instruction Set & Program

| Address   | Instruction | Hex | Mnemonic & Explanation        |
|-----------|-------------|-----|--------------------------------|
| 00000000  | 00011101    | 1D  | LDA 13 (Load A from M[13])     |
| 00000001  | 00101110    | 2E  | LDB 14 (Load B from M[14])     |
| 00000010  | 01100101    | 65  | JMP 5 (PC ← 5)                 |
| 00000011  | 00110000    | 30  | ADD (A ← A + B)                |
| 00000100  | 01011111    | 5F  | SHL_A (Shift value from A 1bit)|
| 00000101  | 11110000    | F0  | HLT (Stop execution)           |

---

#### Table 2: Data Values in RAM

| Address (Binary) | Data (Binary) | Decimal | Hex |
|------------------|---------------|---------|-----|
| 0001101          | 00010100      | 20      | 14  |
| 0001110          | 00011001      | 25      | 19  |

---

### Assembler

The assembler translates *SAP-1 assembly language programs* into *machine code (hexadecimal)* suitable for execution in Logisim.  
It supports instructions such as *LDA, LDB, ADD, SUB, STA, JMP, and HLT*, along with directives like **ORG** and **DEC**.  
The tool automatically generates *Logisim-compatible v2.0 raw hex output*, avoiding manual conversion errors.  

This enables efficient program development, testing, and debugging of the SAP-1 system.

#### 🔗 [Open the SAP-1 Assembler Tool](https://htmlpreview.github.io/?https://github.com/zinia00/SAP_1_Architecture_Logisim/blob/main/Assembler_20.html)

---

#### SAP-1 Assembler Interface

![SAP-1 Assembler](images/compiler.jpg)

Figure 16: Web-based SAP-1 assembler interface converting assembly instructions into Logisim-compatible hexadecimal code.

---

#### Table 3: Examples of Assembly Programs and Corresponding Hex Codes

| Example             | Assembly Code                                                                                   | Hex Code                                      |
|---------------------|------------------------------------------------------------------------------------------------|-----------------------------------------------|
| *ADD Program*       | LDA 13, LDB 14, ADD, STA 15, HLT <br> (ORG 13, DEC 20, ORG 14, DEC 25)                         | 1D 2E 30 5F F0 00 00 00 00 00 00 14 19 00 00  |
| *JMP + ADD Program* | LDA 13, LDB 14, JMP 5, ADD, STA 15, HLT <br> (ORG 13, DEC 20, ORG 14, DEC 25)                  | 1D 2E 65 30 5F F0 00 00 00 00 00 00 14 19 00  |

---

## Operation

The CPU functions through a repetitive sequence of operations controlled by the system clock, known as the *fetch–decode–execute* cycle.  

### Fetch–Decode–Execute Cycle

**Fetch**  
T1: Program Counter (PC) outputs the current instruction address onto the bus, stored in MAR.  
T2: Memory places the instruction on the bus, captured by IR.  
T3: PC increments to point to the next instruction.  

**Decode**  
Opcode in IR is sent to the instruction decoder, which activates the corresponding control line.  
Combined with the active timing state, this defines required control signals.  

**Execute**  
Control unit asserts relevant signals to carry out micro-operations.  
Execution time varies by instruction (e.g., LDA requires 2 states, ADD requires 2, HLT requires 1).  
The process repeats until HLT stops execution.  

---

### Running the CPU in Manual Mode

**Initial Setup**  
Debug pin OFF (LOW).  
Pulse pc_reset once to reset PC.  
Main clock OFF.  
Set en_run HIGH.  

**RAM Programming (Debug Mode)**  
Turn ON debug pin (HIGH).  
Set address using debug_data.  
Pulse mar_in_en_manual to load MAR.  
Set instruction/data on debug_data.  
Pulse ram_wr_manual to write.  

**After loading**  
Turn debug pin OFF.  
Pulse pc_reset again to reset PC.  

**Run Program**  
Manual stepping: press clk repeatedly.  
Continuous run: enable continuous clock.  

**Verify Result**  
Check RAM[15] = 45 (0x2D), result of adding 20 and 25.  


---

### Running the CPU in Automatic Mode (JMP + ADD Program)

**Step 1 – Initial Setup**  
Debug pin LOW.  
Main clock OFF.  
Pulse pc_reset once.  

**Step 2 – Program the ROM**  
Edit ROM contents in Logisim.  
Enter hex sequence:  
1A 2B 30 40 70 80 90 00 00 00 0A 0B 00 00 00 00 

**Step 3 – Load to RAM (Bootloader Mode)**  
Set debug pin HIGH.  
Each clk pulse transfers program from ROM to RAM.  
Observe MAR and Data Bus activity.  

**Step 4 – Stop Bootloader**  
Set debug pin LOW.  
Pulse clk once.  

**Step 5 – Run Program**  
Pulse pc_reset to reset PC.  
Provide clock pulses for execution.  
Observe PC, MAR, IR, A, B registers.  

**Step 6 – Execution Sequence**  
LDA 13 → A = 10  
LDB 14 → B = 11 
JMP 0 → PC = 0  
ADD → A = A + B = 21 
SHL_A → A = Shifted 1 bit to the left
HLT → Stop execution  

**Step 7 – Verify Result**  
RAM[15] = 21   

---

### SAP-1 CPU Execution (Automatic Mode)

![After loading RAM](images/data_in_sram.jpg)  
Figure 18: After loading all instruction and data values into RAM.

![After LDA 13](images/lda_ldb_sum.jpg)  
Figure 19: Value loaded from memory address into Registers and add shown in the output of ALU.


![After STA 15](images/shiftedvalue.jpg)  
Figure 23: Shifted value of register A.

## Future Improvement

Potential directions for extending the current SAP-1 implementation include:

**Status Flags:** Add Zero (Z) and Carry (C) flags to support conditional branch instructions (e.g., JZ, JC).  
**Enhanced Memory & Instructions:** Support multi-byte addressing, immediate data loading, and richer instruction formats.  
**Microcoded Control Unit:** Enable systematic ISA expansion for new operations like shift and rotate.  
**Expanded Assembler:** Develop a symbolic assembler with labels, expressions, and enhanced directives to improve programmability and instructional clarity.

## Conclusion

The enhanced **SAP-1** bridges classical processor design with modern simulation-based education. With **dual operational modes**, **expanded instruction support**, and a **structured control sequencer**, the system demonstrates technical correctness and pedagogical clarity.  Test programs validated proper execution, control logic, and timing coordination. This project provides a **practical, extensible platform** for undergraduate learning in computer architecture and lays the foundation for future enhancements in processor design and research.
