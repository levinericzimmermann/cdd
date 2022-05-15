0dbfs=1

instr 1
    iDuration = p3
    iFrequency = p4
    iAmp = p5

    ; bell sample
    iFactor = iFrequency / 440
    aBell diskin2 "etc/samples/bell-a-strike-gentle1.aif", iFactor
    
    ; filter
    aBellWithLowPass lowpass2 aBell, iFrequency * 4, 30

    ; envelope
    kBellEnvelope linseg 0, 0.0001, 1, p3 * 0.9, 1, p3 * 0.1, 0

    ; out aBell * kBellEnvelope * iAmp
    out aBellWithLowPass * kBellEnvelope
endin
