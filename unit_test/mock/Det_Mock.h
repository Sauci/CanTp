/**
 * @file Det_Mock.h
 * @author Guillaume Sottas
 * @date 11/12/2018
 */

#ifndef DET_MOCK_H
#define DET_MOCK_H

#include <gmock/gmock.h>

#include "Det.h"

class Det_Interface
{
public:

    virtual Std_ReturnType Det_ReportError(uint16, uint8, uint8, uint8) = 0;

    virtual Std_ReturnType Det_ReportRuntimeError(uint16, uint8, uint8, uint8) = 0;
};

class Det_Mock : public Det_Interface
{
private:

    static Det_Mock *singleton;

public:

    static Det_Mock &instance()
    {
        if (singleton == nullptr)
        {
            singleton = new Det_Mock();
        }
        return *singleton;
    }

    static void clear()
    {
        if (singleton != nullptr)
        {
            delete singleton;
            singleton = nullptr;
        }
    }

    MOCK_METHOD4(Det_ReportError, Std_ReturnType(uint16, uint8, uint8, uint8));

    MOCK_METHOD4(Det_ReportRuntimeError, Std_ReturnType(uint16, uint8, uint8, uint8));
};

#endif /* #ifndef DET_MOCK_H */
