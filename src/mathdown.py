# mathdown.py
# Convert a .Mmd file into regular Markdown.


import re


#############################
### MathKernel external calll
#############################

def execute_code(code):
    """Calls WolframKernel over <code>."""
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



####################
### Chunk class
####################

class Chunk:
    """A chunk of text within a .Mmd document."""

    def __init__(self, doc, index, text = ""):
        self.text = text
        """The text of this chunk."""

        self.document = doc
        """The Document object this chunk is part of."""

        self.index = index
        """The unique index corresponding to this Chunk within the Document."""

    def process_output(self, output):
        """Returns the formatted output. <output> must be the resulting text from
        running the code inside this chunk (if any).
        """
        # Override me!
        return output



####################
### CodeChunk class
####################    
    
class CodeChunk(Chunk):
    """A code chunk within a .Mmd document. <self.text> preserves the ```
    separators and options. Use the <code> property to read the
    executable Mathematica code form this chunk.
    """

    graphics_regex = re.compile(r"(.*?Plot(3D)?|Graphics)\[(.*)\]")
    """Regex used to determine if a particular line of Mathematica code will output a Graphics object."""

    code_regex = re.compile(r"\s*```{Mathematica.*?}\s*(.*)\s*```", re.DOTALL)
    """Regex used to determine if a particular chunk is code."""

    link_regex = re.compile(r'"(.*?)"')
    """Regex used to find graphics output when processing code."""

    chunk_header = "Mmd-chunk-begin-id-"
    """Internal use."""

    sep = "```"
    """Delimiter that flags where code chunks begin and end."""

    OPTS_INLINE = 0
    """Inline flag."""

    available_opts = [OPTS_INLINE]
    """List of all possible chunk options."""
    

    def __init__(self, doc, index, text):
        Chunk.__init__(self, doc, index, text)
        
        self._header = ""
        """Internal use. See property header instead."""
        
        self._code = ""
        """Internal use. See property code instead."""

        self.has_graphics = False
        """Whether or not this chunk will output Graphics objects. Use
        only after property code has been computed.
        """

        self._options = None
        """Internal use. See property options instead."""

    @property
    def options(self):
        """List of options. See CodeChunk.available_opts for a list of all possible options."""
        if self._options == None:
            self._options = []

            # inline?
            if not re.match(r'^```{Mathematica.*?}\n', self.text):
                self._options.append(self.OPTS_INLINE)

        return self._options

    @property
    def code(self):
        """The executable Mathematica code from this chunk. If there are any lines
        that output Graphics objects in this chunk, they will be replaced by an
        Export[] expression. For this, the parent Document must make sure the graphics
        directory exists before using this property.
        """
        if not self._code:
            self._code = re.match(self.code_regex, self.text).group(1)

            # If this chunk will output a Graphics object, replace that line with a call to Export[].
            # In this way, all figures are automatically saved instead of displayed.
            if re.match(self.graphics_regex, self._code):
                self.has_graphics = True
                self._code = re.sub(self.graphics_regex, r'Export["' + self.document.graphics_dirname + "chunk-" + str(self.index) + "<CHANGE_ME>" + ".jpg" + r'", \1[\3]]', self._code)

                # We left a <CHANGE_ME> flag in place. Now, we replace it iteratively with
                # the corresponding ordinal number. (We can't do that in a single re.sub call)
                code = self._code
                i = 1
                match = re.search(r"<CHANGE_ME>", code)
                while match:
                    code = code[:match.start()] + "-" + str(i) + code[match.end():]
                    match = re.search(r"<CHANGE_ME>", code)
                    i += 1
                self._code = code

            else:
                self.has_graphics = False

        return self._code

    @property
    def header(self):
        """The internal-use header attached to keep track of output chunks when
        running code.
        """
        if not self._header:
            self._header = self._make_chunk_header(self.text)
        return self._header

    def _make_chunk_header(self, index):
        """Returns an appropriate code chunk header that will be embedded in the input code so
        that we can trace what output came from where.
        """
        return "\nPrint@" + "\"" + self.chunk_header + str(index) + "\"\n"

    def process_output(self, out):
        """Returns the correct output after applying this chunk's options. <out> must be the
        raw output text from MathKernel."""
        output = out

        # handle graphics options and links
        if self.has_graphics:
            output = re.sub(self.link_regex, r'![]("\1")', "\n" + output.strip())
            output = self.text + output
            
        # handle inline option
        elif self.OPTS_INLINE in self.options:
            output = out.strip()

        # default case
        else:
            if re.match(r'^\s*$', output):
                output = self.sep + "\n" + self.sep
            else:
                output = "\n\n" + self.sep + "\n" + output.strip() + "\n" + self.sep

            output = self.text + output

        return output

    
####################
### Document class
####################

class Document:
    """A .Mmd document."""

    code_flag_begin = "{Mathematica"
    """Delimiter at the beginning of every Mathematica code chunk."""

    sep = "```"
    """Delimiter that flags where code chunks begin and end."""

    
    def __init__(self, path):
        """Creates a Document instance representing the file at <path>."""

        self.path = path
        """Note the path isn't read until a call to convert()"""

        self.text = ""
        """The full text in the file."""

        self.chunks = []
        """A list of Chunk objects of all chunks found in this document."""

        self.code_chunks = []
        """A list of CodeChunk objects of code chunks in this document."""

        self.markdown = ""
        """The Markdown text corresponding to the contents of the file."""

        self._graphics_dir_exists = False
        """Whether or not the directory exists. Internal use."""

    @property
    def filename(self):
        """The name of the file, extracted from self.path."""
        return self.path.split("/")[-1]

    @property
    def out_filename(self):
        """Returns the name for the output .md file."""
        return self.filename.split(".")[0] + ".md"

    @property
    def graphics_dirname(self):
        """The name of the directory where all graphics go."""
        return self.filename.split(".")[0] + "-graphics/"

    def convert(self):
        """Converts the .Mmd to .md, processing all chunks in self.chunks."""

        # read from disk
        try: 
            with open(self.path, 'r') as f:
                mmd = f.read()
                self.text = mmd
        except IOError:
            print("No such file or directory: " + self.path + ".")
            exit(1)

        # do some magic!
        outputs = self.run_code_chunks()
        # outputs = [is_link(o) and o or ("\n\n" + SEP + o + SEP) for o in outputs]

        # place output chunks where they're supposed to be
        markdown = self.weave_output(outputs)

        # delete any empty output chunks
        markdown = markdown.replace(self.sep + "\n" + self.sep, "")

        self.markdown = markdown

    def run_code_chunks(self):
        # Parse document and generate Chunk objects
        self._parse_chunks()
        
        # Since we process all chunks in a single kernel call, we need to  we need to keep
        # track of where each chunk starts. That's why we add c.header before any code.
        # The trailing \n after c.code is necessary so that the kernel executes the last
        # expression correctly
        code = "\n".join([c.header + c.code + "\n" for c in self.chunks if isinstance(c, CodeChunk)])

        # Make sure the graphics directory exists
        if re.search(CodeChunk.graphics_regex, code):
            self._make_graphics_dir()

        # Call the kernel - this may take a while...
        output = execute_code(code)
        
        # Partition the output by the added headers
        out_chunks = re.split("\"" + CodeChunk.chunk_header + ".*\"", output)
        out_chunks = list(filter(None, out_chunks))

        # Let each chunk manage its own output
        out_chunks = [self.code_chunks[i].process_output(out_chunks[i]) for i in range(len(out_chunks))]

        return out_chunks

    def weave_output(self, outputs):
        """Places output chunks where they correspond."""
        chunks = [c.text for c in self.chunks]

        # replace each code chunk with the result from CodeChunk.process_output()
        i = 0
        j = 0
        while i < len(chunks):
            if self._is_code_chunk(chunks[i]):
                chunks[i] = outputs[j]
                j += 1
            i += 1
    
        return "".join(chunks)

    def _make_graphics_dir(self):
        """Checks if the graphics directory is already created. If it isn't, create
        it and return True. If it is, immedately return True. Only returns False when
        creating the directory causes an error.
        """
        if self._graphics_dir_exists:
            return True

        import os
        figs_dir = os.getcwd() + "/" + self.graphics_dirname
        try:
            if not os.path.exists(figs_dir):
                os.makedirs(figs_dir)
                self._graphics_dir_exists = True
                return True
            else:
                self._graphics_dir_exists = True
                return True
        except OSError:
            return False

    def _parse_chunks(self):
        """Parse the file and create Chunk objects, stored in self.chunks."""
        regex = re.compile(r'(```.*?```)', re.DOTALL)
        text_chunks = re.split(regex, self.text)

        self.chunks = []
        self.code_chunks = []

        index = 0
        for t in text_chunks:
            if self._is_code_chunk(t):
                c = CodeChunk(self, index, t)
                self.code_chunks.append(c)
            else:
                c = Chunk(self, index, t)
                
            index +=1
            self.chunks.append(c)

    def _is_code_chunk(self, text):
        """Returns whether or not <chunk> is flagged as code."""
        return text.find(self.code_flag_begin) == len(self.sep)

    def write_md(self):
        """Writes markdown to output file."""

        # boilerplate file writing
        try: 
            with open(self.out_filename, 'w') as f:
                f.write(self.markdown)
        except IOError:
            print("Couldn't create file: " + self.out_filename + ".")
            exit(1)



##################################
### MAIN
##################################

if __name__ == "__main__":
    from sys import argv
    
    if len(argv) < 2:
        print("A .Mmd file is needed.")
        exit(1)

    doc = Document(argv[1])
    doc.convert()
    doc.write_md()
        
    exit(0)
