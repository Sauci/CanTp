Feature: CanTp_GetVersion API

  @fixture.can_tp
  Scenario: When requesting the version information of the CanTp module, the pVersionInfo parameter vendorID = 0,
  moduleID = 14, sw_major_version = 0, sw_minor_version = 1 and sw_major_version = 0.
    Given pVersionInfo parameter is a valid pointer to a Std_VersionInfoType structure
    When we call CanTp_GetVersionInfo
    Then pVersionInfo.vendorID is equal to 0
    And pVersionInfo.moduleID is equal to 14
    And pVersionInfo.sw_major_version is equal to 0
    And pVersionInfo.sw_minor_version is equal to 1
    And pVersionInfo.sw_patch_version is equal to 0
