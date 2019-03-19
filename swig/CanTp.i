%module pycantp

%{
    #include "../stub/CanIf.h"
    #include "../stub/Std_Types.h"
    #include "../interface/CanTp.h"
    #include "../interface/CanTp_Cbk.h"
%}

%define SWIGRUNTIME_DEBUG
%enddef

%typemap(in) uint8 %{
    $1 = (int) PyInt_AsLong($input);
    if ($1 < 0x00u)
    {
        PyErr_SetString(PyExc_ValueError, "uint8: outside minimum allowed range 0x0000u");
        return NULL;
    }
    else if ($1 > 0xFFu)
    {
        PyErr_SetString(PyExc_ValueError, "uint8: outside maximum allowed range 0xFFFFu");
        return NULL;
    }
%}

%typemap(in) uint16 %{
    $1 = (int) PyInt_AsLong($input);
    if ($1 < 0x0000u)
    {
        PyErr_SetString(PyExc_ValueError, "uint16: outside minimum allowed range 0x0000u");
        return NULL;
    }
    else if ($1 > 0xFFFFu)
    {
        PyErr_SetString(PyExc_ValueError, "uint16: outside maximum allowed range 0xFFFFu");
        return NULL;
    }
%}

%typemap(in) uint32 %{
$1 = (int) PyInt_AsLong($input);
    if ($1 < (int)0)
    {
        PyErr_SetString(PyExc_ValueError, "uint32: outside minimum allowed range 0x0000u");
        return NULL;
    }
    else if ($1 > (int)0xFFFFFFFF)
    {
        PyErr_SetString(PyExc_ValueError, "uint32: outside maximum allowed range 0xFFFFu");
        return NULL;
    }
%}

PduIdType get_pdu_id(void);

const PduInfoType *get_p_pdu_info_type(void);

Std_ReturnType get_return_value(void);

Std_ReturnType CanIf_Transmit(PduIdType txPduId, const PduInfoType *pPduInfo);

void set_pdu_id(PduIdType pduId);

void set_p_pdu_info_type(PduInfoType *pPduInfo);

void set_return_value(Std_ReturnType returnValue);


void CanTp_MainFunction(void);

void CanTp_GetVersionInfo(Std_VersionInfoType *pVersionInfo);

%include "cpointer.i"
%include "typemaps.i"

%include "../stub/ComStack_Types.h"
%include "../stub/Std_Types.h"

%pointer_functions(sint8, pf_sint8);
%pointer_functions(sint16, pf_sint16);
%pointer_functions(sint8, pf_sint32);
%pointer_functions(uint8, pf_uint8);
%pointer_functions(uint16, pf_uint16);
%pointer_functions(uint32, pf_uint32);

%pointer_functions(PduLengthType, PduLengthType);
%pointer_functions(PduIdType, PduIdType);
%pointer_functions(PduInfoType, p_PduInfoType);
%pointer_functions(Std_VersionInfoType, p_Std_VersionInfoType);
