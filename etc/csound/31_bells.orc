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

    iFileDuration filelen iSamplePath

    iChannelCount = 5

    iPanningStartArray[] init iChannelCount
    iPanningEndArray[] init iChannelCount

    iPanningStartArray fillarray p8, p9, p10, p11, p12
    iPanningEndArray fillarray p13, p14, p15, p16, p17

    aBellSampleArray[] diskin iSamplePath, iPitchFactor

    aBellSample = aBellSampleArray[iChannelIndex]
    aBellSampleFiltered lowpass2 aBellSample, iFilterFrequency, 60
    aBellSampleBalanced balance aBellSampleFiltered, aBellSample
    aBellSampleAdjusted = aBellSampleBalanced * iAmplitude

    kAmplitudeLinsegArray[] init iChannelCount
    aOutputSignalArray[] init iChannelCount

    iInterpolationDuration random 0.3, 0.7

    kAmplitudeLinsegArray[0] linseg iPanningStartArray[0], iInterpolationDuration, iPanningEndArray[0]
    kAmplitudeLinsegArray[1] linseg iPanningStartArray[1], iInterpolationDuration, iPanningEndArray[1]
    kAmplitudeLinsegArray[2] linseg iPanningStartArray[2], iInterpolationDuration, iPanningEndArray[2]
    kAmplitudeLinsegArray[3] linseg iPanningStartArray[3], iInterpolationDuration, iPanningEndArray[3]
    kAmplitudeLinsegArray[4] linseg iPanningStartArray[4], iInterpolationDuration, iPanningEndArray[4]

    aOutputSignalArray[0] = kAmplitudeLinsegArray[0] * aBellSampleAdjusted
    aOutputSignalArray[1] = kAmplitudeLinsegArray[1] * aBellSampleAdjusted
    aOutputSignalArray[2] = kAmplitudeLinsegArray[2] * aBellSampleAdjusted
    aOutputSignalArray[3] = kAmplitudeLinsegArray[3] * aBellSampleAdjusted
    aOutputSignalArray[4] = kAmplitudeLinsegArray[4] * aBellSampleAdjusted

    aConvoledSignalArray00 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray01 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-01.cv"
    aConvoledSignalArray03 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-01.cv"

    aConvoledSignalArray10 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray11 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-02.cv"
    aConvoledSignalArray12 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-02.cv"

    aConvoledSignalArray21 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray22 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-03.cv"
    aConvoledSignalArray23 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-03.cv"

    aConvoledSignalArray30 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray32 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray33 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-04.cv"

    aConvoledSignalArray40 convolve aOutputSignalArray[0], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray41 convolve aOutputSignalArray[1], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray42 convolve aOutputSignalArray[2], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray43 convolve aOutputSignalArray[3], "etc/samples/impulse_responses/hm_williams-04.cv"
    aConvoledSignalArray44 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-04.cv"

    aConvoledSignalArray54 convolve aOutputSignalArray[4], "etc/samples/impulse_responses/hm_williams-05.cv"

    aConvoledSignalArray0 = (aConvoledSignalArray00 * 2) + aConvoledSignalArray01 + aConvoledSignalArray03
    aConvoledSignalArray1 = aConvoledSignalArray10 + (aConvoledSignalArray11 * 2) + aConvoledSignalArray12
    aConvoledSignalArray2 = aConvoledSignalArray21 + (aConvoledSignalArray22 * 2) + aConvoledSignalArray23
    aConvoledSignalArray3 = aConvoledSignalArray30 + aConvoledSignalArray32 + (aConvoledSignalArray33 * 2)
    aConvoledSignalArray4 = (aConvoledSignalArray44 * 2) + (aConvoledSignalArray54 * 0.25)

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
