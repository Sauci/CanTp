Feature: data transmission

  @fixture.can_tp
  Scenario: if we send a large block of data in standard addressing format (segmented transmission) using the
  CanTp_Transmit API and reconstructing it on the CanIf Transmit API call, the input (SduDataPtr field of pPduInfo
  parameter of CanTp_Transmit API) is equal to output (SduDataPtr field of pPduInfo parameter of CanIf_Transmit API)
  plus PCI.
    Given an initialized instance of CanTp module with a single tx N-SDU
    When we call CanTp_Transmit for a large block of tx data
    And we perform the transmission process correctly
    When we assemble the pPduInfo.SduDataPtr of CanIf_Transmit parameter
