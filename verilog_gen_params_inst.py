import re
fn = "parameters.txt"
fn_o = "parameters_out.txt"

step1 = f"Copy parameter declarations in the file {fn}, with format like this:"

#with open("parameters.txt", 'r') as fh:
#    lines = fh.readlines()
#    lines_new = list()
#    for i, line in enumerate(lines):
#        line_striped = line.strip()
#        line_new = 'f"'+line_striped+r'\n'+'"'
#        lines_new.append(line_new)
#
#for _ in lines_new:
#    print(_)

exm_list = [
f"//--- AXI BIT WIDTHs\n",
f"AXI_DW     = 128                 , // AXI DATA    BUS WIDTH\n",
f"AXI_AW     = 40                  , // AXI ADDRESS BUS WIDTH\n",
f"AXI_IW     = 8                   , // AXI ID TAG  BITS WIDTH\n",
f"AXI_LW     = 8                   , // AXI AWLEN   BITS WIDTH\n",
f"AXI_SW     = 3                   , // AXI AWSIZE  BITS WIDTH\n",
f"AXI_BURSTW = 2                   , // AXI AWBURST BITS WIDTH\n",
f"AXI_BRESPW = 2                   , // AXI BRESP   BITS WIDTH\n",
f"AXI_RRESPW = 2                   , // AXI RRESP   BITS WIDTH\n",
f"//--- ASI SLAVE CONFIGURE\n",
f"SLV_OD     = 4                   , // SLAVE OUTSTANDING DEPTH\n",
f"SLV_RD     = 64                  , // SLAVE READ BUFFER DEPTH\n",
f"SLV_WS     = 2                   , // SLAVE READ WAIT STATES CYCLE\n",
f"SLV_WD     = 64                  , // SLAVE WRITE BUFFER DEPTH\n",
f"SLV_BD     = 4                   , // SLAVE WRITE RESPONSE BUFFER DEPTH\n",
f"SLV_ARB    = 0                   , // 1-GRANT READ HIGHER PRIORITY; 0-GRANT WRITE HIGHER PRIORITY\n",
f"//--- DERIVED PARAMETERS\n",
f"AXI_WSTRBW = AXI_DW/8            , // AXI WSTRB BITS WIDTH\n",
f"SLV_BITS   = AXI_DW              ,\n",
f"SLV_BYTES  = SLV_BITS/8          ,\n",
f"SLV_BYTEW  = $clog2(SLV_BYTES+1)\n"
]

#print(step1)
#for _ in exm_list:
#    print(_)

######## main #######
pn_n = 0
with open(fn, 'r') as fh:
    lines = fh.readlines()
    lines_new = list()
    for i, line in enumerate(lines):
        line_striped = line.strip()
        if re.match(r"//", line_striped):
            line_new = line_striped+'\n'
        else:
            pn = re.match(r"\b\w+\b", line_striped)[0]
            line_new = f".{pn}({pn})"
            if i<len(lines)-1:
                line_new = line_new + ','+'\n'
        pn_n = pn_n+1
        lines_new.append(line_new)

with open(fn_o, 'w') as fh:
    fh.writelines(lines_new)
print(f'found {pn_n} parameters')
print(f'written {pn_n} lines into file "{fn_o}"')
