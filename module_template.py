from datetime import date

lines = list()

lines.append(f"// Author: LiBing\n")
lines.append(f"// Date: {date.today()}\n")
lines.append(f"// Description: \n\n")
lines.append(f"module \n")
lines.append(f"#(\n")
lines.append(f")(\n")
lines.append(f"    input rst_n,\n")
lines.append(f"    input clk  ,\n")
lines.append(f");\n")
lines.append(f"timeunit 1ns;\n")
lines.append(f"timeprecision 1ns;\n")
lines.append(f"always_ff @(posedge clk or negedge rst_n)\n")
lines.append(f"    if(!rst_n)\n")
lines.append(f"endmodule\n")
fn = input("input file name to save: ")
with open(fn, 'w') as fh:
    fh.writelines(lines)
print(f"Written {len(lines)} lines into file {fn}")
input()


