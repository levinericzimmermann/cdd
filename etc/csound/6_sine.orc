0dbfs=1

instr 1
    ; initialization
    iduration = p3
    ifrequency = p4
    ivolume = p5
    ipreviousFrequency = p6

    ; pitch envelope
    kFrequencyEnv linseg ipreviousFrequency, iduration * 0.4, ifrequency

    ; oscillator
    asig poscil3 ivolume, kFrequencyEnv
    
    ; volume envelope
    istartAndEndPercentage random 5, 20
    istartAndEnd = iduration * (istartAndEndPercentage / 100)
    if (istartAndEnd >= 10) then
        istartAndEnd = 10
    endif
    icenter = p3 - (istartAndEnd * 2)
    kenv linseg 0, istartAndEnd, 1, icenter, 1, istartAndEnd, 0
    aSineWithEnvelope = asig * kenv

    ; additional attacks
    aNoise noise 1, 0.5
    iBandpassSize random 10, 50
    aFilteredNoise resonx aNoise, ifrequency, iBandpassSize, 2
    aBalancedFilteredNoise balance aFilteredNoise, aNoise
    kNoiseEnvelope linseg 0, 0.004, 1, 0.015, 0.1, 0.05, 0
    aAttack = aBalancedFilteredNoise * kNoiseEnvelope * ivolume

    ; output
    out aSineWithEnvelope + aAttack
endin

