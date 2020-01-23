import copy
import re
import os
from shutil import copyfile


IO = ['input', 'output', 'inout'] # verilog/sverilog singal I/O directions
TYPES = ['logic', 'reg', 'wire'] # verilog/sverilog signal types
IO_MAX = max( [len(_) for _ in IO] ) # max character width
TYPES_MAX = max( [len(_) for _ in TYPES] )
EXTENSIONS = ['.v', '.sv'] # only search for files with these extensions
comment = "//"

def get_files(a_path='.', extension_list=[]):
    """ a_path: a path of interest
        extension_list: a list of extensions of interest
        return: return a list of absolute paths of files, extensions of which are in <extension_list>
    """
    target_files = list()
    for item in os.listdir(a_path):
        if os.path.isfile(item):
            file_name, file_extension = os.path.splitext(item)
            if file_extension in extension_list:
                target_files.append(os.path.join(a_path, item))
    if(target_files):
        return target_files
    else:
        print(f"Found 0 files with extension {extension_list} in path \"{a_path}\". Aborting program...")
        exit(1)

def get_file_lines(fpath):
    """ open a file and return its lines
        fpath: absolute path of a file
        return: lines of the file
    """
    assert(os.path.exists(fpath)), f"File path \"{fpath}\" does not exist"
    with open(fpath, 'r') as fh:
        return fh.readlines()

def strip_comment(s, c=comment):
    if c in s:
        return s[:s.find(c)], s[s.find(c):]
    else:
        return s, ''


class VerilogBeautifier:
    ################################### VERILOG(SVERILOG) CODE BLOCKS ###############################
    ### 1. Top parameters:
    ### A top parameter line format: "param_name = param_expression".
    ### A top parameter block example:


    def beautify_top_params(self,inds):
        """
        beautify top parameter block. modify "self.fo_lines"
        inds: a tuple, (start_i, finish_i)
        return: 0~success; 1~failure
        a parameter block example:
        #(
            //--------- AXI PARAMETERS ------- # start_i
            AXI_DW     = 128                 , // AXI DATA    BUS WIDTH
            AXI_AW     = 40                  , // AXI ADDRESS BUS WIDTH
            AXI_RRESPW = 2                   , // AXI RRESP   BITS WIDTH
            //--------- ASI CONFIGURE --------
            ASI_OD     = 4                   , // ASI OUTSTANDING DEPTH
            ASI_ARB    = 0                   , // 1-GRANT READ WITH HIGHER PRIORITY; 0-GRANT WRITE WITH HIGHER PRIORITY
            //--------- SLAVE ATTRIBUTES -----
            SLV_WS     = 1                   , // SLAVE MODEL READ WAIT STATES CYCLE
            //-------- DERIVED PARAMETERS ----
            AXI_WSTRBW = AXI_BYTES           , // AXI WSTRB BITS WIDTH
            AXI_BYTESW = $clog2(AXI_BYTES+1)
        )( # finish_i
        """
        #1: #######################
        ##### VERIFY INDEXES ######
        ###########################
        start_i = inds[0]
        finish_i = inds[1]
        assert finish_i > start_i, f"start_i = {start_i}; finish_i = {finish_i}"
        #2: #######################
        ##### GET CHAR WIDTHs #####
        ###########################
        n = 0 # parameter declaration number
        for i, line in enumerate(self.fo_lines[start_i:finish_i], start_i):
            if re.match(r"\s*//\W+\s*(\w+\s+)+\W+$", line): # a comment line, e.g.: "//--------- word1 word2 ---------"
                continue
            elif re.match(r"\s*\w+\b\s*=\s*.+,\s*$", line_nc): # a parameter declare, e.g.: "AXI_WSTRBW = AXI_BYTES           , // AXI WSTRB BITS WIDTH"
                continue
            elif 0:
                pass
    def walk_through(self): # walking through lines from top to bottom
        """
        beautify top parameter block of a verilog/sv module
        """
        ######################
        #### TARGET LINES ####
        ######################
        lines = self.fo_lines
        assert lines==self.fi_lines
        #1: ##################
        ####### VERIFY #######
        ######################
        Inside_module = False # starts at "module xxx"
        Inside_params = False # starts at "#("
        indent = ' '*4
        name_mcw = -1 # parameter name max character width
        expr_mcw = -1 # parameter expression max character width
        expr_mcw_limit = 20 # parameter expression max character width limit
        for i, line in enumerate(self.fi_lines):
            line_nc, line_comment = strip_comment(line)
            if (not Inside_module):
                if re.match(r"^\s*module\s*", line_nc):
                    assert re.match(r"^\s*module\s+\w+\s*$", line_nc), f"Unorthodox module declaration: line {i}: {line}" # e.g.: correct: "module xxx"; incorrect: "module xxx("
                    Inside_module = True
                else:
                    assert re.match(r"^\s*`*", line_nc), f"Illegal line {i}: {line}"
                continue
            if Inside_module:
                if not Inside_params:
                    assert re.match(r"^#[(]\s*$", line_nc), f"Unorthodox symbol declaration: line {i}: {line}"
                    Inside_params = True
                    continue
                else:

    def select_a_file(self):
        """ select a file from <self.fi_paths> and return
        """
        assert(self.fi_paths), f"self.fi_paths is an empty list: {self.fi_paths}."
        for i, fn in enumerate(self.fi_paths):
            print(f'{i}: {fn}')
        n = input(f"Enter a number to select a file(press Enter to quit): ")
        try:
            n = int(n)
            a_file = self.fi_paths[n]
            if self.db_mode:
                print(f"Selected file {n}: \"{a_file}\"")
            return a_file
        except:
            print("Invalid input. Exiting program...")
            exit(1)

    def __init__(self, db_mode=True):
        """
            db_mode: debug mode
        """
        self.db_mode = db_mode
        self.fi_paths = get_files(os.getcwd(), EXTENSIONS)
        self.fi_path = self.select_a_file()
        self.fi_lines = get_file_lines(self.fi_path)
        self.fo_lines = copy.deepcopy(self.fi_lines) # fo_lines: lines to be output, initial it to fi_lines

if __name__ == '__main__':
    db_mode = True
    vb = VerilogBeautifier(db_mode)



