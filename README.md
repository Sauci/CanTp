# implementation
the internal state of all **N-SDU** are modified (read/write) in functions ```CanTp_RxIndication```, 
```CanTp_TxConfirmation``` and ```CanTp_Transmit```. 
all timing values are in microseconds (μs), as the lower minimum separation time (**STmin**) 
parameter value is 100 [μs]

# scheduling frequency
the internal state machine the ```CanTp_MainFunction``` function is called cyclically. 
