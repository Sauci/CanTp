/**
 * @file Std_Types.h
 * @author Guillaume Sottas
 * @date 14/10/2016
 */

#ifndef STD_TYPES_H
#define STD_TYPES_H

#ifdef __cplusplus

extern "C" {

#endif /* ifdef __cplusplus */

#include "Compiler.h"
#include "Platform_Types.h"

#ifndef STD_ON

#define STD_ON (0x01u)

#endif /* #ifndef STD_ON */

#ifndef STD_OFF

#define STD_OFF (0x00u)

#endif /* #ifndef STD_OFF */

#ifndef E_OK

#define E_OK (0x00u)

#endif /* #ifndef E_OK */

#ifndef E_NOT_OK

#define E_NOT_OK (0x01u)

#endif /* #ifndef E_NOT_OK */

#ifndef TRUE

#define TRUE (0x01u)

#endif /* #ifndef TRUE */

#ifndef FALSE

#define FALSE (0x00u)

#endif /* #ifndef FALSE */

#ifndef STD_LOW

#define STD_LOW (0x00u)

#endif /* #ifndef STD_LOW */

#ifndef STD_HIGH

#define STD_HIGH (0x01u)

#endif /* #ifndef STD_HIGH */

#ifndef NULL_PTR

#define NULL_PTR ((void *)0x00u)

#endif /* #ifndef NULL_PTR */

typedef uint32 Std_ReturnType;

typedef struct
{
    uint16 vendorID;
    uint16 moduleID;
    uint8 sw_major_version;
    uint8 sw_minor_version;
    uint8 sw_patch_version;
} Std_VersionInfoType;

#ifdef __cplusplus
}

#endif /* ifdef __cplusplus */

#endif /* #ifndef STD_TYPES_H */
