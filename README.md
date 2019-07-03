| branch                                                 | build status                                                                                               |
|:-------------------------------------------------------|:-----------------------------------------------------------------------------------------------------------|
| [master](https://github.com/Sauci/CanTp/tree/master)   | [![Build Status](https://travis-ci.org/Sauci/CanTp.svg?branch=master)](https://travis-ci.org/Sauci/CanTp)  |
| [develop](https://github.com/Sauci/CanTp/tree/develop) | [![Build Status](https://travis-ci.org/Sauci/CanTp.svg?branch=develop)](https://travis-ci.org/Sauci/CanTp) |

### CMake definitions
The following definitions might be set by the user, depending on the needs.

| definition                  | values                           | default                        | description                                                                                                                                                                      |
|:----------------------------|:---------------------------------|:-------------------------------|:---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| ```ENABLE_DET```            | ```ON```/```OFF```               | ```ON```                       | enables/disables development error detections (see AUTOSAR [DET](https://www.autosar.org/fileadmin/user_upload/standards/classic/4-3/AUTOSAR_SWS_DefaultErrorTracer.pdf) module) |
| ```ENABLE_TEST```           | ```ON```/```OFF```               | ```ON```                       | enables/disables tests. if enabled, stubbbed headers are used, and ```CANTP_BUILD_CFFI_INTERFACE``` preprocessor definition is set to ```STD_ON```                               |
| ```ENABLE_SCA```            | ```ON```/```OFF```               | ```OFF```                      | enables/disables generation of targets related to static code analysis (should be disabled if [lint](https://www.gimpel.com) software is not available)                          |
| ```MISRA_C_VERSION```       | ```1998```/```2004```/```2012``` | ```2012```                     | specifies which version of **MISRA** should be used when performing static code analysis (only used if ```ENABLE_SCA``` is set)                                                  |
| ```CANTP_CONFIG_FILEPATH``` | ```-```                          | ```CanTp/config/can_tp.json``` | specifies which json configuration file should be used to generate the auto-generated code                                                                                       |

To use this feature, simply add ```-D<definition>=<value>``` when configuring the build with CMake.
