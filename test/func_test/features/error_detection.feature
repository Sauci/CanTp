Feature: Error detection

  @fixture.can_tp
  Scenario: SWS_CanTp_00260: If development error detection is enabled the function CanTp_CancelReceive shall check the
  validity of RxPduId parameter. If the parameter value is invalid, the CanTp_CancelReceive function shall raise the
  development error CANTP_E_PARAM_ID and return E_NOT_OK (see SWS_CanTp_00294).
    Given DET is enabled
    And the static configuration of the CanTp module is valid
    And the CanTp module is initialized
    And the identifier of the reception PDU is invalid
    When we call CanTp_CancelReceive
    Then the Det_ReportError function is called
    And errorId parameter is equal to CANTP_E_PARAM_ID

  @fixture.can_tp
  Scenario: SWS_CanTp_00260: If the parameter value indicates a cancel reception request for an N-SDU that it is not on
  reception process the CanTp module shall report the runtime error code CANTP_E_OPER_NOT_SUPPORTED to the Default Error
  Tracer and the service shall return E_NOT_OK.
    Given DET is enabled
    And the static configuration of the CanTp module is valid
    And the CanTp module is initialized
    And the identifier of the reception PDU is valid
    When we call CanTp_CancelReceive
    Then Det_ReportRuntimeError is called
    And errorId parameter is equal to CANTP_E_OPER_NOT_SUPPORTED
    And the return value is E_NOT_OK

  @fixture.can_tp
  Scenario: SWS_CanTp_00319: If DET is enabled the function CanTp_GetVersionInfo shall rise CANTP_E_PARAM_POINTER error
  if the argument is a NULL pointer and return without any action.
    Given DET is enabled
    And versionInfo parameter is a NULL pointer
    When we call CanTp_GetVersion
    Then the Det_ReportError function is called
    And errorId parameter is equal to CANTP_E_PARAM_POINTER
