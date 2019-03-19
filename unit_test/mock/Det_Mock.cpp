//
// Created by Guillaume Sottas on 2019-03-01.
//

#include "Det_Mock.h"

Det_Mock *Det_Mock::singleton = nullptr;

Std_ReturnType Det_ReportError(uint16 moduleId, uint8 instanceId, uint8 apiId, uint8 errorId)
{
    return Det_Mock::instance().Det_ReportError(moduleId, instanceId, apiId, errorId);
}

Std_ReturnType Det_ReportRuntimeError(uint16 moduleId, uint8 instanceId, uint8 apiId,
                                      uint8 errorId)
{
    return Det_Mock::instance().Det_ReportRuntimeError(moduleId, instanceId, apiId, errorId);
}
