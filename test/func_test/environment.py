from behave import *
from test.helper import *


@fixture
def module_can_tp(context):
    context.can_tp = CanTp()
    yield context.can_tp


def before_tag(context, tag):
    if tag == 'fixture.can_tp':
        use_fixture(module_can_tp, context)
