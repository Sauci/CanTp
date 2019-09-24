| branch                                                 | build status                                                                                               | coverage                                                                                                                         |
|:-------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|
| [master](https://github.com/Sauci/CanTp/tree/master)   | [![Build Status](https://travis-ci.org/Sauci/CanTp.svg?branch=master)](https://travis-ci.org/Sauci/CanTp)  | [![codecov](https://codecov.io/gh/Sauci/CanTp/branch/master/graph/badge.svg)](https://codecov.io/gh/Sauci/CanTp/branch/master)   |
| [develop](https://github.com/Sauci/CanTp/tree/develop) | [![Build Status](https://travis-ci.org/Sauci/CanTp.svg?branch=develop)](https://travis-ci.org/Sauci/CanTp) | [![codecov](https://codecov.io/gh/Sauci/CanTp/branch/develop/graph/badge.svg)](https://codecov.io/gh/Sauci/CanTp/branch/develop) |

# CMake definitions
The following definitions might be set by the user, depending on the needs.

| definition                    | values                           | default                        | description                                                                                                                                                                      |
|:------------------------------|:---------------------------------|:-------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```AUTOSAR_STD_HEADER_PATH``` | ```-```                          | ```CanTp/test/stub/common```   | specifies the directory containing **AUTOSAR** standard headers ComStack_Types.h and Std_Types.h (used when integrating this module in an other project)                         |
| ```CANTP_CONFIG_FILEPATH```   | ```-```                          | ```CanTp/config/can_tp.json``` | specifies which json configuration file should be used to generate the auto-generated code                                                                                       |
| ```CANTP_ENABLE_TEST```       | ```ON```/```OFF```               | ```OFF```                      | enables/disables tests. if enabled, ```CANTP_BUILD_CFFI_INTERFACE``` preprocessor definition is set to ```STD_ON```                                                              |
| ```ENABLE_DET```              | ```ON```/```OFF```               | ```ON```                       | enables/disables development error detections (see AUTOSAR [DET](https://www.autosar.org/fileadmin/user_upload/standards/classic/4-3/AUTOSAR_SWS_DefaultErrorTracer.pdf) module) |
| ```ENABLE_DOC_GEN```          | ```ON```/```OFF```               | ```OFF```                      | enables/disables generation of [Doxygen](http://www.doxygen.nl/) documentation                                                                                                   |
| ```ENABLE_PC_LINT```          | ```ON```/```OFF```               | ```OFF```                      | enables/disables generation of targets related to static code analysis (should be disabled if [PC-Lint](https://www.gimpel.com) software is not available)                       |
| ```MISRA_C_VERSION```         | ```1998```/```2004```/```2012``` | ```2012```                     | specifies which version of **MISRA** should be used when performing static code analysis (only used if ```ENABLE_PC_LINT``` is set)                                              |
| ```OS_GET_TIME_API```         | ```ON```/```OFF```               | ```OFF```                      | indicates whether the OSEK API GetTime is available or not                                                                                                                       |

To use this feature, simply add ```-D<definition>=<value>``` when configuring the build with CMake.

# Notes
Bellow, a few point to consider when using this module:
- This module does not support nested interrupts. In other words, the functions 
```CanTp_RxIndication```, ```CanTp_TxConfirmation``` and ```CanTp_MainFunction``` (if scheduled 
using timer interrupt) should not be able to interrupt each other.

# TODO
- Protect variables used in both synchronous and asynchronous APIs.
