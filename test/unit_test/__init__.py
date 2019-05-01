import pytest
from .helper import *

try:
    from unittest.mock import ANY
except ImportError:
    from mock import ANY

single_frame_sizes = [pytest.param(fs, id='SF_DL = {}'.format(fs)) for fs in (1, 2, 6)]
multi_frames_sizes = [pytest.param(fs, id='FF_DL = {}'.format(fs)) for fs in (8, 4095)]

n_xx_timeouts = [10, 100, 0xFF]

n_as_timeouts = [pytest.param(t, id='N_As = {}ms'.format(t)) for t in n_xx_timeouts]
n_bs_timeouts = [pytest.param(t, id='N_Bs = {}ms'.format(t)) for t in n_xx_timeouts]
n_cs_timeouts = [pytest.param(t, id='N_Cs = {}ms'.format(t)) for t in n_xx_timeouts]

n_ar_timeouts = [pytest.param(t, id='N_Ar = {}ms'.format(t)) for t in n_xx_timeouts]
n_br_timeouts = [pytest.param(t, id='N_Br = {}ms'.format(t)) for t in n_xx_timeouts]
n_cr_timeouts = [pytest.param(t, id='N_Cr = {}ms'.format(t)) for t in n_xx_timeouts]


@pytest.fixture()
def handle():
    return CanTp()
