/**
 * @file Platform_Types.h
 * @author Guillaume Sottas
 * @date 14/10/2016
 */

#ifndef PLATFORM_TYPES_H
#define PLATFORM_TYPES_H

#ifdef __cplusplus

extern "C"
{

#endif /* ifdef __cplusplus */

typedef unsigned char uint8;

typedef signed char sint8;

typedef unsigned short uint16;

typedef signed short sint16;

typedef unsigned int uint32;

typedef signed int sint32;

typedef uint32 uint8_least;

typedef sint32 sint8_least;

typedef uint32 uint16_least;

typedef sint32 sint16_least;

typedef uint32 uint32_least;

typedef sint32 sint32_least;

typedef uint8_least boolean;

typedef float ieee_float;

#ifdef __cplusplus

}

#endif /* ifdef __cplusplus */

#endif /* #ifndef PLATFORM_TYPES_H */
