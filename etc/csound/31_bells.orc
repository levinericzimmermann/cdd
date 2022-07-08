0dbfs = 1
nchnls = 5
sr = 48000

instr 1
    iDuration = p3
    iSamplePath = p4
    iPitchFactor = p5
    iAmplitude = p6
    iChannelIndex = p7
    iFilterFrequency = p18
    iConvolutionReverbMix = p19

    iChannelCount = 5

    iPanningStartArray[] init iChannelCount
    iPanningEndArray[] init iChannelCount

    iPanningStartArray fillarray p8, p9, p10, p11, p12
    iPanningEndArray fillarray p13, p14, p15, p16, p17

    aBellSampleArray[] diskin iSamplePath, iPitchFactor

    aBellSample = aBellSampleArray[iChannelIndex]
    aBellSampleFiltered lowpass2 aBellSample, iFilterFrequency, 100
    aBellSampleBalanced balance aBellSampleFiltered, aBellSample
    aBellSampleAdjusted = aBellSampleFiltered * iAmplitude

    kAmplitudeLinsegArray[] init iChannelCount
    aOutputSignalArray[] init iChannelCount

    kAmplitudeLinsegArray[0] linseg iPanningStartArray[0], iDuration, iPanningEndArray[0]
    kAmplitudeLinsegArray[1] linseg iPanningStartArray[1], iDuration, iPanningEndArray[1]
    kAmplitudeLinsegArray[2] linseg iPanningStartArray[2], iDuration, iPanningEndArray[2]
    kAmplitudeLinsegArray[3] linseg iPanningStartArray[3], iDuration, iPanningEndArray[3]
    kAmplitudeLinsegArray[4] linseg iPanningStartArray[4], iDuration, iPanningEndArray[4]

    kCount = 0

    until kCount == iChannelCount do
        aOutputSignalArray[kCount] = kAmplitudeLinsegArray[kCount] * aBellSampleAdjusted
        kCount = kCount + 1
    od


    aConvoledSignalArray00 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray01 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray02 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray03 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray04 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-01.cv"

    aConvoledSignalArray10 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray11 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray12 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray13 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray14 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-02.cv"

    aConvoledSignalArray20 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray21 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray22 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray23 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray24 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-03.cv"

    aConvoledSignalArray30 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray31 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray32 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray33 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray34 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-04.cv"

    aConvoledSignalArray40 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray41 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray42 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray43 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray44 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-04.cv"

    aConvoledSignalArray50 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-05.cv"
    aConvoledSignalArray51 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-05.cv"
    aConvoledSignalArray52 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-05.cv"
    aConvoledSignalArray53 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-05.cv"
    aConvoledSignalArray54 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-05.cv"

    aConvoledSignalArray0 = (aConvoledSignalArray00 * 2) + aConvoledSignalArray01 + aConvoledSignalArray02 + aConvoledSignalArray03 + aConvoledSignalArray04 + aConvoledSignalArray50
    aConvoledSignalArray1 = aConvoledSignalArray10 + (aConvoledSignalArray11 * 2) + aConvoledSignalArray12 + aConvoledSignalArray13 + aConvoledSignalArray14 + aConvoledSignalArray51
    aConvoledSignalArray2 = aConvoledSignalArray20 + aConvoledSignalArray21 + (aConvoledSignalArray22 * 2) + aConvoledSignalArray23 + aConvoledSignalArray24 + aConvoledSignalArray52
    aConvoledSignalArray3 = aConvoledSignalArray30 + aConvoledSignalArray31 + aConvoledSignalArray32 + (aConvoledSignalArray33 * 2) + aConvoledSignalArray34 + aConvoledSignalArray53
    aConvoledSignalArray4 = aConvoledSignalArray40 + aConvoledSignalArray41 + aConvoledSignalArray42 + aConvoledSignalArray43 + (aConvoledSignalArray44 * 2) + aConvoledSignalArray54

    iMix = iConvolutionReverbMix

    iDelay filelen "etc/samples/impulse_responses/hm_williams.wav"

    print iDelay

    aDryDelayed[] init 5

    aDryDelayed[0] delay (1 - iMix) * aOutputSignalArray[0], iDelay
    aDryDelayed[1] delay (1 - iMix) * aOutputSignalArray[1], iDelay
    aDryDelayed[2] delay (1 - iMix) * aOutputSignalArray[2], iDelay
    aDryDelayed[3] delay (1 - iMix) * aOutputSignalArray[3], iDelay
    aDryDelayed[4] delay (1 - iMix) * aOutputSignalArray[4], iDelay

    aOutput0 = aDryDelayed[0] + (aConvoledSignalArray0 * iMix)
    aOutput1 = aDryDelayed[1] + (aConvoledSignalArray1 * iMix)
    aOutput2 = aDryDelayed[2] + (aConvoledSignalArray2 * iMix)
    aOutput3 = aDryDelayed[3] + (aConvoledSignalArray3 * iMix)
    aOutput4 = aDryDelayed[4] + (aConvoledSignalArray4 * iMix)

    out aOutput0, aOutput1, aOutput2, aOutput3, aOutput4
endin
