from behave import *


@step('pVersionInfo parameter is a valid pointer to a Std_VersionInfoType structure')
def step_impl(context):
    context.version_info = context.can_tp.ffi.new('Std_VersionInfoType *')


@when('we call CanTp_GetVersionInfo')
def step_impl(context):
    context.return_value = context.can_tp.lib.CanTp_GetVersionInfo(context.version_info)


@step('pVersionInfo.vendorID is equal to 0')
def step_impl(context):
    assert context.version_info.vendorID == 0


@step('pVersionInfo.moduleID is equal to 14')
def step_impl(context):
    assert context.version_info.moduleID == 14


@step('pVersionInfo.sw_major_version is equal to 0')
def step_impl(context):
    assert context.version_info.sw_major_version == 0


@step('pVersionInfo.sw_minor_version is equal to 1')
def step_impl(context):
    assert context.version_info.sw_minor_version == 1


@step('pVersionInfo.sw_patch_version is equal to 0')
def step_impl(context):
    assert context.version_info.sw_patch_version == 0
