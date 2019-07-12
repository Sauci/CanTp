import os
import sys

from cffi import FFI
from cffi.verifier import cleanup_tmpdir
from importlib import import_module
from io import StringIO
from math import ceil
from re import sub
from unittest.mock import MagicMock

from pycparser.c_ast import FuncDecl, NodeVisitor
from pycparser.c_generator import CGenerator as Generator
from pycparser.c_parser import CParser
from pcpp.preprocessor import Preprocessor as Pp

from .cffi_config import build_directory, \
    source as cfg_src, \
    header as cfg_hdr, \
    compile_definitions as cfg_cd, \
    include_directories as cfg_id, \
    CodeGen


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


class Preprocessor(Pp):
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
                 include_dirs=tuple(),
                 define_macros=tuple(),
                 compile_flags=tuple(),
                 link_flags=tuple(),
                 build_dir=''):
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
        if name in sys.modules:
            self.ffi_module = sys.modules[name]
        else:
            self.cdef(str(CFFIHeader(self.header, func_decl.locals, func_decl.extern)))
            self.set_source(name, source,
                            include_dirs=include_dirs,
                            define_macros=list(tuple(d.split('=')) for d in define_macros),
                            extra_compile_args=list(compile_flags),
                            extra_link_args=list(link_flags))
            lib_path = self.compile(tmpdir=build_dir)
            sys.path.append(os.path.dirname(lib_path))
            self.ffi_module = import_module(name)

    @property
    def mocked(self):
        return self.ffi_header.mocked

    @property
    def ffi(self):
        return self.ffi_module.ffi

    @property
    def lib(self):
        return self.ffi_module.lib


class CanTpTest(object):
    def __init__(self,
                 config,
                 initialize=True,
                 rx_buffer_size=0x0FFF):
        self.available_rx_buffer = rx_buffer_size
        self.can_if_tx_data = list()
        self.can_tp_rx_data = list()
        #cleanup_tmpdir(tmpdir=build_directory)
        code_gen = CodeGen(config)
        with open(os.path.join(build_directory, 'CanTp_PBcfg.h'), 'w') as fp:
            fp.write(code_gen.header)
        with open(cfg_src, 'r') as fp:
            source = fp.read()
        with open(cfg_hdr, 'r') as fp:
            header = fp.read()
        self.config = MockGen('_cffi_can_tp_pbcfg_{}'.format(config.get_id),
                              code_gen.source,
                              code_gen.header,
                              define_macros=cfg_cd,
                              include_dirs=cfg_id + [build_directory],
                              build_dir=build_directory)
        self.code = MockGen('_cffi_can_tp',
                            source,
                            header,
                            define_macros=cfg_cd,
                            include_dirs=cfg_id + [build_directory],
                            compile_flags=('-g', '-O0', '-fprofile-arcs', '-ftest-coverage'),
                            link_flags=('-g', '-O0', '-fprofile-arcs', '-ftest-coverage'),
                            build_dir=os.path.dirname(__file__))
        if initialize:
            self.code.lib.CanTp_Init(self.code.ffi.cast('const CanTp_ConfigType *', self.config.lib.CanTp_Config))
            if self.code.lib.CanTp_State != self.code.lib.CANTP_ON:
                raise ValueError('CanTp module not initialized correctly...')

        self.can_if_transmit = MagicMock()
        self.det_report_error = MagicMock()
        self.det_report_runtime_error = MagicMock()
        self.det_report_transient_fault = MagicMock()
        self.pdu_r_can_tp_copy_rx_data = MagicMock()
        self.pdu_r_can_tp_copy_tx_data = MagicMock()
        self.pdu_r_can_tp_rx_indication = MagicMock()
        self.pdu_r_can_tp_start_of_reception = MagicMock()
        self.pdu_r_can_tp_tx_confirmation = MagicMock()
        for func in self.code.mocked:
            self.ffi.def_extern(func)(getattr(self, convert(func)))
        self.can_if_transmit.return_value = self.define('E_OK')
        self.det_report_error.return_value = self.define('E_OK')
        self.det_report_runtime_error.return_value = self.define('E_OK')
        self.det_report_transient_fault.return_value = self.define('E_OK')
        self.pdu_r_can_tp_rx_indication.return_value = None
        self.pdu_r_can_tp_tx_confirmation.return_value = None
        self.pdu_r_can_tp_start_of_reception.return_value = self.code.lib.BUFREQ_OK
        self.pdu_r_can_tp_copy_rx_data.return_value = self.code.lib.BUFREQ_OK
        self.pdu_r_can_tp_copy_tx_data.return_value = self.code.lib.BUFREQ_OK
        self.pdu_r_can_tp_start_of_reception.side_effect = self._pdu_r_can_tp_start_of_reception
        self.pdu_r_can_tp_copy_rx_data.side_effect = self._pdu_r_can_tp_copy_rx_data

    def _pdu_r_can_tp_start_of_reception(self, _i_pdu_id, _pdu_info, _tp_sdu_length, buffer_size):
        buffer_size[0] = self.available_rx_buffer
        return self.pdu_r_can_tp_start_of_reception.return_value

    def _pdu_r_can_tp_copy_rx_data(self, _rx_pdu_id, pdu_info, buffer_size):
        if pdu_info.SduDataPtr != self.code.ffi.NULL and pdu_info.SduLength != 0:
            for idx in range(pdu_info.SduLength):
                self.can_tp_rx_data.append(pdu_info.SduDataPtr[idx])
        buffer_size[0] = self.available_rx_buffer
        return self.pdu_r_can_tp_copy_rx_data.return_value

    def get_pdu_info(self, payload, overridden_size=None, meta_data=None):
        if isinstance(payload, str):
            payload = [ord(c) for c in payload]
        sdu_data = self.code.ffi.new('uint8 []', list(payload))
        if overridden_size is not None:
            sdu_length = overridden_size
        else:
            sdu_length = len(payload)
        pdu_info = self.code.ffi.new('PduInfoType *')
        pdu_info.SduDataPtr = sdu_data
        pdu_info.SduLength = sdu_length
        if meta_data:
            raise NotImplementedError
        else:
            pdu_info.MetaDataPtr = self.code.ffi.NULL
        return pdu_info

    def get_receiver_single_frame(self,
                                  payload=(0xFF,),
                                  af='CANTP_STANDARD',
                                  n_ae=0xAE,
                                  n_ta=0x7A,
                                  padding=None):
        if len(payload) > self.get_payload_size(af, 'SF'):
            raise ValueError('multi frame message...')
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]
        payload = list(payload)
        pci = [(0 << 4) | (len(payload) & 0x0F)]
        tmp_return = n_ai + pci + payload
        if padding is not None:
            [tmp_return.append(padding) for _ in range(8 - len(tmp_return))]
        return tmp_return

    @staticmethod
    def get_receiver_flow_control(flow_status='continue to send',
                                  bs=1,
                                  st_min=0,
                                  af='CANTP_STANDARD',
                                  n_ae=0xAE,
                                  n_ta=0x7A,
                                  padding=None):
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]
        pci = [(3 << 4) | {'continue to send': 0,
                           'wait': 1,
                           'overflow': 2}[flow_status],
               bs,
               st_min]
        return n_ai + pci + (([padding] * (4 if n_ai else 5)) if padding is not None else [])

    @staticmethod
    def get_payload_size(af, frame_type):
        return 8 - {
            'CANTP_STANDARD': {
                'SF': 1, 'FF': 2, 'CF': 1, 'FC': 3
            },
            'CANTP_NORMALFIXED': {
                'SF': 1, 'FF': 2, 'CF': 1, 'FC': 3
            },
            'CANTP_EXTENDED': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            },
            'CANTP_MIXED': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            },
            'CANTP_MIXED29BIT': {
                'SF': 2, 'FF': 3, 'CF': 2, 'FC': 4
            }
        }[af][frame_type]

    def get_receiver_multi_frame(self,
                                 payload=(0xFF,) * 8,
                                 af='CANTP_STANDARD',
                                 n_ae=0xAE,
                                 n_ta=0x7A,
                                 bs=1,
                                 padding=None):
        cf = list()
        tmp_pl = list(payload)
        n_ai = {
            'CANTP_STANDARD': [],
            'CANTP_NORMALFIXED': [],
            'CANTP_EXTENDED': [n_ta],
            'CANTP_MIXED': [n_ae],
            'CANTP_MIXED29BIT': [n_ae]
        }[af]

        ff_pci = [(1 << 4) | ((len(payload) & 0xF00) >> 8), len(payload) & 0x0FF]
        pl = [tmp_pl.pop(0) for _ in range(min((8 - len(n_ai) - len(ff_pci), len(payload))))]
        ff = n_ai + ff_pci + pl
        if bs:
            fbc = ceil(len(tmp_pl) / self.get_payload_size(af, 'CF') * bs)
        else:
            fbc = ceil(len(tmp_pl) / self.get_payload_size(af, 'CF'))
        sn = 0
        for _ in range(fbc) if bs else range(1):
            for _ in range(bs) if bs else range(fbc):
                sn += 1
                cf_pci = [(2 << 4) | (sn & 0x0F)]
                pl = [tmp_pl.pop(0) for _ in range(8 - len(n_ai) - len(cf_pci)) if len(tmp_pl)]
                cf.append(n_ai + cf_pci + pl)
        if padding and len(cf[-1]) < 8:
            cf[-1] += [padding] * (8 - len(cf[-1]))
        return ff, cf

    def define(self, name):
        return self.code.pp.defines[name]

    @property
    def lib(self):
        return self.code.lib

    @property
    def ffi(self):
        return self.code.ffi

    @property
    def available_rx_buffer(self):
        return self._available_rx_buffer - len(self.can_tp_rx_data)

    @available_rx_buffer.setter
    def available_rx_buffer(self, value):
        self._available_rx_buffer = value
