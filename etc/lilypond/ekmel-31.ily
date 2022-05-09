﻿%% This file is part of Ekmelily - Notation of microtonal music with LilyPond.
%% Copyright (C) 2013-2021  Thomas Richter <thomas-richter@aon.at>
%%
%% This program is free software: you can redistribute it and/or modify
%% it under the terms of the GNU General Public License as published by
%% the Free Software Foundation, either version 3 of the License, or
%% (at your option) any later version.
%%
%% This program is distributed in the hope that it will be useful,
%% but WITHOUT ANY WARRANTY; without even the implied warranty of
%% MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
%% GNU General Public License at <http://www.gnu.org/licenses/>
%% for more details.
%%
%%
%% File: ekmel-31.ily  -  Include file for the 31-EDO tuning
%% Version: 3.7
%%
%% Note names from the semitone names in LilyPond 2.22
%% Copyright (C) 2010--2020 Valentin Villenave <valentin@villenave.net> et al.
%%
%% Extended with names for 1st, 3rd, 5th degree
%%

\version "2.19.22"


% Tuning table
ekmTuning = #'(
  (-1     0 30/31 60/31 78/31 108/31 138/31 168/31)
  (#x1A . 6/31)
  (#x28 . 12/31)
  (#x36 . 18/31)
  (#x44 . 24/31)
  (#x50 . 30/31))


% Language tables
ekmLanguages = #'(

;; German names by Roland Meier <meier@informatik.th-darmstadt.de>,
;; Bjoern Jacke <bjoern.jacke@gmx.de>
(deutsch . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (h 6 . 0)
  (ces 0 . #x29)
  (cis 0 . #x28)
  (des 1 . #x29)
  (dis 1 . #x28)
  (es 2 . #x29)
  (eis 2 . #x28)
  (fes 3 . #x29)
  (fis 3 . #x28)
  (ges 4 . #x29)
  (gis 4 . #x28)
  (as 5 . #x29)
  (ais 5 . #x28)
  (hes 6 . #x29)
  (his 6 . #x28)
  (ce 0 . #x1B)
  (ci 0 . #x1A)
  (de 1 . #x1B)
  (di 1 . #x1A)
  (eh 2 . #x1B)
  (ei 2 . #x1A)
  (fe 3 . #x1B)
  (fi 3 . #x1A)
  (ge 4 . #x1B)
  (gi 4 . #x1A)
  (ah 5 . #x1B)
  (ai 5 . #x1A)
  (he 6 . #x1B)
  (hi 6 . #x1A)
  (cese 0 . #x37)
  (cisi 0 . #x36)
  (dese 1 . #x37)
  (disi 1 . #x36)
  (ese 2 . #x37)
  (eisi 2 . #x36)
  (fese 3 . #x37)
  (fisi 3 . #x36)
  (gese 4 . #x37)
  (gisi 4 . #x36)
  (ase 5 . #x37)
  (aisi 5 . #x36)
  (hese 6 . #x37)
  (hisi 6 . #x36)
  (ceses 0 . #x45)
  (cisis 0 . #x44)
  (deses 1 . #x45)
  (disis 1 . #x44)
  (eses 2 . #x45)
  (eisis 2 . #x44)
  (feses 3 . #x45)
  (fisis 3 . #x44)
  (geses 4 . #x45)
  (gisis 4 . #x44)
  (ases 5 . #x45)
  (aisis 5 . #x44)
  (heses 6 . #x45)
  (hisis 6 . #x44)
  (cesese 0 . #x51)
  (cisisi 0 . #x50)
  (desese 1 . #x51)
  (disisi 1 . #x50)
  (esese 2 . #x51)
  (eisisi 2 . #x50)
  (fesese 3 . #x51)
  (fisisi 3 . #x50)
  (gesese 4 . #x51)
  (gisisi 4 . #x50)
  (asese 5 . #x51)
  (aisisi 5 . #x50)
  (hesese 6 . #x51)
  (hisisi 6 . #x50)))

;; Dutch names by Han-Wen Nienhuys <hanwen@xs4all.nl>
(nederlands . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)
  (ces 0 . #x29)
  (cis 0 . #x28)
  (des 1 . #x29)
  (dis 1 . #x28)
  (es 2 . #x29)
  (eis 2 . #x28)
  (fes 3 . #x29)
  (fis 3 . #x28)
  (ges 4 . #x29)
  (gis 4 . #x28)
  (as 5 . #x29)
  (ais 5 . #x28)
  (bes 6 . #x29)
  (bis 6 . #x28)
  (ce 0 . #x1B)
  (ci 0 . #x1A)
  (de 1 . #x1B)
  (di 1 . #x1A)
  (eh 2 . #x1B)
  (ei 2 . #x1A)
  (fe 3 . #x1B)
  (fi 3 . #x1A)
  (ge 4 . #x1B)
  (gi 4 . #x1A)
  (ah 5 . #x1B)
  (ai 5 . #x1A)
  (be 6 . #x1B)
  (bi 6 . #x1A)
  (cese 0 . #x37)
  (cisi 0 . #x36)
  (dese 1 . #x37)
  (disi 1 . #x36)
  (ese 2 . #x37)
  (eisi 2 . #x36)
  (fese 3 . #x37)
  (fisi 3 . #x36)
  (gese 4 . #x37)
  (gisi 4 . #x36)
  (ase 5 . #x37)
  (aisi 5 . #x36)
  (bese 6 . #x37)
  (bisi 6 . #x36)
  (ceses 0 . #x45)
  (cisis 0 . #x44)
  (deses 1 . #x45)
  (disis 1 . #x44)
  (eses 2 . #x45)
  (eisis 2 . #x44)
  (feses 3 . #x45)
  (fisis 3 . #x44)
  (geses 4 . #x45)
  (gisis 4 . #x44)
  (ases 5 . #x45)
  (aisis 5 . #x44)
  (beses 6 . #x45)
  (bisis 6 . #x44)
  (cesese 0 . #x51)
  (cisisi 0 . #x50)
  (desese 1 . #x51)
  (disisi 1 . #x50)
  (esese 2 . #x51)
  (eisisi 2 . #x50)
  (fesese 3 . #x51)
  (fisisi 3 . #x50)
  (gesese 4 . #x51)
  (gisisi 4 . #x50)
  (asese 5 . #x51)
  (aisisi 5 . #x50)
  (besese 6 . #x51)
  (bisisi 6 . #x50)))

;; Spanish names by Carlos García Suárez <cgscqmp@terra.es>,
;; Maximiliano G. G. <mxgdvg@yahoo.it>
(espanol . español)
(español . (
  (dobb 0 . #x45)
  (dotcb 0 . #x37)
  (dob 0 . #x29)
  (docb 0 . #x1B)
  (do 0 . 0)
  (docs 0 . #x1A)
  (dos 0 . #x28)
  (dotcs 0 . #x36)
  (doss 0 . #x44)
  (dox 0 . #x44)
  (rebb 1 . #x45)
  (retcb 1 . #x37)
  (reb 1 . #x29)
  (recb 1 . #x1B)
  (re 1 . 0)
  (recs 1 . #x1A)
  (res 1 . #x28)
  (retcs 1 . #x36)
  (ress 1 . #x44)
  (rex 1 . #x44)
  (mibb 2 . #x45)
  (mitcb 2 . #x37)
  (mib 2 . #x29)
  (micb 2 . #x1B)
  (mi 2 . 0)
  (mics 2 . #x1A)
  (mis 2 . #x28)
  (mitcs 2 . #x36)
  (miss 2 . #x44)
  (mix 2 . #x44)
  (fabb 3 . #x45)
  (fatcb 3 . #x37)
  (fab 3 . #x29)
  (facb 3 . #x1B)
  (fa 3 . 0)
  (facs 3 . #x1A)
  (fas 3 . #x28)
  (fatcs 3 . #x36)
  (fass 3 . #x44)
  (fax 3 . #x44)
  (solbb 4 . #x45)
  (soltcb 4 . #x37)
  (solb 4 . #x29)
  (solcb 4 . #x1B)
  (sol 4 . 0)
  (solcs 4 . #x1A)
  (sols 4 . #x28)
  (soltcs 4 . #x36)
  (solss 4 . #x44)
  (solx 4 . #x44)
  (labb 5 . #x45)
  (latcb 5 . #x37)
  (lab 5 . #x29)
  (lacb 5 . #x1B)
  (la 5 . 0)
  (lacs 5 . #x1A)
  (las 5 . #x28)
  (latcs 5 . #x36)
  (lass 5 . #x44)
  (lax 5 . #x44)
  (sibb 6 . #x45)
  (sitcb 6 . #x37)
  (sib 6 . #x29)
  (sicb 6 . #x1B)
  (si 6 . 0)
  (sics 6 . #x1A)
  (sis 6 . #x28)
  (sitcs 6 . #x36)
  (siss 6 . #x44)
  (six 6 . #x44)))

;; French names by Valentin Villenave <valentin@villenave.net>
(français . (
  (dobb 0 . #x45)
  (dobsb 0 . #x37)
  (dob 0 . #x29)
  (dosb 0 . #x1B)
  (do 0 . 0)
  (dosd 0 . #x1A)
  (dod 0 . #x28)
  (dodsd 0 . #x36)
  (dodd 0 . #x44)
  (dox 0 . #x44)
  (rébb 1 . #x45)
  (rébsb 1 . #x37)
  (réb 1 . #x29)
  (résb 1 . #x1B)
  (ré 1 . 0)
  (résd 1 . #x1A)
  (réd 1 . #x28)
  (rédsd 1 . #x36)
  (rédd 1 . #x44)
  (réx 1 . #x44)
  (rebb 1 . #x45)
  (rebsb 1 . #x37)
  (reb 1 . #x29)
  (resb 1 . #x1B)
  (re 1 . 0)
  (resd 1 . #x1A)
  (red 1 . #x28)
  (redsd 1 . #x36)
  (redd 1 . #x44)
  (rex 1 . #x44)
  (mibb 2 . #x45)
  (mibsb 2 . #x37)
  (mib 2 . #x29)
  (misb 2 . #x1B)
  (mi 2 . 0)
  (misd 2 . #x1A)
  (mid 2 . #x28)
  (midsd 2 . #x36)
  (midd 2 . #x44)
  (mix 2 . #x44)
  (fabb 3 . #x45)
  (fabsb 3 . #x37)
  (fab 3 . #x29)
  (fasb 3 . #x1B)
  (fa 3 . 0)
  (fasd 3 . #x1A)
  (fad 3 . #x28)
  (fadsd 3 . #x36)
  (fadd 3 . #x44)
  (fax 3 . #x44)
  (solbb 4 . #x45)
  (solbsb 4 . #x37)
  (solb 4 . #x29)
  (solsb 4 . #x1B)
  (sol 4 . 0)
  (solsd 4 . #x1A)
  (sold 4 . #x28)
  (soldsd 4 . #x36)
  (soldd 4 . #x44)
  (solx 4 . #x44)
  (labb 5 . #x45)
  (labsb 5 . #x37)
  (lab 5 . #x29)
  (lasb 5 . #x1B)
  (la 5 . 0)
  (lasd 5 . #x1A)
  (lad 5 . #x28)
  (ladsd 5 . #x36)
  (ladd 5 . #x44)
  (lax 5 . #x44)
  (sibb 6 . #x45)
  (sibsb 6 . #x37)
  (sib 6 . #x29)
  (sisb 6 . #x1B)
  (si 6 . 0)
  (sisd 6 . #x1A)
  (sid 6 . #x28)
  (sidsd 6 . #x36)
  (sidd 6 . #x44)
  (six 6 . #x44)))

;; Italian names by Paolo Zuliani <zuliap@easynet.it>,
;; Eric Wurbel <wurbel@univ-tln.fr>
(italiano . (
  (dobb 0 . #x45)
  (dobsb 0 . #x37)
  (dob 0 . #x29)
  (dosb 0 . #x1B)
  (do 0 . 0)
  (dosd 0 . #x1A)
  (dod 0 . #x28)
  (dodsd 0 . #x36)
  (dodd 0 . #x44)
  (rebb 1 . #x45)
  (rebsb 1 . #x37)
  (reb 1 . #x29)
  (resb 1 . #x1B)
  (re 1 . 0)
  (resd 1 . #x1A)
  (red 1 . #x28)
  (redsd 1 . #x36)
  (redd 1 . #x44)
  (mibb 2 . #x45)
  (mibsb 2 . #x37)
  (mib 2 . #x29)
  (misb 2 . #x1B)
  (mi 2 . 0)
  (misd 2 . #x1A)
  (mid 2 . #x28)
  (midsd 2 . #x36)
  (midd 2 . #x44)
  (fabb 3 . #x45)
  (fabsb 3 . #x37)
  (fab 3 . #x29)
  (fasb 3 . #x1B)
  (fa 3 . 0)
  (fasd 3 . #x1A)
  (fad 3 . #x28)
  (fadsd 3 . #x36)
  (fadd 3 . #x44)
  (solbb 4 . #x45)
  (solbsb 4 . #x37)
  (solb 4 . #x29)
  (solsb 4 . #x1B)
  (sol 4 . 0)
  (solsd 4 . #x1A)
  (sold 4 . #x28)
  (soldsd 4 . #x36)
  (soldd 4 . #x44)
  (labb 5 . #x45)
  (labsb 5 . #x37)
  (lab 5 . #x29)
  (lasb 5 . #x1B)
  (la 5 . 0)
  (lasd 5 . #x1A)
  (lad 5 . #x28)
  (ladsd 5 . #x36)
  (ladd 5 . #x44)
  (sibb 6 . #x45)
  (sibsb 6 . #x37)
  (sib 6 . #x29)
  (sisb 6 . #x1B)
  (si 6 . 0)
  (sisd 6 . #x1A)
  (sid 6 . #x28)
  (sidsd 6 . #x36)
  (sidd 6 . #x44)))

;; Portuguese names by Pedro Kröger <kroeger@pedrokroeger.net>
(portugues . português)
(português . (
  (dobb 0 . #x45)
  (dobtqt 0 . #x37)
  (dob 0 . #x29)
  (dobqt 0 . #x1B)
  (do 0 . 0)
  (dosqt 0 . #x1A)
  (dos 0 . #x28)
  (dostqt 0 . #x36)
  (doss 0 . #x44)
  (rebb 1 . #x45)
  (rebtqt 1 . #x37)
  (reb 1 . #x29)
  (rebqt 1 . #x1B)
  (re 1 . 0)
  (resqt 1 . #x1A)
  (res 1 . #x28)
  (restqt 1 . #x36)
  (ress 1 . #x44)
  (mibb 2 . #x45)
  (mibtqt 2 . #x37)
  (mib 2 . #x29)
  (mibqt 2 . #x1B)
  (mi 2 . 0)
  (misqt 2 . #x1A)
  (mis 2 . #x28)
  (mistqt 2 . #x36)
  (miss 2 . #x44)
  (fabb 3 . #x45)
  (fabtqt 3 . #x37)
  (fab 3 . #x29)
  (fabqt 3 . #x1B)
  (fa 3 . 0)
  (fasqt 3 . #x1A)
  (fas 3 . #x28)
  (fastqt 3 . #x36)
  (fass 3 . #x44)
  (solbb 4 . #x45)
  (solbtqt 4 . #x37)
  (solb 4 . #x29)
  (solbqt 4 . #x1B)
  (sol 4 . 0)
  (solsqt 4 . #x1A)
  (sols 4 . #x28)
  (solstqt 4 . #x36)
  (solss 4 . #x44)
  (labb 5 . #x45)
  (labtqt 5 . #x37)
  (lab 5 . #x29)
  (labqt 5 . #x1B)
  (la 5 . 0)
  (lasqt 5 . #x1A)
  (las 5 . #x28)
  (lastqt 5 . #x36)
  (lass 5 . #x44)
  (sibb 6 . #x45)
  (sibtqt 6 . #x37)
  (sib 6 . #x29)
  (sibqt 6 . #x1B)
  (si 6 . 0)
  (sisqt 6 . #x1A)
  (sis 6 . #x28)
  (sistqt 6 . #x36)
  (siss 6 . #x44)))
)


% Notation tables
ekmNotations = #'(

;; Standard notation (with arrows)
(std . (
  (#x00 #xE261)
  (#x1A #xE27A)
  (#x1B #xE27B)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE27A #xE262)
  (#x37 #xE27B #xE260)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE27A #xE263)
  (#x51 #xE27B #xE264)))

;; Sagittal notation
(sag . (
  (#x00 #xE261)
  (#x1A #xE30A)
  (#x1B #xE30B)
  (#x28 #xE318)
  (#x29 #xE319)
  (#x36 #xE326)
  (#x37 #xE327)
  (#x44 #xE334)
  (#x45 #xE335)
  (#x50 #xE30A #xE334)
  (#x51 #xE30B #xE335)))

;; Mixed Sagittal notation
(msag . (
  (#x00 #xE261)
  (#x1A #xE30A)
  (#x1B #xE30B)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE30A #xE262)
  (#x37 #xE30B #xE260)
  (#x44 #xE47D)
  (#x45 #xE264)
  (#x50 #xE30A #xE47D)
  (#x51 #xE30B #xE264)))

;; Stein / Zimmermann notation
(stz . (
  (#x00 #xE261)
  (#x1A #xE282)
  (#x1B #xE284)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE283)
  (#x37 #xE285)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE282 #xE263)
  (#x51 #xE284 #xE264)))

;; Stein / Half flat notation
(sth . (
  (#x00 #xE261)
  (#x1A #xE282)
  (#x1B #xF612)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE283)
  (#x37 #xF613)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE282 #xE263)
  (#x51 #xF612 #xE264)))
)


\include "ekmel-main.ily"