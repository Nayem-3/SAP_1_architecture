
#!/usr/bin/env python3
import re, sys

# --- Custom Instruction Set for Enhanced SAP-1 ---
ISA = {
    "LDA": (0x1, True),   # Load Accumulator A from memory
    "LDB": (0x2, True),   # Load Register B from memory
    "ADD": (0x3, False),  # Add contents of A and B
    "SHL_A": (0x4, False), # Shift A left
    "SHR_A": (0x5, False), # Shift A right
    "SHL_B": (0x6, False), # Shift B left
    "SHR_B": (0x7, False), # Shift B right
    "JUMP": (0x8, True),  # Jump to address
    "HLT": (0x9, False),  # Halt execution
}

# --- Helper Functions ---
def is_binary_token(s):
    # Treat only 0bxxxx as binary, not plain numbers like 10 or 11
    return s.lower().startswith("0b") and re.fullmatch(r"0b[01]+", s.lower()) is not None

def parse_number(tok):
    tok = tok.strip()
    if is_binary_token(tok): return int(tok, 2)
    if tok.startswith(("0x","0X")): return int(tok, 16)
    if tok.lower().startswith("0b"): return int(tok, 2)
    # Default: treat plain numeric strings (10, 11, etc.) as decimal
    return int(tok, 10)

def tokenize(src):
    for raw in src.splitlines():
        line = raw.split(";")[0].split("#")[0].strip()
        if line: yield line

# --- Pass 1: label collection and token parsing ---
def first_pass(lines):
    pc=0; labels={}; out=[]
    for line in lines:
        if ":" in line:
            lab,line = line.split(":",1); lab=lab.strip(); line=line.strip()
            if lab:
                if lab in labels: raise ValueError(f"Duplicate label: {lab}")
                labels[lab]=pc
            if not line: out.append(("NOPLINE",[],pc)); continue
        toks=line.replace(","," ").split()
        out.append((toks[0].upper(), toks[1:], pc))
        if toks[0].upper()=="ORG": pc = parse_number(toks[1]) & 0xF
        else: pc=(pc+1)&0xF
    return labels,out

# --- Assembler Core ---
def assemble(src):
    mem=[0x00]*16
    labels, lines = first_pass(list(tokenize(src)))
    pc=0
    for op,args,at in lines:
        if op=="NOPLINE": pc=at; continue
        if op=="ORG": pc=parse_number(args[0])&0xF; continue
        if op=="DATA":
            mem[pc]=parse_number(args[0])&0xFF; pc=(pc+1)&0xF; continue
        if op not in ISA: raise ValueError(f"Unknown instruction: {op}")
        opcode, needs = ISA[op]; operand=0
        if needs:
            if not args: raise ValueError(f"{op} needs an operand at address {pc:01X}")
            a=args[0]; operand=(labels[a]&0xF) if a in labels else (parse_number(a)&0xF)
        mem[pc]=((opcode&0xF)<<4)|(operand&0xF); pc=(pc+1)&0xF
    return mem

# --- Main Program ---
def main():
    import argparse
    parser=argparse.ArgumentParser(description="SAP-1 assembler -> 16-byte hex image")
    parser.add_argument("file", nargs="?")
    args,_=parser.parse_known_args()
    if args.file:
        src=open(args.file,"r",encoding="utf-8").read()
    else:
        print("Enter SAP-1 assembly. Type END on a line by itself to finish:")
        buf=[]
        while True:
            try: line=input()
            except EOFError: break
            if line.strip()=="END": break
            buf.append(line)
        src="\n".join(buf)
    mem=assemble(src)
    print(" ".join(f"{b:02X}" for b in mem))

if __name__=="__main__":
    main()
