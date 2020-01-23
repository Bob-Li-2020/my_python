import re

def test(s, sub_exprs):
    assert re.match(''.join(sub_exprs), s)
    i = 0 # character index
    for sub_expr in sub_exprs:
        sub_string = re.match(sub_expr, s[i:]).group()
        i = i + len(sub_string)
        print(f"sub_string = {sub_string}")

if __name__ == "__main__":
    s = "AXI_DW = 128"
    sub_exprs = [r"\s*\b", r"\w+", r"\s*", r"=", r"\s*", r"\w+\b"]
    test(s, sub_exprs)
    input()
