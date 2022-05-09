0dbfs=1
instr 1
    asig poscil 1, 200
    istartAndEnd = p3 * 0.45
    if (istartAndEnd >= 10) then
        istartAndEnd = 10
    endif
    icenter = p3 - (istartAndEnd * 2)
    kenv expseg p4, istartAndEnd, p5, icenter, p5, istartAndEnd, p6
    out asig * kenv
endin

