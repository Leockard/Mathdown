# main.py
# Convert a .Mmd file into regular Markdown.

code_flag_begin = "{Mathematica"
chunk_header = "Mmd-chunk-begin-id-"
NCHUNKS = 0
SEP = "```"

#######################
### AUXILIARY FUNCTIONS
#######################

def is_code_chunk(chunk):
    """Returns whether or not <chunk> is flagged as code.
    @param chunk: a string
    """
    return chunk.find(code_flag_begin) == 0

def remove_chunk_header(chunk):
    """Removes the {Mathematica opts...} header from each chunk."""
    return "\n".join(chunk.split("\n")[1:])

def make_chunk_header(c):
    """Returns an appropriate code chunk header that will be embedded in the input code so
    that we can trace what output came from where.
    """
    global NCHUNKS
    NCHUNKS += 1
    return "\nPrint@" + "\"" + chunk_header + str(NCHUNKS) + "\"\n"

def make_out_name(in_name):
    """Returns an appropriate output file name from the input file name.
    @param in_name: string.
    """
    name, ext = input_name.split(".")[:2]
    return name + "." + ext[1:]


##################################
### OUTPUT CHUNK PARSING FUNCTIONS
##################################

def parse_raw_output(out):
    """Processes the output of running all code chunks together. Returns a list of strings,
    one with the ouput of each chunk.
    @param out: the raw output returned by executing the code in WolframKernel.
    """
    import re
    out_chunks = re.split("\"" + chunk_header + ".*\"", out)
    out_chunks = filter(None, out_chunks)

    return out_chunks

def pretty_up_output(out):
    """Processes the output chunk list into a suitable format for embedding into the .md file.
    @param out: output chunk list.
    """
    return ["\n\n" + SEP + o for o in out]


#################################
### INPUT CHUNK PARSING FUNCTIONS
#################################

def parse_chunk_options(chunk):
    """Parses options of the form {Mathematica opts...}.
    @param chunk: a string. 
    """
    return []

def generate_code(chunks, opts):
    """Generates code to run from all chunks. All chunks are run at once. Correspondingly,
    this returns one single string with all code.
    @param chunks: a list of all code chunks. Each chunk still has the {Mathematica opts...} directive.
    @param opts: a list of lists of parsed options, one for each chunk.
    """
    chunks = [remove_chunk_header(c) for c in chunks]
    
    code = ""
    for c in chunks:
        code = code + make_chunk_header(c) + c

    return code

def execute_code(code):
    """Calls WolframKernel over <code>.
    @param code: a string containing Mathematica code.
    """
    import tempfile
    import subprocess
    
    # create a temp file with the code we need to run
    temp = tempfile.NamedTemporaryFile()
    temp.write(code)
    temp.seek(0)

    # execute code with WolframKernel
    output = subprocess.check_output(["WolframKernel", "-noprompt"], stdin = temp.file)
    temp.close()

    return parse_raw_output(output)


##################################
### TOP LEVEL PROCESSING FUNCTIONS
##################################

def process_all_chunks(chunk_list):
    """Processes all code chunks.
    @param <chunk_list>: a list of strings.
    """
    opt_list = [parse_chunk_options(c) for c in chunk_list]
    output_list = execute_code(generate_code(chunk_list, opt_list))

    return output_list

def make_markdown(text):
    """Converts the contents of a .Mmd file into Markdown.
    @param text: string read from a .Mmd file.
    """
    # get and process the code chunks
    chunks = mmd.split(SEP)
    outputs = process_all_chunks([c for c in chunks if is_code_chunk(c)])
    outputs = pretty_up_output(outputs)
    
    # add output to original Markdown
    # each output goes immediately after the corresponding input chunk
    i = 0
    j = 0
    while j < len(chunks):
        if is_code_chunk(chunks[j]):
            chunks.insert(j + 1, outputs[i])
            i += 1
        j += 1

    # delete any empty outputs
    code = SEP.join(chunks)
    code = code.replace(SEP + "\n" + SEP, "")
    
    return code


##################################
### MAIN
##################################

if __name__ == "__main__":
    from sys import argv

    # check for necessary file name
    if len(argv) < 2:
        print "A .Mmd file is needed."
        exit(1)

    # boilerplate file opening
    input_name = argv[1]
    try: 
        with open(input_name, 'r') as f:
            mmd = f.read()
    except IOError:
        print "No such file or directory: " + input_name
        exit(1)

    # make magic!
    output_name = make_out_name(input_name)
    markdown = make_markdown(mmd)

    # boilerplate file writing
    try: 
        with open(output_name, 'w') as f:
            f.write(markdown)
    except IOError:
        print "Couldn't create file: " + output_name
        exit(1)

    exit(0)
