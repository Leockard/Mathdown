# main.py
# Convert a .Mmd file into regular Markdown.

import re

code_flag_begin = "{Mathematica"
chunk_header = "Mmd-chunk-begin-id-"
NCHUNKS = 0
SEP = "```"
GRAPHICS_DIR = "figures"

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

def create_figures_dir(title):
    """Checks if the figures dir is already created. If it isn't, create it and return
    True. If it is, immedately return True. Only returns False when creating the directory
    causes an error.
    """
    import os
    figs_dir = os.getcwd() + "/" + title + "-" + GRAPHICS_DIR
    try:
        if not os.path.exists(figs_dir):
            os.makedirs(figs_dir)
            return True
    except OSError:
        return False

def make_image_link(filename):
    """Returns the Markdown code that embeds the image <filename>."""
    return "![](" + filename + ")"

def is_link(exp):
    """Returns True if the expression is a Markdown link, i.e., if it begins with a !"""
    return exp.strip().find("!") == 0


##################################
### OUTPUT CHUNK PARSING FUNCTIONS
##################################

def parse_raw_output(out):
    """Processes the output of running all code chunks together. Returns a list of strings,
    one with the ouput of each chunk.
    @param out: the raw output returned by executing the code in WolframKernel.
    """
    out_chunks = re.split("\"" + chunk_header + ".*\"", out)
    out_chunks = list(filter(None, out_chunks))

    return out_chunks

def pretty_up_output(out):
    """Processes the output chunk list into a suitable format for embedding into the .md file.
    @param out: output chunk list.
    """
    # the "\n" at the beginning is essential since we will then remove empty code chunks
    # i.e., we need the input and ouptut chunks to be separated by at least one empty line
    return [is_link(o) and o or ("\n\n" + SEP + o + SEP) for o in out]

def weave_output(chunks, outputs):
    """Pastes output chunks immediately after the corresponding input
    chunk. Returns one string containing both input and output.
    @param chunks: all chunks (text and code).
    @param outputs: output chunks.
    """
    i = 0
    j = 0
    while j < len(chunks):
        if is_code_chunk(chunks[j]):
            chunks[j] = SEP + chunks[j] + SEP
            chunks.insert(j + 1, outputs[i])
            i += 1
        j += 1

    return "".join(chunks)

def get_graphics(output):
    """Returns a list of Graphics[] expressions found in output.
    @param output: output string.
    """
    # if we do
    #     re.findall("(Graphics\[.*])", output)
    # directly over output, we would have to assume that WolframKernel outputs each Graphics[]
    # on a single line (no newline) and that it separates multiple Graphics[] by at least one
    # newline. To avoid that assumption, we add a newline in front of each Graphics[]
    with_newlines = output.replace("Graphics[", "\nGraphics[")
    return re.findall("(Graphics\[.*])", with_newlines)

def process_all_graphics(outputs, title):
    """Looks for Graphics[] expressions inside each output chunk and replaces them with an
    embedded image.
    @param outputs: list of output chunks.
    """
    return [process_graphics(outputs[i], title, "chunk-" + str(i)) for i in range(len(outputs))]

def process_graphics(output, title, fileprefix, ext="jpg"):
    """Processes Graphics[] objects in one output chunk. Calls Export["fileprefix_i.ext",
    graphics], where graphics is extracted from the output chunk and i is an integer
    denoting the order in which the graphics object appears in the output.
    @param output: output string.
    @param fileprefix: the file to save the image to.
    """
    def make_command(g, i):
        return "Export[FileNameJoin[{\"" + title + "-" + GRAPHICS_DIR + "\", \"" + fileprefix + "-" + str(i) + "."+ext + "\"}], " + g + "]"
    
    figure_dir = create_figures_dir(title)
    i = 1;
    for g in get_graphics(output):
        # WE NEED ERROR HANDLING HERE!!!
        outfile = execute_code(make_command(g, i))
        output = output.replace(g, make_image_link(outfile.rstrip()))
        i += 1

    return output


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
    temp.write(bytes(code, 'UTF-8'))
    temp.seek(0)

    # execute code with WolframKernel
    # check_output() returns a bytes object, need to cast to string
    output = subprocess.check_output(["WolframKernel", "-noprompt"], stdin = temp.file)
    output = output.decode("utf-8")
    temp.close()

    return output


##################################
### TOP LEVEL PROCESSING FUNCTIONS
##################################

def process_all_chunks(chunk_list):
    """Processes all code chunks.
    @param <chunk_list>: a list of strings.
    """
    opt_list = [parse_chunk_options(c) for c in chunk_list]
    output_list = parse_raw_output(execute_code(generate_code(chunk_list, opt_list)))

    return output_list

def pretty_up_code(md):
    """Processes the markdown and sets it up for pretty printing.
    @param md: raw markdown.
    """
    # delete any empty outputs
    md = md.replace(SEP + "\n" + SEP, "")
    return md
    
def make_markdown(text, title=""):
    """Converts the contents of a .Mmd file into Markdown.
    @param text: string read from a .Mmd file.
    @param title: string to be appended to the figures directory, if any.
    """
    chunks = mmd.split(SEP)
    outputs = process_all_chunks([c for c in chunks if is_code_chunk(c)])
    outputs = process_all_graphics(outputs, title)
    outputs = pretty_up_output(outputs)
    markdown = weave_output(chunks, outputs)
    markdown = pretty_up_code(markdown)

    return markdown


##################################
### MAIN
##################################

if __name__ == "__main__":
    from sys import argv

    # check for necessary file name
    if len(argv) < 2:
        print("A .Mmd file is needed.")
        exit(1)

    # boilerplate file opening
    input_name = argv[1]
    try: 
        with open(input_name, 'r') as f:
            mmd = f.read()
    except IOError:
        print("No such file or directory: " + input_name)
        exit(1)

    # make magic!
    output_name = make_out_name(input_name)
    markdown = make_markdown(mmd, input_name.split(".")[0])

    # boilerplate file writing
    try: 
        with open(output_name, 'w') as f:
            f.write(markdown)
    except IOError:
        print("Couldn't create file: " + output_name)
        exit(1)

    exit(0)
