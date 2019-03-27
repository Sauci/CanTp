Feature: minimum separation time (STmin) timeout

  @fixture.can_tp
  Scenario: When sending a long message (segmented), with a minimum separation time of 0, there is no wait time between
  the transmission of two consecutive frames.
    Given the static configuration of the CanTp module is valid
    And the CanTp module is initialized
    And the CanTp_MainFunction is called cyclically
    And the identifier of the transmission PDU is valid
    And a PDU info structure containing a long message
    When we call CanTp_Transmit
