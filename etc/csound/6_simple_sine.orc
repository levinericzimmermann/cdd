0dbfs=1

instr 1
    ; initialization
    iduration = p3
    ifrequency = p4

    ; oscillator
    asig poscil3 1, ifrequency
    
    ; volume envelope
    istartAndEndPercentage random 5, 20
    istartAndEnd = iduration * (istartAndEndPercentage / 100)
    if (istartAndEnd >= 10) then
        istartAndEnd = 10
    endif
    icenter = p3 - (istartAndEnd * 2)
    kenv linseg 0, istartAndEnd, 1, icenter, 1, istartAndEnd, 0
    aSineWithEnvelope = asig * kenv

    ; output
    out aSineWithEnvelope
endin

