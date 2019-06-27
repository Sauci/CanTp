/**
 * @file Det.h
 * @author Guillaume Sottas
 * @date 27/10/2016
 */

#ifndef DET_H
#define DET_H

#ifdef __cplusplus

extern "C"
{

#endif /* #ifdef __cplusplus */

#ifndef STD_TYPES_H
#include "Std_Types.h"
#endif /* #ifndef STD_TYPES_H */

extern Std_ReturnType Det_ReportError(uint16 moduleId,
                                      uint8 instanceId,
                                      uint8 apiId,
                                      uint8 errorId);

extern Std_ReturnType Det_ReportRuntimeError(uint16 moduleId,
                                             uint8 instanceId,
                                             uint8 apiId,
                                             uint8 errorId);

extern Std_ReturnType Det_ReportTransientFault(uint16 moduleId,
                                               uint8 instanceId,
                                               uint8 apiId,
                                               uint8 faultId);

#ifdef __cplusplus

}

#endif /* #ifdef __cplusplus */

#endif /* #ifndef DET_H */
