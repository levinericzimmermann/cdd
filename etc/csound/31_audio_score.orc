0dbfs=1
sr=44100
instr 1
    asig diskin p4
    kenv linseg 0, 0.01, 1, p3 - 0.02, 1, 0.01, 0
    out asig * kenv
endin

