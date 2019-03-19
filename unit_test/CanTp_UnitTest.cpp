/**
 * @file CanTp_UnitTest.h
 * @author Guillaume Sottas
 * @date 11/12/2018
 */

#include <gtest/gtest.h>

#include "CanTp.h"
#include "CanTp_Cbk.h"
#include "CanTp_Cfg.h"
#include "ComStack_Types.h"

#include "CanIf_Mock.h"
#include "Det_Mock.h"
#include "PduR_Mock.h"

using ::testing::_;
using ::testing::DoAll;
using ::testing::InSequence;
using ::testing::InvokeWithoutArgs;
using ::testing::NiceMock;
using ::testing::Return;
using ::testing::SaveArgPointee;
using ::testing::SetArgPointee;
using ::testing::Sequence;

ACTION_P(Increment, v)
{
    auto p_v = v;
    (*p_v)++;
    return *p_v;
}

MATCHER_P3(PduInfoTypeMatcher, SduDataPtr, MetaDataPtr, SduLength, "")
{
    bool tmp_return = false;

    if ((arg->SduLength == SduLength))
    {
        tmp_return = true;

        for (uint32 i = 0x00u; i < SduLength; i++)
        {
            if (arg->SduDataPtr[i] != SduDataPtr[i])
            {
                tmp_return = false;
                *result_listener << "DATA value at index " << i << " doesn't match (expected ";
                *result_listener << std::hex << (uint32)SduDataPtr[i] << ", ";
                *result_listener << "actual " << std::hex << (uint32)arg->SduDataPtr[i] << ")";
                break;
            }
        }
    }
    else
    {
        *result_listener << "SDU length value doesn't match (expected " << SduLength << ", ";
        *result_listener << "actual " << arg->SduLength << ")";
    }

    if (tmp_return)
    {
        *result_listener << "PASS";
    }
    return tmp_return;
}

class CanTpTest : public testing::Test
{
public:

    CanIf_Mock *canif_;
    Det_Mock *det_;
    PduR_Mock *pdur_;

protected:

    void SetUp() override
    {
        canif_ = &CanIf_Mock::instance();
        det_ = &Det_Mock::instance();
        pdur_ = &PduR_Mock::instance();
    }

    void TearDown() override
    {
        canif_->clear();
        det_->clear();
        pdur_->clear();
    }
};

TEST_F(CanTpTest,
       cantp_init_calls_det_with_cantp_e_init_failed_if_channel_count_value_in_static_configuration_does_not_correspond_to_defined_value)
{
    CanTp_ConfigType config[] = {{10, 0, nullptr, 0xFFu}};

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, 0, CANTP_INIT_API_ID, CANTP_E_INIT_FAILED))
        .Times(1);

    ASSERT_EQ(CANTP_NUM_OF_CHANNEL, 1);

    CanTp_Init(&config[0]);
}

TEST_F(CanTpTest,
       cantp_init_calls_det_with_cantp_e_init_failed_if_number_of_n_sdus_in_static_configuration_is_greater_than_defined_value)
{
    CanTp_RxNSduType rx_n_sdu_config =
        {
            0,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            CANTP_EXTENDED,
            CANTP_ON,
            CANTP_PHYSICAL
        };

    CanTp_TxNSduType tx_n_sdu_config =
        {
            1,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            TRUE,
            CANTP_STANDARD,
            CANTP_ON,
            CANTP_PHYSICAL,
            0
        };

    CanTp_ChannelType channel_config[] = {
        {nullptr,          0, nullptr,          0},
        {&rx_n_sdu_config, 1, &tx_n_sdu_config, 1},
        {nullptr,          1, nullptr,          2},
        {nullptr,          2, nullptr,          1},
        {nullptr,          2, nullptr,          2},
    };

    CanTp_ConfigType config = {10, 1, nullptr, 0xFFu};

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, 0, CANTP_INIT_API_ID, CANTP_E_INIT_FAILED))
        .Times(3);

    ASSERT_EQ(CANTP_MAX_NUM_OF_N_SDU, 2);

    for (int idx = 0x00u; idx < (sizeof(channel_config) / sizeof(channel_config[0])); idx++)
    {
        config.pChannel = &channel_config[idx];
        CanTp_Init(&config);
    }
}

TEST_F(CanTpTest,
       cantp_init_calls_det_with_cantp_e_init_failed_if_n_sdu_value_is_greater_than_allowed_range_for_channel)
{
    CanTp_RxNSduType rx_n_sdu_config =
        {
            2,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            CANTP_EXTENDED,
            CANTP_ON,
            CANTP_PHYSICAL
        };

    CanTp_TxNSduType tx_n_sdu_config =
        {
            2,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            TRUE,
            CANTP_STANDARD,
            CANTP_ON,
            CANTP_PHYSICAL,
            0
        };

    CanTp_ChannelType channel_config[] = {
        {&rx_n_sdu_config, 1, nullptr,          0},
        {nullptr,          0, &tx_n_sdu_config, 1}
    };

    CanTp_ConfigType config = {10, 1, nullptr, 0xFFu};

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, 0, CANTP_INIT_API_ID, CANTP_E_INIT_FAILED))
        .Times(2);

    for (int idx = 0x00u; idx < (sizeof(channel_config) / sizeof(channel_config[0])); idx++)
    {
        config.pChannel = &channel_config[idx];
        CanTp_Init(&config);
    }
}

TEST_F(CanTpTest,
       cantp_init_calls_det_with_cantp_e_init_failed_if_n_sdu_identifier_is_defined_twice_in_static_configuration)
{
    CanTp_RxNSduType rx_n_sdu =
        {
            0,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            CANTP_EXTENDED,
            CANTP_ON,
            CANTP_PHYSICAL
        };

    CanTp_TxNSduType tx_n_sdu =
        {
            0,
            nullptr,
            nullptr,
            nullptr,
            0,
            0,
            0,
            TRUE,
            CANTP_STANDARD,
            CANTP_ON,
            CANTP_PHYSICAL,
            0
        };

    CanTp_RxNSduType rx_n_sdu_config[] = {rx_n_sdu, rx_n_sdu};
    CanTp_TxNSduType tx_n_sdu_config[] = {tx_n_sdu, tx_n_sdu};

    CanTp_ChannelType channel_config[] = {
        {&rx_n_sdu_config[0], 1, &tx_n_sdu_config[0], 1},
        {&rx_n_sdu_config[0], 1, &tx_n_sdu_config[0], 1},
        {&rx_n_sdu_config[0], 2, nullptr,             0},
        {nullptr,             0, &tx_n_sdu_config[0], 2},
    };

    CanTp_ConfigType config = {10, 1, nullptr, 0xFFu};

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, 0, CANTP_INIT_API_ID, CANTP_E_INIT_FAILED))
        .Times(4);

    for (int idx = 0x00u; idx < (sizeof(channel_config) / sizeof(channel_config[0])); idx++)
    {
        config.pChannel = &channel_config[idx];
        CanTp_Init(&config);
    }
}

TEST_F(CanTpTest,
       the_cantp_module_waits_stmin_time_according_to_iso15765_before_sending_next_consecutive_frame)
{
    //    EXPECT_CALL(*pdur_, PduR_CanTpTxConfirmation(_, _)).WillRepeatedly(Return());
    //    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _)).WillRepeatedly(Return(BUFREQ_OK));

    const uint32 n_as = 100000u;
    const uint32 main_function_period = 1;
    const uint32 user_data_size = 20; /* FF, and 2 CF */

    uint8 user_data[user_data_size];
    PduInfoType user_pdu = {&user_data[0], nullptr, 0};

    uint8 fc0[] = {0x03u << 0x04u,
                   0xFF,
                   0,
                   CANTP_PADDING_BYTE,
                   CANTP_PADDING_BYTE,
                   CANTP_PADDING_BYTE,
                   CANTP_PADDING_BYTE,
                   CANTP_PADDING_BYTE};
    PduInfoType fc_pdu = {(uint8 *)&fc0[0], nullptr, 8};

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        n_as,
        100,
        100,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {main_function_period, 1, &channel_config[0], 0};

    uint32 frame_sent;

    EXPECT_CALL(*canif_, CanIf_Transmit(_, _)).WillRepeatedly(Increment(&frame_sent));

    user_pdu.SduLength = user_data_size;

    uint8 st_min;

    for (st_min = 0; st_min <= 0x7Fu; st_min++)
    {
        frame_sent = 0;
        fc0[2] = st_min;
        CanTp_Init(&config);
        CanTp_Transmit(0, &user_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
        CanTp_RxIndication(0, &fc_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);


        /* stmin is in [ms], and the main function period is in us. */
        for (int i = 0; i < (st_min * 1000); i++)
        {
            CanTp_MainFunction();
        }

        ASSERT_EQ(frame_sent, 2);

        CanTp_MainFunction();

        ASSERT_EQ(frame_sent, 3);
    }

    for (st_min = 0xF1u; st_min <= 0xF9u; st_min++)
    {
        frame_sent = 0;
        fc0[2] = st_min;
        CanTp_Init(&config);
        CanTp_Transmit(0, &user_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
        CanTp_RxIndication(0, &fc_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);

        for (int i = 0; i < ((st_min & 0x0Fu) * 100); i++)
        {
            CanTp_MainFunction();
        }

        ASSERT_EQ(frame_sent, 2);

        CanTp_MainFunction();

        ASSERT_EQ(frame_sent, 3);
    }

    st_min = 0x80u;

    while (true)
    {
        frame_sent = 0;
        fc0[2] = st_min;
        CanTp_Init(&config);
        CanTp_Transmit(0, &user_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
        CanTp_RxIndication(0, &fc_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);

        for (int i = 0; i < (0x7Fu * 1000); i++)
        {
            CanTp_MainFunction();
        }

        ASSERT_EQ(frame_sent, 2);

        CanTp_MainFunction();

        ASSERT_EQ(frame_sent, 3);

        st_min++;
        if (st_min == 0xF1u)
        {
            st_min = 0xFAu;
        }
        else if (st_min == 0x00u)
        {
            break;
        }
    }
}

TEST_F(CanTpTest, SWS_CanTp_00031)
{
    Std_ReturnType result;
    PduInfoType pdu_info = {nullptr, nullptr, 0};

    InSequence sequence;

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_SHUTDOWN_API_ID, CANTP_E_UNINIT))
        .Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_TRANSMIT_API_ID, CANTP_E_UNINIT))
        .Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_CANCEL_TRANSMIT_API_ID,
                                       CANTP_E_UNINIT)).Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_CANCEL_RECEIVE_API_ID,
                                       CANTP_E_UNINIT)).Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_CHANGE_PARAMETER_API_ID,
                                       CANTP_E_UNINIT)).Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_READ_PARAMETER_API_ID,
                                       CANTP_E_UNINIT)).Times(1);
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, CANTP_MAIN_FUNCTION_API_ID,
                                       CANTP_E_UNINIT)).Times(1);

    CanTp_State = CANTP_OFF;

    CanTp_Shutdown();

    result = CanTp_Transmit(0x00u, &pdu_info);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelTransmit(0x00u);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelReceive(0x00u);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_ChangeParameter(0x00u, TPParameterType::TP_STMIN, 0x00u);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_ReadParameter(0x00u, TPParameterType::TP_STMIN, nullptr);
    ASSERT_EQ(result, E_NOT_OK);

    CanTp_MainFunction();
}

TEST_F(CanTpTest, SWS_CanTp_00090)
{
    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _)).WillRepeatedly(Return(BUFREQ_OK));
    EXPECT_CALL(*canif_, CanIf_Transmit(_, _)).WillRepeatedly(Return(E_OK));

    EXPECT_CALL(*pdur_, PduR_CanTpTxConfirmation(0, E_OK)).Times(1);

    const uint32 data_size = 50;

    uint8 user_data[data_size];

    for (uint32 i = 0x00u; i < data_size; i++)
    {
        user_data[i] = (uint8)i;
    }

    PduInfoType user_pdu = {&user_data[0], nullptr, data_size};

    const uint8 fc0[] = {(3u << 4u) | 0u, // PCIType = FC, FS = CTS,
                         3, // BS
                         0, // STmin = 0, meaning no waiting time.
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE};

    PduInfoType fc_pdu = {(uint8 *)&fc0[0], nullptr, 8};

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        100,
        100,
        100,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {10, 1, &channel_config[0], 0};

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    for (int i = 0x00u; i < 2; i++)
    {
        CanTp_RxIndication(0, &fc_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
        CanTp_MainFunction();
        CanTp_TxConfirmation(0, E_OK);
    }

    CanTp_RxIndication(0, &fc_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_MainFunction();
}

TEST_F(CanTpTest, SWS_CanTp_00170)
{
    CanTp_Init(&CanTp_Config[0x00u]);

    ASSERT_EQ(CanTp_State, CANTP_ON);
}

TEST_F(CanTpTest, SWS_CanTp_00229)
{
    uint32 n_as = 100;
    uint32 n_bs = 200;
    uint32 n_cs = 300;
    uint8 user_data[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    PduInfoType user_pdu = {&user_data[0], nullptr, 0};

    const uint8 fc0[] = {0x03u << 0x04u,
                         0,
                         0,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE};
    PduInfoType fc_pdu = {(uint8 *)&fc0[0], nullptr, 8};

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        n_as,
        n_bs,
        n_cs,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {10, 1, &channel_config[0], 0};

    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _)).WillRepeatedly(Return(BUFREQ_OK));
    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID, _, _, CANTP_E_TX_COM)).Times(4);

    user_pdu.SduLength = 1;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);

    for (uint32 idx = 0x00u; idx < (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);

    for (uint32 idx = 0x00u; idx <= (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    user_pdu.SduLength = 9;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_MainFunction();
    CanTp_RxIndication(0, &fc_pdu);

    for (uint32 idx = 0x00u; idx < (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_MainFunction();
    CanTp_RxIndication(0, &fc_pdu);

    for (uint32 idx = 0x00u; idx <= (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    user_pdu.SduLength = 9;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    for (uint32 idx = 0x00u; idx < (n_bs / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    for (uint32 idx = 0x00u; idx <= (n_bs / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    InSequence cs;

    const uint32 num_of_fc = 3;
    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _))
        .Times(1).WillRepeatedly(Return(BUFREQ_OK));
    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _))
        .Times((n_cs / CanTp_Config->mainFunctionPeriod) * num_of_fc)
        .WillRepeatedly(Return(BUFREQ_E_BUSY));
    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _))
        .Times(1).WillRepeatedly(Return(BUFREQ_OK));
    EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(_, _, _, _))
        .Times((n_cs / CanTp_Config->mainFunctionPeriod) + 1)
        .WillRepeatedly(Return(BUFREQ_E_BUSY));

    user_pdu.SduLength = 9;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    uint32 fc_idx;

    for (fc_idx = 0x00u; fc_idx < num_of_fc; fc_idx++)
    {
        CanTp_RxIndication(0, &fc_pdu);

        for (uint32 idx = 0; idx < (n_cs / CanTp_Config->mainFunctionPeriod); idx++)
        {
            CanTp_MainFunction();
        }
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_RxIndication(0, &fc_pdu);

    for (uint32 idx = 0; idx <= (n_cs / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }
}

TEST_F(CanTpTest, SWS_CanTp_00253)
{
    /* TODO: run as integration test, as the state value at initialization depends on the memory
     * initialization of ECU.
     */
    //ASSERT_EQ(CanTp_State, CANTP_OFF);
}

TEST_F(CanTpTest, SWS_CanTp_00254)
{
    Std_ReturnType result;

    CanTp_RxNSduType rx_n_sdu = {
        1,
        nullptr,
        nullptr,
        nullptr,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        CANTP_EXTENDED,
        CANTP_ON,
        CANTP_PHYSICAL
    };

    CanTp_TxNSduType tx_n_sdu = {
        0,
        nullptr,
        nullptr,
        nullptr,
        0,
        0,
        0,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_RxNSduType rx_n_sdu_config[] = {rx_n_sdu, rx_n_sdu};
    CanTp_TxNSduType tx_n_sdu_config[] = {tx_n_sdu, tx_n_sdu};

    CanTp_ChannelType channel_config = {
        &rx_n_sdu_config[0], 1, &tx_n_sdu_config[0], 1
    };

    CanTp_ConfigType config = {10, 1, &channel_config, 0xFFu};

    InSequence sequence;

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID,
                                       _,
                                       CANTP_CANCEL_TRANSMIT_API_ID,
                                       CANTP_E_PARAM_ID)).Times(1);

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID,
                                       _,
                                       CANTP_CANCEL_TRANSMIT_API_ID,
                                       CANTP_E_PARAM_ID)).Times(1);

    EXPECT_CALL(*det_, Det_ReportRuntimeError(CANTP_MODULE_ID,
                                              _,
                                              CANTP_CANCEL_TRANSMIT_API_ID,
                                              CANTP_E_OPER_NOT_SUPPORTED)).Times(1);

    CanTp_Init(&config);

    result = CanTp_CancelTransmit(1);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelTransmit(2);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelTransmit(0);
    ASSERT_EQ(result, E_NOT_OK);
}

TEST_F(CanTpTest, SWS_CanTp_00255)
{
    EXPECT_CALL(*pdur_, PduR_CanTpTxConfirmation(0, E_NOT_OK)).Times(1);

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        0,
        0,
        0,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    uint8 user_data[8];
    PduInfoType user_pdu = {&user_data[0], nullptr, 8};

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {10, 1, &channel_config[0], 0};

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();

    CanTp_CancelTransmit(0);
}

TEST_F(CanTpTest, SWS_CanTp_00260)
{
    Std_ReturnType result;

    CanTp_RxNSduType rx_n_sdu = {
        0,
        nullptr,
        nullptr,
        nullptr,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        CANTP_EXTENDED,
        CANTP_ON,
        CANTP_PHYSICAL
    };

    CanTp_TxNSduType tx_n_sdu = {
        1,
        nullptr,
        nullptr,
        nullptr,
        0,
        0,
        0,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_RxNSduType rx_n_sdu_config[] = {rx_n_sdu, rx_n_sdu};
    CanTp_TxNSduType tx_n_sdu_config[] = {tx_n_sdu, tx_n_sdu};

    CanTp_ChannelType channel_config = {
        &rx_n_sdu_config[0], 1, &tx_n_sdu_config[0], 1
    };

    CanTp_ConfigType config = {10, 1, &channel_config, 0xFFu};

    InSequence sequence;

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID,
                                       _,
                                       CANTP_CANCEL_RECEIVE_API_ID,
                                       CANTP_E_PARAM_ID)).Times(1);

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID,
                                       _,
                                       CANTP_CANCEL_RECEIVE_API_ID,
                                       CANTP_E_PARAM_ID)).Times(1);

    EXPECT_CALL(*det_, Det_ReportRuntimeError(CANTP_MODULE_ID,
                                              _,
                                              CANTP_CANCEL_RECEIVE_API_ID,
                                              CANTP_E_OPER_NOT_SUPPORTED)).Times(1);

    CanTp_Init(&config);

    result = CanTp_CancelReceive(1);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelReceive(2);
    ASSERT_EQ(result, E_NOT_OK);

    result = CanTp_CancelReceive(0);
    ASSERT_EQ(result, E_NOT_OK);
}

TEST_F(CanTpTest, SWS_CanTp_00310)
{
    uint32 n_as = 100;
    uint32 n_bs = 200;
    uint32 n_cs = 300;
    uint8 user_data[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    PduInfoType user_pdu = {&user_data[0], nullptr, 0};

    const uint8 fc0[] = {0x03u << 0x04u,
                         0,
                         0,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE,
                         CANTP_PADDING_BYTE};
    PduInfoType fc_pdu = {(uint8 *)&fc0[0], nullptr, 8};

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        n_as,
        n_bs,
        n_cs,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {10, 1, &channel_config[0], 0};

    EXPECT_CALL(*pdur_, PduR_CanTpTxConfirmation(0, E_NOT_OK)).Times(2);

    user_pdu.SduLength = 1;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);

    for (uint32 idx = 0x00u; idx < (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);

    for (uint32 idx = 0x00u; idx <= (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    user_pdu.SduLength = 9;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_RxIndication(0, &fc_pdu);

    for (uint32 idx = 0x00u; idx < (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);
    CanTp_RxIndication(0, &fc_pdu);

    for (uint32 idx = 0x00u; idx <= (n_as / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }
}

TEST_F(CanTpTest, SWS_CanTp_00316)
{
    uint32 n_as = 100;
    uint32 n_bs = 200;
    uint32 n_cs = 300;
    uint8 user_data[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    PduInfoType user_pdu = {&user_data[0], nullptr, 0};

    CanTp_TxNSduType tx_n_sdu_config = {
        0,
        nullptr,
        nullptr,
        nullptr,
        n_as,
        n_bs,
        n_cs,
        TRUE,
        CANTP_STANDARD,
        CANTP_ON,
        CANTP_PHYSICAL,
        0
    };

    CanTp_ChannelType channel_config[] = {nullptr, 0, &tx_n_sdu_config, 1};
    CanTp_ConfigType config = {10, 1, &channel_config[0], 0};

    EXPECT_CALL(*pdur_, PduR_CanTpTxConfirmation(0, E_NOT_OK)).Times(1);

    user_pdu.SduLength = 9;

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    for (uint32 idx = 0x00u; idx < (n_bs / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }

    CanTp_Init(&config);
    CanTp_Transmit(0, &user_pdu);
    CanTp_MainFunction();
    CanTp_TxConfirmation(0, E_OK);

    for (uint32 idx = 0x00u; idx <= (n_bs / CanTp_Config->mainFunctionPeriod); idx++)
    {
        CanTp_MainFunction();
    }
}

TEST_F(CanTpTest, SWS_CanTp_00319)
{
    Std_VersionInfoType versionInfo;

    EXPECT_CALL(*det_, Det_ReportError(CANTP_MODULE_ID,
                                       _,
                                       CANTP_GET_VERSION_INFO_API_ID,
                                       CANTP_E_PARAM_POINTER)).Times(1);

    CanTp_GetVersionInfo(nullptr);
    CanTp_GetVersionInfo(&versionInfo);
}

TEST_F(CanTpTest, SWS_CanTp_00348)
{
    PduIdType pdu_id = 0x01u;
    uint8 up[] = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16};
    PduInfoType user_pdu = {&up[0], nullptr, 0};
    {
        user_pdu.SduLength = 1;
        const uint8 sf[] = {1, /* PCI type = SF, SF_DL = 1 */
                            up[0], 0x55, 0x55, 0x55, 0x55, 0x55, 0x55};
        EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(pdu_id, _, _, _))
            .Times(1)
            .WillOnce(
                DoAll(PduR_SetCopiedTxDataPdu((uint8 *)&up[0], nullptr, 1), Return(BUFREQ_OK)));
        EXPECT_CALL(*canif_, CanIf_Transmit(pdu_id, PduInfoTypeMatcher(&sf[0], nullptr, 8)))
            .Times(1);

        CanTp_Init(&CanTp_Config[0]);

        CanTp_Transmit(pdu_id, &user_pdu);
        CanTp_MainFunction();
    }
    {
        InSequence sequence;

        user_pdu.SduLength = 9;

        const uint8 ff[] = {1 << 4, /* PCI type = FF */
                            9, /* FF_DL = 9 (lower than 0x100u, fits into LSB). */
                            up[0],
                            up[1],
                            up[2],
                            up[3],
                            up[4],
                            up[5]};
        const uint8 fc0[0x08u] = {3 << 4, /* PCI type = FC, FS = CTS */
                                  16, /* BS = 16 */
                                  0, /* STmin = 0 */
                                  0x55u, 0x55u, 0x55u, 0x55u, 0x55u};
        const uint8 cf0[0x08u] = {(2 << 4) | 1, /* PCI type = CF, SN = 1 */
                                  up[6],
                                  up[7],
                                  up[8],
                                  0x55u, 0x55u, 0x55u, 0x55u};

        PduInfoType fc_pdu = {(uint8 *)&fc0[0], nullptr, 8};

        EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(pdu_id, _, _, _)).Times(1).WillOnce(
            DoAll(PduR_SetCopiedTxDataPdu((uint8 *)&up[0], nullptr, 6), Return(BUFREQ_OK)));
        EXPECT_CALL(*canif_, CanIf_Transmit(pdu_id, PduInfoTypeMatcher(ff, nullptr, 8))).Times(1);

        EXPECT_CALL(*pdur_, PduR_CanTpCopyTxData(pdu_id, _, nullptr, _)).WillOnce(
            DoAll(PduR_SetCopiedTxDataPdu((uint8 *)&up[6], nullptr, 3), Return(BUFREQ_OK)));
        EXPECT_CALL(*canif_, CanIf_Transmit(pdu_id, PduInfoTypeMatcher(cf0, nullptr, 8))).Times(1);

        CanTp_Init(&CanTp_Config[0]);

        CanTp_Transmit(pdu_id, &user_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(pdu_id, E_OK);
        CanTp_MainFunction();
        CanTp_RxIndication(pdu_id, &fc_pdu);
        CanTp_MainFunction();
        CanTp_TxConfirmation(pdu_id, E_OK);
        CanTp_MainFunction();
    }
}

int main(int argc, char **argv)
{
    ::testing::InitGoogleMock(&argc, argv);

    int result = RUN_ALL_TESTS();
    return result;
}
