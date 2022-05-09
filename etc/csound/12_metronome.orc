0dbfs=1

instr 1
    iFrequency = p4
    iAmp = p5
    iBandpassSize = p6
    aNoise noise 1, 0.5
    aFilteredNoise resonx aNoise, iFrequency, iBandpassSize, 2
    aBalancedFilteredNoise balance aFilteredNoise, aNoise
    kEnvelope linseg 0, 0.004, 1, 0.015, 0.5, 0.05, 0
    aResult = aBalancedFilteredNoise * kEnvelope * iAmp
    out aResult
endin
