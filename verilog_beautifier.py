import copy
import re
import os
from shutil import copyfile

def get_char_len(a):
    """ return the sum of characters of each item in a list.
        a: input list
        return: l; character number
    """
    l = 0
    for item in a:
        l += len(item)
    return l

class VerilogBeautifier:

    def __init__(self):
        self.kw_direction = ['input', 'output', 'inout']
        self.kw_dir_max = max( [len(x) for x in self.kw_direction] )
        self.kw_signaltype = ['logic', 'wire', 'reg']
        self.kw_sig_max = max( [len(x) for x in self.kw_signaltype] )
        self.extension_list = ['.v', '.sv']
        self.cwd = os.getcwd()
        self.files_in = self.get_input_files()
        self.files_todo = self.select_one_file()
        self.files_paths = [os.path.join(self.cwd, file_name) for file_name in self.files_todo]

    def get_input_files(self):
        """ get the file paths of verilog or systemverilog files to be beautified.
            return: file paths list
        """
        files_in = list()
        for item in os.listdir():
            if os.path.isfile(item):
                item_name, item_extension = os.path.splitext(item)
                if item_extension in self.extension_list:
                    if not item_name.endswith('_copy'):
                        files_in.append(item)
        if files_in:
            return files_in
        else:
            print(f'No files with extensions {self.extension_list} found in "{self.cwd}". Exiting program...')
            exit(1)

    def select_one_file(self):
        """ select one file in self.files_in and return """
        files_in = list()
        if len(self.files_in)>1:
            print(f'Found {len(self.files_in)} verilog files in "{self.cwd}". Select a file to beautify:')
            for i, f in enumerate(self.files_in):
                print(f'{i}: {f}')
            f_i = int(input())
            #f_i = 0 # for test
            files_in.append(self.files_in[f_i])
        else:
            files_in.append(self.files_in[0])
        return files_in

    def copy_files(self):
        """ copy files in 'self.files_path' to back them up"""
        files_copy = list()
        for fn in self.files_todo:
            fn_name, fn_extension = os.path.splitext(fn)
            files_copy.append(fn_name+'_copy'+fn_extension)
        files_copy_paths = [os.path.join(self.cwd, file_name) for file_name in files_copy]
        for i, file_path in enumerate(self.files_paths):
            src = file_path
            dst = files_copy_paths[i]
            if os.path.isfile(dst):
                print(f'{dst} already exist, skip copying')
            else:
                print(f'copying src: {src}')
                print(f'copying dst: {dst}')
                copyfile(src,dst)

    def beautify_module_instances(self, lines, start_i, finish_i):
        """ perform module instantiation beautifying, e.g., .DW(DW) -> .DW( DW       )
        """
        #### get max character width of "param_m" and "param_s" as in: (.param_m(param_s))
        mexp = r"\.\w+"
        sexp = r"\(.+\)"
        m_max = -1 # master parameter character width
        m_line = ''
        s_max = -1 # slave parameter character width
        s_line = ''
        for i, line in enumerate(lines):
            ### skip uninterested lines
            if i not in range(start_i, finish_i):
                continue
            ### skip blank lines or comment lines
            if ( not line.strip() ) or ( re.match(r'\s*//', line )):
                    continue
            ### process interested lines:
            indent = re.match(r"\s*", line).group() # leading white spaces
            if '//' in line:
                comment = line[line.find('//'):]
            else:
                comment = ''
            param_m = re.findall(mexp, line) # ".dw" in ".dw(dw)"
            param_s = re.findall(sexp, line) # "(dw)" in ".dw(dw)"
            #print(f'param_s = {param_s}')
            if param_m:
                param_m = param_m[0][1:].strip() # "dw" in ".dw"
                if len(param_m)>m_max:
                    m_max = len(param_m)
                    m_line = line
            if param_s:
                param_s = param_s[0][1:-1].strip() # dw in "(dw)"
                if len(param_s)>s_max:
                    s_max = len(param_s)
                    s_line = line
        #print(f's_max = {s_max}')
        #print(f's_line = {s_line}')
        #print(f'm_max = {m_max}')
        #print(f'm_line = {m_line}')
        #input()
        for i, line in enumerate(lines):
            ### skip uninterested lines
            if i not in range(start_i, finish_i):
                continue
            ### skip blank lines or comment lines
            if ( not line.strip() ) or ( re.match(r'\s*//', line )):
                continue
            ### process interested lines:
            indent = re.match(r"\s*", line).group() # leading white spaces
            if not re.match(r'\s*\.\w+\s*\(.+\)', line):
                continue
            #if '//' in line:
            #    comment = line[line.find('//'):]
            #else:
            #    comment = ''
            line_end = line[line[:line.find('//')].rfind(')'):]
            #line_end = line[line.find(')'):] # starting from ")...."
            param_m = re.findall(mexp, line) # ".dw" in ".dw(dw)"
            param_s = re.findall(sexp, line) # "(dw)" in ".dw(dw)"
            if param_m:
                param_m = param_m[0][1:].strip() # "dw" in ".dw"
            else:
                print(f'param_m is empty! in {line}')
                print(f'mexp = {mexp}')
                print(re.findall(mexp, line))
                exit(1)
            if param_s:
                param_s = param_s[0][1:-1].strip() # dw in "(dw)"
            else:
                print(f'param_s is empty! in {line}')
                print(f'sexp = {sexp}')
                print(re.findall(sexp, line))
                exit(1)
            m_spaces = ' '*(m_max-len(param_m)+1) # spaces to be added after "param_m"
            s_spaces = ' '*(s_max-len(param_s))+' '
            line = indent+'.'+param_m+m_spaces+'('+' '+param_s+s_spaces+line_end
            lines[i] = line
        return lines

    def beautify_assign(self, lines, start_i, finish_i):
        """ lines: whole lines of the ongoing file to be beautified.
            perform assign alignment, e.g.: "assign A = b; // test"
        """
        kw = r"assign"
        kexp = r"assign +.+?="
        ksep = '='
        kend = ';'
        key_lines = lines[start_i:finish_i]
        lh_max = -1 # max character width of left-handed variable, e.g., 'assign A=B;' 'A' is the lh
        lh_max_line = ''
        rh_max = -1
        rh_max_line = ''
        lh_maxlimit = 20
        rh_maxlimit = 20
        ### get character width info
        for i, line in enumerate(key_lines, start_i):
            line = line.lstrip()
            if line.startswith('//') or not line:
                continue
            assert(line.startswith(kw))
            assert(re.match(kexp, line))
            lh = line[len(kw):line.find(ksep)].strip()
            rh = line[line.find(ksep)+1:line.find(kend)].strip()
            if len(lh)>lh_max and len(lh)<lh_maxlimit:
                lh_max = len(lh)
                lh_max_line = line
            if len(rh)>rh_max and len(rh)<rh_maxlimit:
                rh_max = len(rh)
                rh_max_line = line
            #if i>=167 and i<=170:
            #    print(f'start_i = {start_i}; finish_i = {finish_i}')
            #    print(f'lh_max = {lh_max}')
            #    print(f'rh_max = {rh_max}')
            #    print(f'lh_max_line = {lh_max_line}')
            #    print(f'rh_max_line = {rh_max_line}')
            #    input()
        ### align
        for i, line in enumerate(key_lines, start_i):
            indent = re.match(r"\s*", line).group()
            if not line.strip():
                line = '\n'
            elif line.lstrip().startswith('//'):
                line = indent + line.lstrip()
            else:
                line_copy = copy.deepcopy(line)
                line = line.lstrip()
                char_list = line.split()
                char_len_original = get_char_len(char_list) # character length of the line before modified
                after_end = line[line.find(kend):] # e.g., ";//test" in "assign A=a;//test"
                lh = line[len(kw):line.find(ksep)].strip()
                rh = line[line.find(ksep)+1:line.find(kend)].strip()
                lh_new = lh+' '*(lh_max-len(lh))
                if len(lh)>lh_max:
                    rh_new = rh+' '*(rh_max-len(rh)-(len(lh)-lh_max))
                else:
                    rh_new = rh+' '*(rh_max-len(rh))
                line = indent+kw+' '+lh_new+' '+ksep+' '+rh_new+after_end
                char_len = get_char_len(line.split())
                if(char_len_original != char_len):
                    print(line)
                    print(line_copy)
                    exit(1)
            lines[i] = line
        return lines

    def beautify_declarations(self, top_ports, lines, start_i, finish_i):
        """ lines: whole lines of the ongoing file to be beautified.
            top_ports==True: perform top ports declaration alignment.
            top_ports==False: perform inside module signals declaration alignment.
        """
        if top_ports:
            print(f'Beautifying top ports...')
        else:
            print(f'Beautifying inside module signals declaration...')
        if top_ports:
            indent = ' '*4
            puct = r','
        else:
            indent = ''
            puct = r';'
        key_lines = lines[start_i:finish_i]
        for i, line in enumerate(key_lines, start_i):
            if line.strip():
                if top_ports:
                    assert(any( [line.strip().startswith(x) for x in ['//', 'input', 'output', 'inout']] )), f'line{i}: {line}'
                else:
                    assert(any( [line.strip().startswith(x) for x in ['//', 'logic', 'wire', 'reg']] )), f'{line}'
        kw_direction = self.kw_direction
        kw_dir_max = self.kw_dir_max
        kw_signaltype = self.kw_signaltype
        kw_sig_max = self.kw_sig_max
        ### ----- 1. prepare: get max character width infomation
        bw_max = -1 # max character width of the first part in brackets, e.g. "[AXI_AW-1" in [AXI_AW-1:0]
        bw_max_line = ''
        bw2_max = -1 # ":0]" in [AXI_AW-1:0]
        bw2_max_line = ''
        dir_max = -1 # direction character max width
        dir_max_line = ''
        sig_max = -1 # signal type character max width
        sig_max_line = ''
        name_max = -1 # signal name
        name_max_line = ''
        for i, line in enumerate(key_lines, start_i):
            line = line.lstrip()
            if line.startswith('//') or not line:
                continue
            # get dir_max and sig_max
            if top_ports:
                dir_name = re.findall(r'\w+', line)[0]
                sig_name = re.findall(r'\w+', line)[1]
                assert(dir_name in kw_direction)
            else:
                dir_name = ''
                sig_name = re.findall(r'\w+', line)[0]
            if len(dir_name) > dir_max:
                dir_max = len(dir_name)
                dir_max_line = line
            if sig_name in kw_signaltype:
                if len(sig_name) > sig_max:
                    sig_max = len(sig_name)
                    sig_max_line = line
            # get bits width character max width
            results = re.findall(r'\[.+?\]', line)
            if results:
                results = results[0]
                results_list = results.split(':')
                bw = ''.join(results_list[0].split()) # e.g., "[AXI_AW-1" in "[AXI_AW-1:0]"
                bw2 = ''.join(results_list[1].split())# e.g., "0]" in "[AXI_AW-1:0]"
                if len(bw) > bw_max:
                    bw_max = len(bw)
                    bw_max_line = line
                if len(bw2) > bw2_max:
                    bw2_max = len(bw2)
                    bw2_max_line = line
            # get name max character width
            if '//' in line:
                line = line[:line.find('//')]
            if i-start_i==len(key_lines)-1 and top_ports:
                assert(len(re.findall(puct, line))==0) # assert no puct in the last line of top ports
            else:
                assert(len(re.findall(puct, line))==1) # assert 1 puct if not the last line of top ports
            results = re.findall(r'(\w+)(\[.+.\])*', line)
            results = ''.join(results[-1])
            assert(results), f'Found no signal name in line {i}: {line}'
            if len(results) > name_max:
                name_max = len(results)
                name_max_line = line
        #print(f'dir_max = {dir_max}')
        #print(f'dir_max_line = {dir_max_line}')
        #print(f'sig_max = {sig_max}')
        #print(f'sig_max_line = {sig_max_line}')
        #print(f'bw_max = {bw_max}')
        #print(f'bw_max_line = {bw_max_line}')
        #print(f'bw2_max = {bw2_max}')
        #print(f'bw2_max_line = {bw2_max_line}')
        #print(f'name_max = {name_max}')
        #print(f'name_max_line = {name_max_line}')
        #input()
        ### ----- 2. get aligned segments
        ### line is split into 5 segments:
        ### seg[0]: direction
        ### seg[1]: signal type
        ### seg[2]: bit width
        ### seg[3]: signal name
        ### seg[4]: comments
        seg = ['']*5
        new_key_lines = list()
        for i, line in enumerate(key_lines, start_i):
            if top_ports:
                pass
            else:
                indent = re.match(r"\s*", line).group()
            if not line.strip():
                line = '\n'
            elif line.lstrip().startswith('//'):
                line = indent + line.lstrip()
            else:
                line = line.lstrip()
                word_list = re.findall(r'\w+', line)
                ### seg[0]: direction
                if top_ports:
                    seg[0] = word_list[0]
                    assert(seg[0] in kw_direction)
                    seg[0] += ' '*(dir_max-len(seg[0])+1) # left align
                else:
                    seg[0] = ''
                ### seg[1]: signal type
                if top_ports:
                    seg[1] = word_list[1]
                else:
                    seg[1] = word_list[0]
                if seg[1] in kw_signaltype:
                    seg[1] += ' '*(sig_max-len(seg[1])+1)
                else:
                    if not top_ports:
                        print(f' Found no signal type while performing logic declaration align in line {i}: {line}. Exiting program...')
                        exit(1)
                    else:
                        seg[1] = ' '*(sig_max+1)
                ### seg[2]: bit width declaration
                results = re.findall(r'\[.+?\]', line)
                if results:
                    results = results[0] # e.g.: [AXI_IW-1    : 0]
                    results_list = results.split(':') # ['AXI_IW-1    ', ' 0']
                    results_list = [''.join(x.split()) for x in results_list] # ['AXI_IW-1', '0']
                    results_list[0] += ' '*(bw_max-len(results_list[0])+1)
                    results_list[1] += ' '*(bw2_max-len(results_list[1])+1)
                    results_list[1] = ' '+results_list[1]
                    seg[2] = ':'.join(results_list)
                else:
                    seg[2] = ' '*(bw_max+1+1+1+bw2_max+1)
                ### seg[3]: signal name
                if '//' in line:
                    line_temp = line[:line.find('//')].strip()
                else:
                    line_temp = line
                if seg[2].strip(): # if bit width declatrations exists. e.g., [AXI_IW-1:0]
                    seg[3] = line_temp[line_temp.find(']')+1:].strip()
                elif seg[1].strip(): # else if signal type declatrations exists. e.g., logic [AXI_IW-1:0]
                    seg1_strip = seg[1].strip()
                    seg[3] = line_temp[line_temp.find(seg1_strip)+len(seg1_strip):].strip()
                else: # only direction declatrations exists. e.g., input a
                    seg[3] = line_temp[line_temp.find(seg[0].strip())+len(seg[0].strip()):].strip()
                if not seg[3]:
                    print(f'Signal name not found in line {i}: {line}. Exiting program...')
                    exit(1)
                if seg[3][-1]==puct:
                    seg[3] = seg[3][:-1]
                    seg[3] = seg[3].strip()
                if i-start_i==len(key_lines)-1 and top_ports:
                    seg[3] = seg[3]+' '*(name_max-len(seg[3])+1)+' '
                else:
                    seg[3] = seg[3]+' '*(name_max-len(seg[3])+1)+puct
                ### seg[4]: comments
                if '//' in line:
                    results = line[line.find('//'):]
                    seg[4] = ' '+results
                else:
                    seg[4] = '\n'
                line = indent+''.join(seg)
                #if i-start_i==len(key_lines)-1 and top_ports:
                    #for _ in seg:
                    #    print(_)
                    #input(f'line = {line}' )
            new_key_lines.append(line)
            #print(line, end='')
        lines[start_i:finish_i] = new_key_lines
        return lines

    def beautify(self, file_path):
        print(f'Beautifying {file_path}')
        with open(file_path, 'r') as fh:
            lines = fh.readlines()
            fh_lines = copy.deepcopy(lines)
        ### 1. top ports Beautifying:
        start_key = ')(' # port declatrations start from this
        finish_key = ');' # finish at this
        start_i = -1 # start line number
        finish_i = 0 # finish line number
        for i, line in enumerate(lines):
            if line.strip()==start_key:
                start_i = i+1
                break
        for i, line in enumerate(lines):
            if line.strip()==finish_key:
                finish_i = i
                break
        lines = self.beautify_declarations(True, lines, start_i, finish_i)
        #assert(len(lines)==len(lines))
        #for i, line in enumerate(lines):
        #    if i not in range(start_i, finish_i):
        #        assert(line == fh_lines[i]) # assert only lines outside ragne (start_i, finish_i) are not modified

        ### 2. inside-module-signals declaration(logic, wire, reg) Beautifying:
        inside_declaration = False
        start_i = -1
        finish_i = 0
        for i, line in enumerate(lines):
            sline = line.strip()
            if not sline:
                continue
            if any( [sline.startswith(x) for x in self.kw_signaltype] ) and not inside_declaration:
                start_i = i
                inside_declaration = True
            if (not any( [sline.startswith(x) for x in self.kw_signaltype] )) and (not sline.startswith('//')) and inside_declaration: # if a line does not start with ['logic', 'wire', 'reg'] or ['//']
                finish_i = i
                inside_declaration = False
                # 2.1. perfom alignment on a signal declaration block
                lines = self.beautify_declarations(False, lines, start_i, finish_i)
                #break # only perform beautifying on the 1st logic block

        ## 3. 'assign' Beautifying:
        inside_declaration = False
        start_i = -1
        finish_i = 0
        kw = r"assign"
        for i, line in enumerate(lines):
            sline = line.strip()
            if not sline:
                continue
            if sline.startswith(kw) and not inside_declaration:
                start_i = i
                inside_declaration = True
            if (not sline.startswith(kw)) and (not sline.startswith('//')) and inside_declaration: # if a line does not start with "assign" and it's not a comment line
                finish_i = i
                inside_declaration = False
                # 2.1. perfom alignment
                lines = self.beautify_assign(lines, start_i, finish_i)
                #break # only perform beautifying on the 1st block
        lines = self.beautify_assign(lines, start_i, finish_i)

        ## 4. module instances Beautifying:
        start_i = -1
        finish_i = 0
        for i, line in enumerate(lines):
            if re.match(r'\s*\w+\s*#\s*\(', line):
                start_i = i
                #print(f'i={i}; line={line}')
            if re.match(r'\s*\)\s*\w+\s*\(', line):
                finish_i = i
                lines = self.beautify_module_instances(lines, start_i, finish_i)
                start_i = i
                #print(f'i={i}; line={line}')
                #input()
            if re.match(r'\s*\);', line):
                finish_i = i
                lines = self.beautify_module_instances(lines, start_i, finish_i)
        #lines = self.beautify_module_instances(lines, 221, 229)
        #lines = self.beautify_module_instances(lines, 214, 219)
        #for _ in lines:
        #    print(_)

        ### final: validify characters
        assert(len(lines)==len(fh_lines))
        for i, line in enumerate(lines):
            line_len = get_char_len(lines[i].split())
            fhline_len = get_char_len(fh_lines[i].split())
            assert(line_len==fhline_len), f'line_line={line_len}; fhline_len={fhline_len}\nline  = "{line}"\nfhline="{fh_lines[i]}"'

        with open(file_path, 'w') as fh:
            print(f'written to file {file_path}')
            fh.writelines(lines)

    def beautify_all(self):
        ### backup files
        print(f'files to beautify: ')
        for file_path in self.files_paths:
            print(file_path)
        self.copy_files()
        ### beautify files in "self.files_paths"
        for file_path in self.files_paths:
            self.beautify(file_path)

if __name__ == '__main__':
    print("hello...")
    v = VerilogBeautifier()
    v.beautify_all()

