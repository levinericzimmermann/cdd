0dbfs=1
instr 1
    asig phasor p4
    itremoloFreq random 1, 50
    atremolo poscil 0.5, itremoloFreq / 100
    afiltered lowpass2 asig, p4 * 3, 20
    istart = 4
    kenv linseg 0, istart, 1, p3 - (istart * 2), 1, istart, 0
    out afiltered * kenv * p5 * 0.25 * ((((atremolo + 1) / 2) * 0.5) + 0.5)
endin
