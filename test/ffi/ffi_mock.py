import os
import sys

from cffi import FFI
from importlib import import_module
from io import StringIO
from re import sub
from unittest.mock import MagicMock

from pycparser.c_ast import FuncDecl, NodeVisitor
from pycparser.c_generator import CGenerator as Generator
from pycparser.c_parser import CParser
from pcpp.preprocessor import Preprocessor as PP


def convert(name):
    s1 = sub('(.)([A-Z][a-z][_]+)', r'\1_\2', name)
    return sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


class FunctionDecl(NodeVisitor):
    def __init__(self, source_string):
        self.static = set()
        self.extern = set()
        self.locals = set()
        self.visit(CParser().parse(source_string))

    def visit_Decl(self, node):
        if isinstance(node.type, FuncDecl):
            if 'static' in node.storage:
                self.static.add(node)
            elif 'extern' in node.storage:
                self.extern.add(node)
            else:
                self.locals.add(node)


class CFFIHeader(Generator):
    def __init__(self, interface, local, extern):
        super(CFFIHeader, self).__init__()
        self.locals = set(e.name for e in local)
        self.extern = set(e.name for e in extern)
        self.mocked = set()
        self.string = self.visit(CParser().parse(interface))

    def __str__(self):
        return self.string

    def visit_Decl(self, n, no_type=False):
        if isinstance(n.type, FuncDecl):
            if n.name in self.extern:
                self.mocked.add(n.name)
                n.storage.remove('extern')
                n.storage.append('extern "Python+C"')
        return Generator.visit_Decl(self, n)


class Preprocessor(PP):
    def __init__(self):
        super(Preprocessor, self).__init__()
        self.defines = dict()

    def on_directive_handle(self, directive, tokens, if_pass_thru):
        if directive.value == 'define':
            name = [t.value for t in tokens if t.type == 'CPP_ID']
            value = [t.value for t in tokens if t.type in 'CPP_INTEGER']
            if len(name) and len(value):
                name = name[0]
                value = value[0].rstrip('UuLl')
                try:
                    value = int(value, 10)
                except ValueError:
                    try:
                        value = int(value, 16)
                    except ValueError as e:
                        raise e
                self.defines[name] = value
        return super(Preprocessor, self).on_directive_handle(directive, tokens, if_pass_thru)


class MockGen(FFI):
    def __init__(self,
                 name,
                 source,
                 header,
                 output,
                 sources=tuple(),
                 include_dirs=tuple(),
                 define_macros=tuple()):
        super(MockGen, self).__init__()
        self.pp = Preprocessor()
        for include_directory in include_dirs:
            self.pp.add_path(include_directory)
        for compile_definition in (' '.join(d.split('=')) for d in define_macros):
            self.pp.define(compile_definition)
        self.pp.parse(header)
        handle = StringIO()
        self.pp.write(handle)
        self.header = handle.getvalue()
        func_decl = FunctionDecl(self.header)
        self.ffi_header = CFFIHeader(self.header, func_decl.locals, func_decl.extern)
        self.cdef(str(CFFIHeader(self.header, func_decl.locals, func_decl.extern)))
        self.set_source(name, source,
                        sources=sources,
                        include_dirs=include_dirs,
                        define_macros=list(tuple(d.split('=')) for d in define_macros))
        lib_path = self.compile()
        sys.path.append(os.path.dirname(lib_path))
        self.ffi_module = import_module(name)
        self.can_if_transmit = MagicMock()
        self.det_report_error = MagicMock()
        self.det_report_runtime_error = MagicMock()
        self.det_report_transient_fault = MagicMock()
        self.pdu_r_can_tp_copy_rx_data = MagicMock()
        self.pdu_r_can_tp_copy_tx_data = MagicMock()
        self.pdu_r_can_tp_rx_indication = MagicMock()
        self.pdu_r_can_tp_start_of_reception = MagicMock()
        self.pdu_r_can_tp_tx_confirmation = MagicMock()
        for func in self.mocked:
            self.ffi.def_extern(func)(getattr(self, convert(func)))

    @property
    def mocked(self):
        return self.ffi_header.mocked

    @property
    def ffi(self):
        return self.ffi_module.ffi

    @property
    def lib(self):
        return self.ffi_module.lib
