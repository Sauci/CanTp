#ifdef __arm__

#ifndef SECTION_VAR_FAST_NO_INIT_BOOLEAN

#define SECTION_VAR_FAST_NO_INIT_BOOLEAN \
    __attribute__((section(".ram_var_fast.no_init.boolean")))

#endif

#ifndef SECTION_VAR_FAST_NO_INIT_8

#define SECTION_VAR_FAST_NO_INIT_8 \
    __attribute__((section(".ram_var_fast.no_init.8_bit")))

#endif

#ifndef SECTION_VAR_FAST_NO_INIT_16

#define SECTION_VAR_FAST_NO_INIT_16 \
    __attribute__((section(".ram_var_fast.no_init.16_bit")))

#endif

#ifndef SECTION_VAR_FAST_NO_INIT_32

#define SECTION_VAR_FAST_NO_INIT_32 \
    __attribute__((section(".ram_var_fast.no_init.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_NO_INIT_UNSPECIFIED

#define SECTION_VAR_FAST_NO_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.no_init.unspecified")))

#endif

#ifndef SECTION_VAR_FAST_INIT_BOOLEAN

#define SECTION_VAR_FAST_INIT_BOOLEAN \
    __attribute__((section(".ram_var_fast.init.boolean")))

#endif

#ifndef SECTION_VAR_FAST_INIT_8

#define SECTION_VAR_FAST_INIT_8 \
    __attribute__((section(".ram_var_fast.init.8_bit")))

#endif

#ifndef SECTION_VAR_FAST_INIT_16

#define SECTION_VAR_FAST_INIT_16 \
    __attribute__((section(".ram_var_fast.init.16_bit")))

#endif

#ifndef SECTION_VAR_FAST_INIT_32

#define SECTION_VAR_FAST_INIT_32 \
    __attribute__((section(".ram_var_fast.init.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_INIT_UNSPECIFIED

#define SECTION_VAR_FAST_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.init.unspecified")))

#endif

#ifndef SECTION_VAR_FAST_CLEARED_BOOLEAN

#define SECTION_VAR_FAST_CLEARED_BOOLEAN \
    __attribute__((section(".ram_var_fast.cleared.boolean")))

#endif

#ifndef SECTION_VAR_FAST_CLEARED_8

#define SECTION_VAR_FAST_CLEARED_8 \
    __attribute__((section(".ram_var_fast.cleared.8_bit")))

#endif

#ifndef SECTION_VAR_FAST_CLEARED_16

#define SECTION_VAR_FAST_CLEARED_16 \
    __attribute__((section(".ram_var_fast.cleared.16_bit")))

#endif

#ifndef SECTION_VAR_FAST_CLEARED_32

#define SECTION_VAR_FAST_CLEARED_32 \
    __attribute__((section(".ram_var_fast.cleared.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_CLEARED_UNSPECIFIED

#define SECTION_VAR_FAST_CLEARED_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.cleared.unspecified")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_INIT_BOOLEAN

#define SECTION_VAR_FAST_POWER_ON_INIT_BOOLEAN \
    __attribute__((section(".ram_var_fast.power_on_init.boolean")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_INIT_8

#define SECTION_VAR_FAST_POWER_ON_INIT_8 \
    __attribute__((section(".ram_var_fast.power_on_init.8_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_INIT_16

#define SECTION_VAR_FAST_POWER_ON_INIT_16 \
    __attribute__((section(".ram_var_fast.power_on_init.16_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_INIT_32

#define SECTION_VAR_FAST_POWER_ON_INIT_32 \
    __attribute__((section(".ram_var_fast.power_on_init.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_INIT_UNSPECIFIED

#define SECTION_VAR_FAST_POWER_ON_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.power_on_init.unspecified")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_BOOLEAN

#define SECTION_VAR_FAST_POWER_ON_CLEARED_BOOLEAN \
    __attribute__((section(".ram_var_fast.power_on_cleared.boolean")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_8

#define SECTION_VAR_FAST_POWER_ON_CLEARED_8 \
    __attribute__((section(".ram_var_fast.power_on_cleared.8_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_16

#define SECTION_VAR_FAST_POWER_ON_CLEARED_16 \
    __attribute__((section(".ram_var_fast.power_on_cleared.16_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_32

#define SECTION_VAR_FAST_POWER_ON_CLEARED_32 \
    __attribute__((section(".ram_var_fast.power_on_cleared.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED

#define SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.power_on_cleared.unspecified")))

#endif

#ifndef SECTION_VAR_SLOW_NO_INIT_BOOLEAN

#define SECTION_VAR_SLOW_NO_INIT_BOOLEAN \
    __attribute__((section(".ram_var_slow.no_init.boolean")))

#endif

#ifndef SECTION_VAR_SLOW_NO_INIT_8

#define SECTION_VAR_SLOW_NO_INIT_8 \
    __attribute__((section(".ram_var_slow.no_init.8_bit")))

#endif

#ifndef SECTION_VAR_SLOW_NO_INIT_16

#define SECTION_VAR_SLOW_NO_INIT_16 \
    __attribute__((section(".ram_var_slow.no_init.16_bit")))

#endif

#ifndef SECTION_VAR_SLOW_NO_INIT_32

#define SECTION_VAR_SLOW_NO_INIT_32 \
    __attribute__((section(".ram_var_slow.no_init.32_bit")))

#endif

#ifndef SECTION_VAR_SLOW_NO_INIT_UNSPECIFIED

#define SECTION_VAR_SLOW_NO_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_slow.no_init.unspecified")))

#endif

#ifndef SECTION_VAR_SLOW_INIT_BOOLEAN

#define SECTION_VAR_SLOW_INIT_BOOLEAN \
    __attribute__((section(".ram_var_slow.init.boolean")))

#endif

#ifndef SECTION_VAR_SLOW_INIT_8

#define SECTION_VAR_SLOW_INIT_8 \
    __attribute__((section(".ram_var_slow.init.8_bit")))

#endif

#ifndef SECTION_VAR_SLOW_INIT_16

#define SECTION_VAR_SLOW_INIT_16 \
    __attribute__((section(".ram_var_slow.init.16_bit")))

#endif

#ifndef SECTION_VAR_SLOW_INIT_32

#define SECTION_VAR_SLOW_INIT_32 \
    __attribute__((section(".ram_var_slow.init.32_bit")))

#endif

#ifndef SECTION_VAR_SLOW_INIT_UNSPECIFIED

#define SECTION_VAR_SLOW_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_slow.init.unspecified")))

#endif

#ifndef SECTION_VAR_SLOW_CLEARED_BOOLEAN

#define SECTION_VAR_SLOW_CLEARED_BOOLEAN \
    __attribute__((section(".ram_var_slow.cleared.boolean")))

#endif

#ifndef SECTION_VAR_SLOW_CLEARED_8

#define SECTION_VAR_SLOW_CLEARED_8 \
    __attribute__((section(".ram_var_slow.cleared.8_bit")))

#endif

#ifndef SECTION_VAR_SLOW_CLEARED_16

#define SECTION_VAR_SLOW_CLEARED_16 \
    __attribute__((section(".ram_var_slow.cleared.16_bit")))

#endif

#ifndef SECTION_VAR_SLOW_CLEARED_32

#define SECTION_VAR_SLOW_CLEARED_32 \
    __attribute__((section(".ram_var_slow.cleared.32_bit")))

#endif

#ifndef SECTION_VAR_SLOW_CLEARED_UNSPECIFIED

#define SECTION_VAR_SLOW_CLEARED_UNSPECIFIED \
    __attribute__((section(".ram_var_slow.cleared.unspecified")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_INIT_BOOLEAN

#define SECTION_VAR_SLOW_POWER_ON_INIT_BOOLEAN \
    __attribute__((section(".ram_var_slow.power_on_init.boolean")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_INIT_8

#define SECTION_VAR_SLOW_POWER_ON_INIT_8 \
    __attribute__((section(".ram_var_slow.power_on_init.8_bit")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_INIT_16

#define SECTION_VAR_SLOW_POWER_ON_INIT_16 \
    __attribute__((section(".ram_var_slow.power_on_init.16_bit")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_INIT_32

#define SECTION_VAR_SLOW_POWER_ON_INIT_32 \
    __attribute__((section(".ram_var_slow.power_on_init.32_bit")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED

#define SECTION_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED \
    __attribute__((section(".ram_var_slow.power_on_init.unspecified")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN

#define SECTION_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN \
    __attribute__((section(".ram_var_slow.power_on_cleared.boolean")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_CLEARED_8

#define SECTION_VAR_SLOW_POWER_ON_CLEARED_8 \
    __attribute__((section(".ram_var_slow.power_on_cleared.8_bit")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_CLEARED_16

#define SECTION_VAR_SLOW_POWER_ON_CLEARED_16 \
    __attribute__((section(".ram_var_slow.power_on_cleared.16_bit")))

#endif

#ifndef SECTION_VAR_SLOW_POWER_ON_CLEARED_32

#define SECTION_VAR_SLOW_POWER_ON_CLEARED_32 \
    __attribute__((section(".ram_var_slow.power_on_cleared.32_bit")))

#endif

#ifndef SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED

#define SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED \
    __attribute__((section(".ram_var_fast.power_on_cleared.unspecified")))

#endif

#ifndef SECTION_CONST_BOOLEAN

#define SECTION_CONST_BOOLEAN \
    __attribute__((section(".flash_const.boolean")))

#endif

#ifndef SECTION_CONST_8

#define SECTION_CONST_8 \
    __attribute__((section(".flash_const.8_bit")))

#endif

#ifndef SECTION_CONST_16

#define SECTION_CONST_16 \
    __attribute__((section(".flash_const.16_bit")))

#endif

#ifndef SECTION_CONST_32

#define SECTION_CONST_32 \
    __attribute__((section(".flash_const.32_bit")))

#endif

#ifndef SECTION_CONST_UNSPECIFIED

#define SECTION_CONST_UNSPECIFIED \
    __attribute__((section(".flash_const.unspecified")))

#endif

#ifndef SECTION_CODE_FAST

#define SECTION_CODE_FAST \
    __attribute__((section(".ram_code_fast")))

#endif

#ifndef SECTION_CODE_SLOW

#define SECTION_CODE_SLOW \
    __attribute__((section(".ram_code_slow")))

#endif

#if defined(MEMMAP_ERROR)

#error unterminated memory section.

#else

#define MEMMAP_ERROR

#endif

#if defined(CanTp_START_SEC_VAR_FAST_NO_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_FAST_NO_INIT_BOOLEAN
SECTION_VAR_FAST_NO_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_NO_INIT_8)
#undef CanTp_START_SEC_VAR_FAST_NO_INIT_8
SECTION_VAR_FAST_NO_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_NO_INIT_16)
#undef CanTp_START_SEC_VAR_FAST_NO_INIT_16
SECTION_VAR_FAST_NO_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_NO_INIT_32)
#undef CanTp_START_SEC_VAR_FAST_NO_INIT_32
SECTION_VAR_FAST_NO_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_NO_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_NO_INIT_UNSPECIFIED
SECTION_VAR_FAST_NO_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_FAST_INIT_BOOLEAN
SECTION_VAR_FAST_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_INIT_8)
#undef CanTp_START_SEC_VAR_FAST_INIT_8
SECTION_VAR_FAST_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_INIT_16)
#undef CanTp_START_SEC_VAR_FAST_INIT_16
SECTION_VAR_FAST_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_INIT_32)
#undef CanTp_START_SEC_VAR_FAST_INIT_32
SECTION_VAR_FAST_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_INIT_UNSPECIFIED
SECTION_VAR_FAST_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_CLEARED_BOOLEAN)
#undef CanTp_START_SEC_VAR_FAST_CLEARED_BOOLEAN
SECTION_VAR_FAST_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_CLEARED_8)
#undef CanTp_START_SEC_VAR_FAST_CLEARED_8
SECTION_VAR_FAST_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_CLEARED_16)
#undef CanTp_START_SEC_VAR_FAST_CLEARED_16
SECTION_VAR_FAST_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_CLEARED_32)
#undef CanTp_START_SEC_VAR_FAST_CLEARED_32
SECTION_VAR_FAST_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_CLEARED_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_CLEARED_UNSPECIFIED
SECTION_VAR_FAST_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_BOOLEAN
SECTION_VAR_FAST_POWER_ON_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_8)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_8
SECTION_VAR_FAST_POWER_ON_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_16)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_16
SECTION_VAR_FAST_POWER_ON_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_32)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_32
SECTION_VAR_FAST_POWER_ON_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED
SECTION_VAR_FAST_POWER_ON_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_BOOLEAN)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_BOOLEAN
SECTION_VAR_FAST_POWER_ON_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_8)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_8
SECTION_VAR_FAST_POWER_ON_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_16)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_16
SECTION_VAR_FAST_POWER_ON_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_32)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_32
SECTION_VAR_FAST_POWER_ON_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_NO_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_SLOW_NO_INIT_BOOLEAN
SECTION_VAR_SLOW_NO_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_NO_INIT_8)
#undef CanTp_START_SEC_VAR_SLOW_NO_INIT_8
SECTION_VAR_SLOW_NO_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_NO_INIT_16)
#undef CanTp_START_SEC_VAR_SLOW_NO_INIT_16
SECTION_VAR_SLOW_NO_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_NO_INIT_32)
#undef CanTp_START_SEC_VAR_SLOW_NO_INIT_32
SECTION_VAR_SLOW_NO_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_NO_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_SLOW_NO_INIT_UNSPECIFIED
SECTION_VAR_SLOW_NO_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_SLOW_INIT_BOOLEAN
SECTION_VAR_SLOW_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_INIT_8)
#undef CanTp_START_SEC_VAR_SLOW_INIT_8
SECTION_VAR_SLOW_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_INIT_16)
#undef CanTp_START_SEC_VAR_SLOW_INIT_16
SECTION_VAR_SLOW_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_INIT_32)
#undef CanTp_START_SEC_VAR_SLOW_INIT_32
SECTION_VAR_SLOW_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_SLOW_INIT_UNSPECIFIED
SECTION_VAR_SLOW_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_CLEARED_BOOLEAN)
#undef CanTp_START_SEC_VAR_SLOW_CLEARED_BOOLEAN
SECTION_VAR_SLOW_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_CLEARED_8)
#undef CanTp_START_SEC_VAR_SLOW_CLEARED_8
SECTION_VAR_SLOW_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_CLEARED_16)
#undef CanTp_START_SEC_VAR_SLOW_CLEARED_16
SECTION_VAR_SLOW_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_CLEARED_32)
#undef CanTp_START_SEC_VAR_SLOW_CLEARED_32
SECTION_VAR_SLOW_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_CLEARED_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_SLOW_CLEARED_UNSPECIFIED
SECTION_VAR_SLOW_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_BOOLEAN)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_BOOLEAN
SECTION_VAR_SLOW_POWER_ON_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_8)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_8
SECTION_VAR_SLOW_POWER_ON_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_16)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_16
SECTION_VAR_SLOW_POWER_ON_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_32)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_32
SECTION_VAR_SLOW_POWER_ON_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED
SECTION_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN
SECTION_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_8)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_8
SECTION_VAR_SLOW_POWER_ON_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_16)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_16
SECTION_VAR_SLOW_POWER_ON_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_32)
#undef CanTp_START_SEC_VAR_SLOW_POWER_ON_CLEARED_32
SECTION_VAR_SLOW_POWER_ON_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED)
#undef CanTp_START_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
SECTION_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CONST_BOOLEAN)
#undef CanTp_START_SEC_CONST_BOOLEAN
SECTION_CONST_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CONST_8)
#undef CanTp_START_SEC_CONST_8
SECTION_CONST_8
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CONST_16)
#undef CanTp_START_SEC_CONST_16
SECTION_CONST_16
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CONST_32)
#undef CanTp_START_SEC_CONST_32
SECTION_CONST_32
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CONST_UNSPECIFIED)
#undef CanTp_START_SEC_CONST_UNSPECIFIED
SECTION_CONST_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CODE_FAST)
#undef CanTp_START_SEC_CODE_FAST
SECTION_CODE_FAST
#undef MEMMAP_ERROR

#elif defined(CanTp_START_SEC_CODE_SLOW)
#undef CanTp_START_SEC_CODE_SLOW
SECTION_CODE_SLOW
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_NO_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_FAST_NO_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_NO_INIT_8)
#undef CanTp_STOP_SEC_VAR_FAST_NO_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_NO_INIT_16)
#undef CanTp_STOP_SEC_VAR_FAST_NO_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_NO_INIT_32)
#undef CanTp_STOP_SEC_VAR_FAST_NO_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_NO_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_NO_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_FAST_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_INIT_8)
#undef CanTp_STOP_SEC_VAR_FAST_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_INIT_16)
#undef CanTp_STOP_SEC_VAR_FAST_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_INIT_32)
#undef CanTp_STOP_SEC_VAR_FAST_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_CLEARED_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_FAST_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_CLEARED_8)
#undef CanTp_STOP_SEC_VAR_FAST_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_CLEARED_16)
#undef CanTp_STOP_SEC_VAR_FAST_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_CLEARED_32)
#undef CanTp_STOP_SEC_VAR_FAST_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_CLEARED_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_8)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_16)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_32)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_8)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_16)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_32)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_NO_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_SLOW_NO_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_NO_INIT_8)
#undef CanTp_STOP_SEC_VAR_SLOW_NO_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_NO_INIT_16)
#undef CanTp_STOP_SEC_VAR_SLOW_NO_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_NO_INIT_32)
#undef CanTp_STOP_SEC_VAR_SLOW_NO_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_NO_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_SLOW_NO_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_SLOW_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_INIT_8)
#undef CanTp_STOP_SEC_VAR_SLOW_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_INIT_16)
#undef CanTp_STOP_SEC_VAR_SLOW_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_INIT_32)
#undef CanTp_STOP_SEC_VAR_SLOW_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_SLOW_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_CLEARED_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_SLOW_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_CLEARED_8)
#undef CanTp_STOP_SEC_VAR_SLOW_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_CLEARED_16)
#undef CanTp_STOP_SEC_VAR_SLOW_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_CLEARED_32)
#undef CanTp_STOP_SEC_VAR_SLOW_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_CLEARED_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_SLOW_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_8)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_16)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_32)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_INIT_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_8)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_16)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_32)
#undef CanTp_STOP_SEC_VAR_SLOW_POWER_ON_CLEARED_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED)
#undef CanTp_STOP_SEC_VAR_FAST_POWER_ON_CLEARED_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CONST_BOOLEAN)
#undef CanTp_STOP_SEC_CONST_BOOLEAN
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CONST_8)
#undef CanTp_STOP_SEC_CONST_8
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CONST_16)
#undef CanTp_STOP_SEC_CONST_16
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CONST_32)
#undef CanTp_STOP_SEC_CONST_32
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CONST_UNSPECIFIED)
#undef CanTp_STOP_SEC_CONST_UNSPECIFIED
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CODE_FAST)
#undef CanTp_STOP_SEC_CODE_FAST
#undef MEMMAP_ERROR

#elif defined(CanTp_STOP_SEC_CODE_SLOW)
#undef CanTp_STOP_SEC_CODE_SLOW
#undef MEMMAP_ERROR

#else

#error undefined memory section used.

#endif /* #if defined(CanTp_START_SEC_VAR_FAST_NO_INIT_BOOLEAN) */

#endif /* #ifdef __arm__ */
