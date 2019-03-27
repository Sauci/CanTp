import os
from cffi import FFI
from pycparser.c_ast import FuncDecl, NodeVisitor
from pycparser.c_generator import CGenerator
from pycparser.c_parser import CParser

input_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'input')

with open(os.path.join(input_dir, 'source.c'), 'r') as fp:
    source = fp.read()

with open(os.path.join(input_dir, 'header.h'), 'r') as fp:
    header = CGenerator().visit(CParser().parse(fp.read()))


# call the C generator to format the source/header file. this step is not really required, but is
# useful to generate clean code coverage reports.
for s, name in ((source, 'source.c'), (header, 'header.h')):
    formatted_string = CGenerator().visit(CParser().parse(s))
    with open(os.path.join(input_dir, name), 'w') as fp:
        fp.write(formatted_string)


class FunctionFinder(NodeVisitor):
    def __init__(self, source_string):
        self.declarations = set()
        self.definitions = set()
        self.calls = set()
        self.visit(CParser().parse(source_string))

    def visit_Decl(self, node):
        if isinstance(node.type, FuncDecl):
            self.declarations.add(node)

    def visit_FuncDef(self, node):
        self.definitions.add(node.decl.name)
        v = FunctionCall()
        v.visit(node)
        self.calls.update(v.function)


class FunctionCall(NodeVisitor):
    def __init__(self):
        self.function = set()

    def visit_FuncCall(self, node):
        self.function.add(node.name.name)


class CFFICDefGenerator(CGenerator):
    def __init__(self, source_string, mock_func, declarations):
        self.mock_func = mock_func
        #print('bellow function will be automatically mocked:\n- ' + '\n- '.join(sorted(mock_func)))
        super(CFFICDefGenerator, self).__init__()
        self.updated = self.visit(CParser().parse(source_string))
        remaining = list()
        for declaration in [d for d in declarations if d.name in self.mock_func and 'static' not in d.storage]:
            if 'extern' in declaration.storage:
                declaration.storage.remove('extern')
            declaration.storage = ['extern "Python+C"']
            remaining.append(CGenerator().visit(declaration) + ';')
            self.mock_func.remove(declaration.name)
        self.updated = '\n'.join(self.updated.splitlines() + remaining)

    def visit_Decl(self, n, *args, **kwargs):
        result = CGenerator.visit_Decl(self, n, *args, **kwargs)
        if isinstance(n.type, FuncDecl):
            if n.name in self.mock_func:
                result = 'extern "Python+C" ' + result
                self.mock_func.remove(n.name)
        return result


source_finder = FunctionFinder(source)
header_finder = FunctionFinder(header)

header = CFFICDefGenerator(header, source_finder.calls - source_finder.definitions,
                           source_finder.declarations | header_finder.declarations).updated

#with open(os.path.join(input_dir, 'header.h'), 'w') as fp:
#    fp.write(header)

ffi_builder = FFI()

ffi_builder.cdef(header)

ffi_builder.set_source('pycantp._cantp', source,
                       extra_compile_args=['-g', '-O0', '-fprofile-arcs', '-ftest-coverage'],
                       extra_link_args=['-g', '-O0', '-fprofile-arcs', '-ftest-coverage'])
