0dbfs  = 1
nchnls = 3

giSine   ftgen 1, 0, 16384, 10, 1

instr 1
    iDuration = p3
    iFrequency = p4
    iAmp = p5
    iChannel = p6

    ; FM Synth
    iAttack = 0.0001
    iReleaseFactor random 700, 900
    iRelease = iDuration * (iReleaseFactor / 1000)
    iSustain = iDuration - iRelease - iAttack
    kFMEnvelope linseg 0, iAttack, 1, iSustain, 1, iRelease, 0

    kModulationIndex randomi 1, 4, 3
    kFilterFrequencyFactor randomi 2, 3, 2
    iCarrierFactor random 2, 4
    aFM foscili 1, iFrequency, 1, iCarrierFactor, kModulationIndex, 1
    aFMFiltered lowpass2 aFM, iFrequency * kFilterFrequencyFactor, 25
    aFMFilteredAndBalanced balance, aFMFiltered, aFM
    aFMwithEnvelope = aFMFilteredAndBalanced * kFMEnvelope

    ; Lower sine tone
    aSine poscil3 0.2, iFrequency * 0.25
    aSineWithEnvelope = aSine * kFMEnvelope

    ; Attack noise
    iNoiseAttack = 0.00001
    iNoiseRelease = 0.01
    iNoiseSustain = 0.002

    aNoise pinker
    aNoiseWithFilter reson aNoise, iFrequency, 10
    kNoiseEnvelope linseg 0, iNoiseAttack, 1, iNoiseSustain, 1, iNoiseRelease, 0
    aNoiseWithEnvelope = aNoiseWithFilter * kNoiseEnvelope * 0.4

    ; Main signal
    aSignal = (aFMwithEnvelope + aNoiseWithEnvelope + aSineWithEnvelope) * iAmp

    ; Delay lines

    ; Distribute signal to specific channels
    if (iChannel == 0) then
        iLowFactor = 0.2
        outq1 aSignal
    elseif (iChannel == 1) then
        iLowFactor = 0.2
        outq2 aSignal
    elseif (iChannel == 2) then
        iLowFactor = 0.2
        outq3 aSignal
    ; If there is no main channel
    else
        iLowFactor = 0.35
    endif

    aLowSignal = aSignal * iLowFactor

    outs aLowSignal, aLowSignal, aLowSignal
endin
