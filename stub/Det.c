/**
 * @file Det.h
 * @author Guillaume Sottas
 * @date 27/10/2016
 */

#include "Det.h"

Std_ReturnType Det_ReportError(uint16 moduleId,
                               uint8 instanceId,
                               uint8 apiId,
                               uint8 errorId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)errorId;

    return E_OK;
}

Std_ReturnType Det_ReportRuntimeError(uint16 moduleId,
                                      uint8 instanceId,
                                      uint8 apiId,
                                      uint8 errorId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)errorId;

    return E_OK;
}

Std_ReturnType Det_ReportTransientFault(uint16 moduleId,
                                        uint8 instanceId,
                                        uint8 apiId,
                                        uint8 faultId)
{
    (void)moduleId;
    (void)instanceId;
    (void)apiId;
    (void)faultId;

    return E_OK;
}
