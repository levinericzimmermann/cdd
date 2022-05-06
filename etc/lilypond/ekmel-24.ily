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
%% File: ekmel-24.ily  -  Include file for the 24-EDO tuning
%% Version: 3.7
%%
%% Note names from the semitone and quarter-tone names in LilyPond 2.22
%% Copyright (C) 2010--2020 Valentin Villenave <valentin@villenave.net> et al.
%%
%% Extended with names for enharmonically equivalent quarter-tones.
%%

\version "2.19.22"


% Tuning table
ekmTuning = #'(
  (#x1A . 1/4)
  (#x28 . 1/2)
  (#x36 . 3/4)
  (#x44 . 1)
  (#x50 . 5/4))


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
  (cis 0 . #x28)
  (ces 0 . #x29)
  (dis 1 . #x28)
  (des 1 . #x29)
  (eis 2 . #x28)
  (es 2 . #x29)
  (fis 3 . #x28)
  (fes 3 . #x29)
  (gis 4 . #x28)
  (ges 4 . #x29)
  (ais 5 . #x28)
  (as 5 . #x29)
  (his 6 . #x28)
  (b 6 . #x29)
  (hes 6 . #x29)
  (cih 0 . #x1A)
  (ceh 0 . #x1B)
  (dih 1 . #x1A)
  (deh 1 . #x1B)
  (eih 2 . #x1A)
  (eh 2 . #x1B)
  (eeh 2 . #x1B)
  (fih 3 . #x1A)
  (feh 3 . #x1B)
  (gih 4 . #x1A)
  (geh 4 . #x1B)
  (aih 5 . #x1A)
  (ah 5 . #x1B)
  (aeh 5 . #x1B)
  (hih 6 . #x1A)
  (heh 6 . #x1B)
  (ciseh 0 . #x21A)
  (cesih 0 . #x21B)
  (diseh 1 . #x21A)
  (desih 1 . #x21B)
  (eiseh 2 . #x21A)
  (esih 2 . #x21B)
  (fiseh 3 . #x21A)
  (fesih 3 . #x21B)
  (giseh 4 . #x21A)
  (gesih 4 . #x21B)
  (aiseh 5 . #x21A)
  (asih 5 . #x21B)
  (hiseh 6 . #x21A)
  (hesih 6 . #x21B)
  (cisih 0 . #x36)
  (ceseh 0 . #x37)
  (disih 1 . #x36)
  (deseh 1 . #x37)
  (eisih 2 . #x36)
  (eseh 2 . #x37)
  (fisih 3 . #x36)
  (feseh 3 . #x37)
  (gisih 4 . #x36)
  (geseh 4 . #x37)
  (aisih 5 . #x36)
  (asah 5 . #x37)
  (aseh 5 . #x37)
  (hisih 6 . #x36)
  (heseh 6 . #x37)
  (cisiseh 0 . #x236)
  (cesesih 0 . #x237)
  (disiseh 1 . #x236)
  (desesih 1 . #x237)
  (eisiseh 2 . #x236)
  (esesih 2 . #x237)
  (fisiseh 3 . #x236)
  (fesesih 3 . #x237)
  (gisiseh 4 . #x236)
  (gesesih 4 . #x237)
  (aisiseh 5 . #x236)
  (asasih 5 . #x237)
  (asesih 5 . #x237)
  (hisiseh 6 . #x236)
  (hesesih 6 . #x237)
  (cisis 0 . #x44)
  (ceses 0 . #x45)
  (disis 1 . #x44)
  (deses 1 . #x45)
  (eisis 2 . #x44)
  (eses 2 . #x45)
  (fisis 3 . #x44)
  (feses 3 . #x45)
  (gisis 4 . #x44)
  (geses 4 . #x45)
  (aisis 5 . #x44)
  (asas 5 . #x45)
  (ases 5 . #x45)
  (hisis 6 . #x44)
  (heses 6 . #x45)
  (cisisih 0 . #x50)
  (ceseseh 0 . #x51)
  (disisih 1 . #x50)
  (deseseh 1 . #x51)
  (eisisih 2 . #x50)
  (eseseh 2 . #x51)
  (fisisih 3 . #x50)
  (feseseh 3 . #x51)
  (gisisih 4 . #x50)
  (geseseh 4 . #x51)
  (aisisih 5 . #x50)
  (asasah 5 . #x51)
  (aseseh 5 . #x51)
  (hisisih 6 . #x50)
  (heseseh 6 . #x51)))

;; English names by Han-Wen Nienhuys <hanwen@xs4all.nl>
(english . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)
  (cs 0 . #x28)
  (cf 0 . #x29)
  (ds 1 . #x28)
  (df 1 . #x29)
  (es 2 . #x28)
  (ef 2 . #x29)
  (fs 3 . #x28)
  (ff 3 . #x29)
  (gs 4 . #x28)
  (gf 4 . #x29)
  (as 5 . #x28)
  (af 5 . #x29)
  (bs 6 . #x28)
  (bf 6 . #x29)
  (cqs 0 . #x1A)
  (cqf 0 . #x1B)
  (dqs 1 . #x1A)
  (dqf 1 . #x1B)
  (eqs 2 . #x1A)
  (eqf 2 . #x1B)
  (fqs 3 . #x1A)
  (fqf 3 . #x1B)
  (gqs 4 . #x1A)
  (gqf 4 . #x1B)
  (aqs 5 . #x1A)
  (aqf 5 . #x1B)
  (bqs 6 . #x1A)
  (bqf 6 . #x1B)
  (csaqf 0 . #x21A)
  (cfaqs 0 . #x21B)
  (dsaqf 1 . #x21A)
  (dfaqs 1 . #x21B)
  (esaqf 2 . #x21A)
  (efaqs 2 . #x21B)
  (fsaqf 3 . #x21A)
  (ffaqs 3 . #x21B)
  (gsaqf 4 . #x21A)
  (gfaqs 4 . #x21B)
  (asaqf 5 . #x21A)
  (afaqs 5 . #x21B)
  (bsaqf 6 . #x21A)
  (bfaqs 6 . #x21B)
  (ctqs 0 . #x36)
  (ctqf 0 . #x37)
  (dtqs 1 . #x36)
  (dtqf 1 . #x37)
  (etqs 2 . #x36)
  (etqf 2 . #x37)
  (ftqs 3 . #x36)
  (ftqf 3 . #x37)
  (gtqs 4 . #x36)
  (gtqf 4 . #x37)
  (atqs 5 . #x36)
  (atqf 5 . #x37)
  (btqs 6 . #x36)
  (btqf 6 . #x37)
  (cssaqf 0 . #x236)
  (cffaqs 0 . #x237)
  (dssaqf 1 . #x236)
  (dffaqs 1 . #x237)
  (essaqf 2 . #x236)
  (effaqs 2 . #x237)
  (fssaqf 3 . #x236)
  (fffaqs 3 . #x237)
  (gssaqf 4 . #x236)
  (gffaqs 4 . #x237)
  (assaqf 5 . #x236)
  (affaqs 5 . #x237)
  (bssaqf 6 . #x236)
  (bffaqs 6 . #x237)
  (css 0 . #x44)
  (cx 0 . #x44)
  (cff 0 . #x45)
  (dss 1 . #x44)
  (dx 1 . #x44)
  (dff 1 . #x45)
  (ess 2 . #x44)
  (ex 2 . #x44)
  (eff 2 . #x45)
  (fss 3 . #x44)
  (fx 3 . #x44)
  (fff 3 . #x45)
  (gss 4 . #x44)
  (gx 4 . #x44)
  (gff 4 . #x45)
  (ass 5 . #x44)
  (ax 5 . #x44)
  (aff 5 . #x45)
  (bss 6 . #x44)
  (bx 6 . #x44)
  (bff 6 . #x45)
  (cfqs 0 . #x50)
  (cfqf 0 . #x51)
  (dfqs 1 . #x50)
  (dfqf 1 . #x51)
  (efqs 2 . #x50)
  (efqf 2 . #x51)
  (ffqs 3 . #x50)
  (ffqf 3 . #x51)
  (gfqs 4 . #x50)
  (gfqf 4 . #x51)
  (afqs 5 . #x50)
  (afqf 5 . #x51)
  (bfqs 6 . #x50)
  (bfqf 6 . #x51)))

;; Dutch names by Han-Wen Nienhuys <hanwen@xs4all.nl>
(nederlands . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (b 6 . 0)
  (cis 0 . #x28)
  (ces 0 . #x29)
  (dis 1 . #x28)
  (des 1 . #x29)
  (eis 2 . #x28)
  (ees 2 . #x29)
  (es 2 . #x29)
  (fis 3 . #x28)
  (fes 3 . #x29)
  (gis 4 . #x28)
  (ges 4 . #x29)
  (ais 5 . #x28)
  (aes 5 . #x29)
  (as 5 . #x29)
  (bis 6 . #x28)
  (bes 6 . #x29)
  (cih 0 . #x1A)
  (ceh 0 . #x1B)
  (dih 1 . #x1A)
  (deh 1 . #x1B)
  (eih 2 . #x1A)
  (eeh 2 . #x1B)
  (fih 3 . #x1A)
  (feh 3 . #x1B)
  (gih 4 . #x1A)
  (geh 4 . #x1B)
  (aih 5 . #x1A)
  (aeh 5 . #x1B)
  (bih 6 . #x1A)
  (beh 6 . #x1B)
  (ciseh 0 . #x21A)
  (cesih 0 . #x21B)
  (diseh 1 . #x21A)
  (desih 1 . #x21B)
  (eiseh 2 . #x21A)
  (eesih 2 . #x21B)
  (esih 2 . #x21B)
  (fiseh 3 . #x21A)
  (fesih 3 . #x21B)
  (giseh 4 . #x21A)
  (gesih 4 . #x21B)
  (aiseh 5 . #x21A)
  (aesih 5 . #x21B)
  (asih 5 . #x21B)
  (biseh 6 . #x21A)
  (besih 6 . #x21B)
  (cisih 0 . #x36)
  (ceseh 0 . #x37)
  (disih 1 . #x36)
  (deseh 1 . #x37)
  (eisih 2 . #x36)
  (eeseh 2 . #x37)
  (eseh 2 . #x37)
  (fisih 3 . #x36)
  (feseh 3 . #x37)
  (gisih 4 . #x36)
  (geseh 4 . #x37)
  (aisih 5 . #x36)
  (aeseh 5 . #x37)
  (aseh 5 . #x37)
  (bisih 6 . #x36)
  (beseh 6 . #x37)
  (cisiseh 0 . #x236)
  (cesesih 0 . #x237)
  (disiseh 1 . #x236)
  (desesih 1 . #x237)
  (eisiseh 2 . #x236)
  (eesesih 2 . #x237)
  (esesih 2 . #x237)
  (fisiseh 3 . #x236)
  (fesesih 3 . #x237)
  (gisiseh 4 . #x236)
  (gesesih 4 . #x237)
  (aisiseh 5 . #x236)
  (aesesih 5 . #x237)
  (asesih 5 . #x237)
  (bisiseh 6 . #x236)
  (besesih 6 . #x237)
  (cisis 0 . #x44)
  (ceses 0 . #x45)
  (disis 1 . #x44)
  (deses 1 . #x45)
  (eisis 2 . #x44)
  (eeses 2 . #x45)
  (eses 2 . #x45)
  (fisis 3 . #x44)
  (feses 3 . #x45)
  (gisis 4 . #x44)
  (geses 4 . #x45)
  (aisis 5 . #x44)
  (aeses 5 . #x45)
  (ases 5 . #x45)
  (bisis 6 . #x44)
  (beses 6 . #x45)
  (cisisih 0 . #x50)
  (ceseseh 0 . #x51)
  (disisih 1 . #x50)
  (deseseh 1 . #x51)
  (eisisih 2 . #x50)
  (eeseseh 2 . #x51)
  (eseseh 2 . #x51)
  (fisisih 3 . #x50)
  (feseseh 3 . #x51)
  (gisisih 4 . #x50)
  (geseseh 4 . #x51)
  (aisisih 5 . #x50)
  (aeseseh 5 . #x51)
  (aseseh 5 . #x51)
  (bisisih 6 . #x50)
  (beseseh 6 . #x51)))

;; Catalan names by Jaume Obrador <jobrador@ipc4.uib.es>
;; Torsten Hämmerle <torsten.haemmerle@web.de>  quarter-tones added
(catalan . català)
(català . (
  (do 0 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dod 0 . #x28)
  (dob 0 . #x29)
  (red 1 . #x28)
  (reb 1 . #x29)
  (mid 2 . #x28)
  (mib 2 . #x29)
  (fad 3 . #x28)
  (fab 3 . #x29)
  (sold 4 . #x28)
  (solb 4 . #x29)
  (lad 5 . #x28)
  (lab 5 . #x29)
  (sid 6 . #x28)
  (sib 6 . #x29)
  (doqd 0 . #x1A)
  (doqb 0 . #x1B)
  (reqd 1 . #x1A)
  (reqb 1 . #x1B)
  (miqd 2 . #x1A)
  (miqb 2 . #x1B)
  (faqd 3 . #x1A)
  (faqb 3 . #x1B)
  (solqd 4 . #x1A)
  (solqb 4 . #x1B)
  (laqd 5 . #x1A)
  (laqb 5 . #x1B)
  (siqd 6 . #x1A)
  (siqb 6 . #x1B)
  (dodqb 0 . #x21A)
  (dobqd 0 . #x21B)
  (redqb 1 . #x21A)
  (rebqd 1 . #x21B)
  (midqb 2 . #x21A)
  (mibqd 2 . #x21B)
  (fadqb 3 . #x21A)
  (fabqd 3 . #x21B)
  (soldqb 4 . #x21A)
  (solbqd 4 . #x21B)
  (ladqb 5 . #x21A)
  (labqd 5 . #x21B)
  (sidqb 6 . #x21A)
  (sibqd 6 . #x21B)
  (dotqd 0 . #x36)
  (dotqb 0 . #x37)
  (retqd 1 . #x36)
  (retqb 1 . #x37)
  (mitqd 2 . #x36)
  (mitqb 2 . #x37)
  (fatqd 3 . #x36)
  (fatqb 3 . #x37)
  (soltqd 4 . #x36)
  (soltqb 4 . #x37)
  (latqd 5 . #x36)
  (latqb 5 . #x37)
  (sitqd 6 . #x36)
  (sitqb 6 . #x37)
  (doddqb 0 . #x236)
  (dobbqd 0 . #x237)
  (reddqb 1 . #x236)
  (rebbqd 1 . #x237)
  (middqb 2 . #x236)
  (mibbqd 2 . #x237)
  (faddqb 3 . #x236)
  (fabbqd 3 . #x237)
  (solddqb 4 . #x236)
  (solbbqd 4 . #x237)
  (laddqb 5 . #x236)
  (labbqd 5 . #x237)
  (siddqb 6 . #x236)
  (sibbqd 6 . #x237)
  (dodd 0 . #x44)
  (dobb 0 . #x45)
  (redd 1 . #x44)
  (rebb 1 . #x45)
  (midd 2 . #x44)
  (mibb 2 . #x45)
  (fadd 3 . #x44)
  (fabb 3 . #x45)
  (soldd 4 . #x44)
  (solbb 4 . #x45)
  (ladd 5 . #x44)
  (labb 5 . #x45)
  (sidd 6 . #x44)
  (sibb 6 . #x45)
  (docqd 0 . #x50)
  (docqb 0 . #x51)
  (recqd 1 . #x50)
  (recqb 1 . #x51)
  (micqd 2 . #x50)
  (micqb 2 . #x51)
  (facqd 3 . #x50)
  (facqb 3 . #x51)
  (solcqd 4 . #x50)
  (solcqb 4 . #x51)
  (lacqd 5 . #x50)
  (lacqb 5 . #x51)
  (sicqd 6 . #x50)
  (sicqb 6 . #x51)))

;; Spanish names by Carlos García Suárez <cgscqmp@terra.es>,
;; Maximiliano G. G. <mxgdvg@yahoo.it>
(espanol . español)
(español . (
  (do 0 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dos 0 . #x28)
  (dob 0 . #x29)
  (res 1 . #x28)
  (reb 1 . #x29)
  (mis 2 . #x28)
  (mib 2 . #x29)
  (fas 3 . #x28)
  (fab 3 . #x29)
  (sols 4 . #x28)
  (solb 4 . #x29)
  (las 5 . #x28)
  (lab 5 . #x29)
  (sis 6 . #x28)
  (sib 6 . #x29)
  (docs 0 . #x1A)
  (docb 0 . #x1B)
  (recs 1 . #x1A)
  (recb 1 . #x1B)
  (mics 2 . #x1A)
  (micb 2 . #x1B)
  (facs 3 . #x1A)
  (facb 3 . #x1B)
  (solcs 4 . #x1A)
  (solcb 4 . #x1B)
  (lacs 5 . #x1A)
  (lacb 5 . #x1B)
  (sics 6 . #x1A)
  (sicb 6 . #x1B)
  (doscb 0 . #x21A)
  (dobcs 0 . #x21B)
  (rescb 1 . #x21A)
  (rebcs 1 . #x21B)
  (miscb 2 . #x21A)
  (mibcs 2 . #x21B)
  (fascb 3 . #x21A)
  (fabcs 3 . #x21B)
  (solscb 4 . #x21A)
  (solbcs 4 . #x21B)
  (lascb 5 . #x21A)
  (labcs 5 . #x21B)
  (siscb 6 . #x21A)
  (sibcs 6 . #x21B)
  (dotcs 0 . #x36)
  (dotcb 0 . #x37)
  (retcs 1 . #x36)
  (retcb 1 . #x37)
  (mitcs 2 . #x36)
  (mitcb 2 . #x37)
  (fatcs 3 . #x36)
  (fatcb 3 . #x37)
  (soltcs 4 . #x36)
  (soltcb 4 . #x37)
  (latcs 5 . #x36)
  (latcb 5 . #x37)
  (sitcs 6 . #x36)
  (sitcb 6 . #x37)
  (dosscb 0 . #x236)
  (doxcb 0 . #x236)
  (dobbcs 0 . #x237)
  (resscb 1 . #x236)
  (rexcb 1 . #x236)
  (rebbcs 1 . #x237)
  (misscb 2 . #x236)
  (mixcb 2 . #x236)
  (mibbcs 2 . #x237)
  (fasscb 3 . #x236)
  (faxcb 3 . #x236)
  (fabbcs 3 . #x237)
  (solsscb 4 . #x236)
  (solxcb 4 . #x236)
  (solbbcs 4 . #x237)
  (lasscb 5 . #x236)
  (laxcb 5 . #x236)
  (labbcs 5 . #x237)
  (sisscb 6 . #x236)
  (sixcb 6 . #x236)
  (sibbcs 6 . #x237)
  (doss 0 . #x44)
  (dox 0 . #x44)
  (dobb 0 . #x45)
  (ress 1 . #x44)
  (rex 1 . #x44)
  (rebb 1 . #x45)
  (miss 2 . #x44)
  (mix 2 . #x44)
  (mibb 2 . #x45)
  (fass 3 . #x44)
  (fax 3 . #x44)
  (fabb 3 . #x45)
  (solss 4 . #x44)
  (solx 4 . #x44)
  (solbb 4 . #x45)
  (lass 5 . #x44)
  (lax 5 . #x44)
  (labb 5 . #x45)
  (siss 6 . #x44)
  (six 6 . #x44)
  (sibb 6 . #x45)
  (doccs 0 . #x50)
  (doccb 0 . #x51)
  (reccs 1 . #x50)
  (reccb 1 . #x51)
  (miccs 2 . #x50)
  (miccb 2 . #x51)
  (faccs 3 . #x50)
  (faccb 3 . #x51)
  (solccs 4 . #x50)
  (solccb 4 . #x51)
  (laccs 5 . #x50)
  (laccb 5 . #x51)
  (siccs 6 . #x50)
  (siccb 6 . #x51)))

;; Italian names by Paolo Zuliani <zuliap@easynet.it>,
;; Eric Wurbel <wurbel@univ-tln.fr>
(italiano . (
  (do 0 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dod 0 . #x28)
  (dob 0 . #x29)
  (red 1 . #x28)
  (reb 1 . #x29)
  (mid 2 . #x28)
  (mib 2 . #x29)
  (fad 3 . #x28)
  (fab 3 . #x29)
  (sold 4 . #x28)
  (solb 4 . #x29)
  (lad 5 . #x28)
  (lab 5 . #x29)
  (sid 6 . #x28)
  (sib 6 . #x29)
  (dosd 0 . #x1A)
  (dosb 0 . #x1B)
  (resd 1 . #x1A)
  (resb 1 . #x1B)
  (misd 2 . #x1A)
  (misb 2 . #x1B)
  (fasd 3 . #x1A)
  (fasb 3 . #x1B)
  (solsd 4 . #x1A)
  (solsb 4 . #x1B)
  (lasd 5 . #x1A)
  (lasb 5 . #x1B)
  (sisd 6 . #x1A)
  (sisb 6 . #x1B)
  (dodsb 0 . #x21A)
  (dobsd 0 . #x21B)
  (redsb 1 . #x21A)
  (rebsd 1 . #x21B)
  (midsb 2 . #x21A)
  (mibsd 2 . #x21B)
  (fadsb 3 . #x21A)
  (fabsd 3 . #x21B)
  (soldsb 4 . #x21A)
  (solbsd 4 . #x21B)
  (ladsb 5 . #x21A)
  (labsd 5 . #x21B)
  (sidsb 6 . #x21A)
  (sibsd 6 . #x21B)
  (dodsd 0 . #x36)
  (dobsb 0 . #x37)
  (redsd 1 . #x36)
  (rebsb 1 . #x37)
  (midsd 2 . #x36)
  (mibsb 2 . #x37)
  (fadsd 3 . #x36)
  (fabsb 3 . #x37)
  (soldsd 4 . #x36)
  (solbsb 4 . #x37)
  (ladsd 5 . #x36)
  (labsb 5 . #x37)
  (sidsd 6 . #x36)
  (sibsb 6 . #x37)
  (doddsb 0 . #x236)
  (dobbsd 0 . #x237)
  (reddsb 1 . #x236)
  (rebbsd 1 . #x237)
  (middsb 2 . #x236)
  (mibbsd 2 . #x237)
  (faddsb 3 . #x236)
  (fabbsd 3 . #x237)
  (solddsb 4 . #x236)
  (solbbsd 4 . #x237)
  (laddsb 5 . #x236)
  (labbsd 5 . #x237)
  (siddsb 6 . #x236)
  (sibbsd 6 . #x237)
  (dodd 0 . #x44)
  (dobb 0 . #x45)
  (redd 1 . #x44)
  (rebb 1 . #x45)
  (midd 2 . #x44)
  (mibb 2 . #x45)
  (fadd 3 . #x44)
  (fabb 3 . #x45)
  (soldd 4 . #x44)
  (solbb 4 . #x45)
  (ladd 5 . #x44)
  (labb 5 . #x45)
  (sidd 6 . #x44)
  (sibb 6 . #x45)
  (doddsd 0 . #x50)
  (dobbsb 0 . #x51)
  (reddsd 1 . #x50)
  (rebbsb 1 . #x51)
  (middsd 2 . #x50)
  (mibbsb 2 . #x51)
  (faddsd 3 . #x50)
  (fabbsb 3 . #x51)
  (solddsd 4 . #x50)
  (solbbsb 4 . #x51)
  (laddsd 5 . #x50)
  (labbsb 5 . #x51)
  (siddsd 6 . #x50)
  (sibbsb 6 . #x51)))

;; French names by Valentin Villenave <valentin@villenave.net>
(français . (
  (do 0 . 0)
  (ré 1 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dod 0 . #x28)
  (dob 0 . #x29)
  (réd 1 . #x28)
  (red 1 . #x28)
  (réb 1 . #x29)
  (reb 1 . #x29)
  (mid 2 . #x28)
  (mib 2 . #x29)
  (fad 3 . #x28)
  (fab 3 . #x29)
  (sold 4 . #x28)
  (solb 4 . #x29)
  (lad 5 . #x28)
  (lab 5 . #x29)
  (sid 6 . #x28)
  (sib 6 . #x29)
  (dosd 0 . #x1A)
  (dosb 0 . #x1B)
  (résd 1 . #x1A)
  (resd 1 . #x1A)
  (résb 1 . #x1B)
  (resb 1 . #x1B)
  (misd 2 . #x1A)
  (misb 2 . #x1B)
  (fasd 3 . #x1A)
  (fasb 3 . #x1B)
  (solsd 4 . #x1A)
  (solsb 4 . #x1B)
  (lasd 5 . #x1A)
  (lasb 5 . #x1B)
  (sisd 6 . #x1A)
  (sisb 6 . #x1B)
  (dodsb 0 . #x21A)
  (dobsd 0 . #x21B)
  (rédsb 1 . #x21A)
  (redsb 1 . #x21A)
  (rébsd 1 . #x21B)
  (rebsd 1 . #x21B)
  (midsb 2 . #x21A)
  (mibsd 2 . #x21B)
  (fadsb 3 . #x21A)
  (fabsd 3 . #x21B)
  (soldsb 4 . #x21A)
  (solbsd 4 . #x21B)
  (ladsb 5 . #x21A)
  (labsd 5 . #x21B)
  (sidsb 6 . #x21A)
  (sibsd 6 . #x21B)
  (dodsd 0 . #x36)
  (dobsb 0 . #x37)
  (rédsd 1 . #x36)
  (redsd 1 . #x36)
  (rébsb 1 . #x37)
  (rebsb 1 . #x37)
  (midsd 2 . #x36)
  (mibsb 2 . #x37)
  (fadsd 3 . #x36)
  (fabsb 3 . #x37)
  (soldsd 4 . #x36)
  (solbsb 4 . #x37)
  (ladsd 5 . #x36)
  (labsb 5 . #x37)
  (sidsd 6 . #x36)
  (sibsb 6 . #x37)
  (doddsb 0 . #x236)
  (doxsb 0 . #x236)
  (dobbsd 0 . #x237)
  (réddsb 1 . #x236)
  (réxsb 1 . #x236)
  (reddsb 1 . #x236)
  (rexsb 1 . #x236)
  (rébbsd 1 . #x237)
  (rebbsd 1 . #x237)
  (middsb 2 . #x236)
  (mixsb 2 . #x236)
  (mibbsd 2 . #x237)
  (faddsb 3 . #x236)
  (faxsb 3 . #x236)
  (fabbsd 3 . #x237)
  (solddsb 4 . #x236)
  (solxsb 4 . #x236)
  (solbbsd 4 . #x237)
  (laddsb 5 . #x236)
  (laxsb 5 . #x236)
  (labbsd 5 . #x237)
  (siddsb 6 . #x236)
  (sixsb 6 . #x236)
  (sibbsd 6 . #x237)
  (dodd 0 . #x44)
  (dox 0 . #x44)
  (dobb 0 . #x45)
  (rédd 1 . #x44)
  (réx 1 . #x44)
  (redd 1 . #x44)
  (rex 1 . #x44)
  (rébb 1 . #x45)
  (rebb 1 . #x45)
  (midd 2 . #x44)
  (mix 2 . #x44)
  (mibb 2 . #x45)
  (fadd 3 . #x44)
  (fax 3 . #x44)
  (fabb 3 . #x45)
  (soldd 4 . #x44)
  (solx 4 . #x44)
  (solbb 4 . #x45)
  (ladd 5 . #x44)
  (lax 5 . #x44)
  (labb 5 . #x45)
  (sidd 6 . #x44)
  (six 6 . #x44)
  (sibb 6 . #x45)
  (doddsd 0 . #x50)
  (doxsd 0 . #x50)
  (dobbsb 0 . #x51)
  (réddsd 1 . #x50)
  (réxsd 1 . #x50)
  (reddsd 1 . #x50)
  (rexsd 1 . #x50)
  (rébbsb 1 . #x51)
  (rebbsb 1 . #x51)
  (middsd 2 . #x50)
  (mixsd 2 . #x50)
  (mibbsb 2 . #x51)
  (faddsd 3 . #x50)
  (faxsd 3 . #x50)
  (fabbsb 3 . #x51)
  (solddsd 4 . #x50)
  (solxsd 4 . #x50)
  (solbbsb 4 . #x51)
  (laddsd 5 . #x50)
  (laxsd 5 . #x50)
  (labbsb 5 . #x51)
  (siddsd 6 . #x50)
  (sixsd 6 . #x50)
  (sibbsb 6 . #x51)))

;; Portuguese names by Pedro Kröger <kroeger@pedrokroeger.net>
(portugues . português)
(português . (
  (do 0 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dos 0 . #x28)
  (dob 0 . #x29)
  (res 1 . #x28)
  (reb 1 . #x29)
  (mis 2 . #x28)
  (mib 2 . #x29)
  (fas 3 . #x28)
  (fab 3 . #x29)
  (sols 4 . #x28)
  (solb 4 . #x29)
  (las 5 . #x28)
  (lab 5 . #x29)
  (sis 6 . #x28)
  (sib 6 . #x29)
  (dosqt 0 . #x1A)
  (dobqt 0 . #x1B)
  (resqt 1 . #x1A)
  (rebqt 1 . #x1B)
  (misqt 2 . #x1A)
  (mibqt 2 . #x1B)
  (fasqt 3 . #x1A)
  (fabqt 3 . #x1B)
  (solsqt 4 . #x1A)
  (solbqt 4 . #x1B)
  (lasqt 5 . #x1A)
  (labqt 5 . #x1B)
  (sisqt 6 . #x1A)
  (sibqt 6 . #x1B)
  (dosbqt 0 . #x21A)
  (dobsqt 0 . #x21B)
  (resbqt 1 . #x21A)
  (rebsqt 1 . #x21B)
  (misbqt 2 . #x21A)
  (mibsqt 2 . #x21B)
  (fasbqt 3 . #x21A)
  (fabsqt 3 . #x21B)
  (solsbqt 4 . #x21A)
  (solbsqt 4 . #x21B)
  (lasbqt 5 . #x21A)
  (labsqt 5 . #x21B)
  (sisbqt 6 . #x21A)
  (sibsqt 6 . #x21B)
  (dostqt 0 . #x36)
  (dobtqt 0 . #x37)
  (restqt 1 . #x36)
  (rebtqt 1 . #x37)
  (mistqt 2 . #x36)
  (mibtqt 2 . #x37)
  (fastqt 3 . #x36)
  (fabtqt 3 . #x37)
  (solstqt 4 . #x36)
  (solbtqt 4 . #x37)
  (lastqt 5 . #x36)
  (labtqt 5 . #x37)
  (sistqt 6 . #x36)
  (sibtqt 6 . #x37)
  (dossbqt 0 . #x236)
  (dobbsqt 0 . #x237)
  (ressbqt 1 . #x236)
  (rebbsqt 1 . #x237)
  (missbqt 2 . #x236)
  (mibbsqt 2 . #x237)
  (fassbqt 3 . #x236)
  (fabbsqt 3 . #x237)
  (solssbqt 4 . #x236)
  (solbbsqt 4 . #x237)
  (lassbqt 5 . #x236)
  (labbsqt 5 . #x237)
  (sissbqt 6 . #x236)
  (sibbsqt 6 . #x237)
  (doss 0 . #x44)
  (dobb 0 . #x45)
  (ress 1 . #x44)
  (rebb 1 . #x45)
  (miss 2 . #x44)
  (mibb 2 . #x45)
  (fass 3 . #x44)
  (fabb 3 . #x45)
  (solss 4 . #x44)
  (solbb 4 . #x45)
  (lass 5 . #x44)
  (labb 5 . #x45)
  (siss 6 . #x44)
  (sibb 6 . #x45)
  (doscqt 0 . #x50)
  (dobcqt 0 . #x51)
  (rescqt 1 . #x50)
  (rebcqt 1 . #x51)
  (miscqt 2 . #x50)
  (mibcqt 2 . #x51)
  (fascqt 3 . #x50)
  (fabcqt 3 . #x51)
  (solscqt 4 . #x50)
  (solbcqt 4 . #x51)
  (lascqt 5 . #x50)
  (labcqt 5 . #x51)
  (siscqt 6 . #x50)
  (sibcqt 6 . #x51)))

;; Norwegian names by Arvid Grøtting <arvidg@ifi.uio.no>
;; Torsten Hämmerle <torsten.haemmerle@web.de>  quarter-tones added
(norsk . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (h 6 . 0)
  (cis 0 . #x28)
  (ciss 0 . #x28)
  (ces 0 . #x29)
  (cess 0 . #x29)
  (dis 1 . #x28)
  (diss 1 . #x28)
  (des 1 . #x29)
  (dess 1 . #x29)
  (eis 2 . #x28)
  (eiss 2 . #x28)
  (ees 2 . #x29)
  (eess 2 . #x29)
  (es 2 . #x29)
  (ess 2 . #x29)
  (fis 3 . #x28)
  (fiss 3 . #x28)
  (fes 3 . #x29)
  (fess 3 . #x29)
  (gis 4 . #x28)
  (giss 4 . #x28)
  (ges 4 . #x29)
  (gess 4 . #x29)
  (ais 5 . #x28)
  (aiss 5 . #x28)
  (aes 5 . #x29)
  (aess 5 . #x29)
  (as 5 . #x29)
  (ass 5 . #x29)
  (his 6 . #x28)
  (hiss 6 . #x28)
  (b 6 . #x29)
  (cih 0 . #x1A)
  (ceh 0 . #x1B)
  (dih 1 . #x1A)
  (deh 1 . #x1B)
  (eih 2 . #x1A)
  (eeh 2 . #x1B)
  (eh 2 . #x1B)
  (fih 3 . #x1A)
  (feh 3 . #x1B)
  (gih 4 . #x1A)
  (geh 4 . #x1B)
  (aih 5 . #x1A)
  (aeh 5 . #x1B)
  (hih 6 . #x1A)
  (heh 6 . #x1B)
  (ciseh 0 . #x21A)
  (cisseh 0 . #x21A)
  (cesih 0 . #x21B)
  (cessih 0 . #x21B)
  (diseh 1 . #x21A)
  (disseh 1 . #x21A)
  (desih 1 . #x21B)
  (dessih 1 . #x21B)
  (eiseh 2 . #x21A)
  (eisseh 2 . #x21A)
  (eesih 2 . #x21B)
  (eessih 2 . #x21B)
  (esih 2 . #x21B)
  (essih 2 . #x21B)
  (fiseh 3 . #x21A)
  (fisseh 3 . #x21A)
  (fesih 3 . #x21B)
  (fessih 3 . #x21B)
  (giseh 4 . #x21A)
  (gisseh 4 . #x21A)
  (gesih 4 . #x21B)
  (gessih 4 . #x21B)
  (aiseh 5 . #x21A)
  (aisseh 5 . #x21A)
  (aesih 5 . #x21B)
  (aessih 5 . #x21B)
  (asih 5 . #x21B)
  (assih 5 . #x21B)
  (hiseh 6 . #x21A)
  (hisseh 6 . #x21A)
  (bih 6 . #x21B)
  (cisih 0 . #x36)
  (cissih 0 . #x36)
  (ceseh 0 . #x37)
  (cesseh 0 . #x37)
  (disih 1 . #x36)
  (dissih 1 . #x36)
  (deseh 1 . #x37)
  (desseh 1 . #x37)
  (eisih 2 . #x36)
  (eissih 2 . #x36)
  (eeseh 2 . #x37)
  (eesseh 2 . #x37)
  (eseh 2 . #x37)
  (esseh 2 . #x37)
  (fisih 3 . #x36)
  (fissih 3 . #x36)
  (feseh 3 . #x37)
  (fesseh 3 . #x37)
  (gisih 4 . #x36)
  (gissih 4 . #x36)
  (geseh 4 . #x37)
  (gesseh 4 . #x37)
  (aisih 5 . #x36)
  (aissih 5 . #x36)
  (aeseh 5 . #x37)
  (aesseh 5 . #x37)
  (aseh 5 . #x37)
  (asseh 5 . #x37)
  (hisih 6 . #x36)
  (hissih 6 . #x36)
  (beh 6 . #x37)
  (cisiseh 0 . #x236)
  (cississeh 0 . #x236)
  (cesesih 0 . #x237)
  (cessessih 0 . #x237)
  (disiseh 1 . #x236)
  (dississeh 1 . #x236)
  (desesih 1 . #x237)
  (dessessih 1 . #x237)
  (eisiseh 2 . #x236)
  (eississeh 2 . #x236)
  (eesesih 2 . #x237)
  (eessessih 2 . #x237)
  (esesih 2 . #x237)
  (essessih 2 . #x237)
  (fisiseh 3 . #x236)
  (fississeh 3 . #x236)
  (fesesih 3 . #x237)
  (fessessih 3 . #x237)
  (gisiseh 4 . #x236)
  (gississeh 4 . #x236)
  (gesesih 4 . #x237)
  (gessessih 4 . #x237)
  (aisiseh 5 . #x236)
  (aississeh 5 . #x236)
  (aesesih 5 . #x237)
  (aessessih 5 . #x237)
  (asesih 5 . #x237)
  (assessih 5 . #x237)
  (hisiseh 6 . #x236)
  (hississeh 6 . #x236)
  (besih 6 . #x237)
  (bessih 6 . #x237)
  (cisis 0 . #x44)
  (cississ 0 . #x44)
  (ceses 0 . #x45)
  (cessess 0 . #x45)
  (disis 1 . #x44)
  (dississ 1 . #x44)
  (deses 1 . #x45)
  (dessess 1 . #x45)
  (eisis 2 . #x44)
  (eississ 2 . #x44)
  (eeses 2 . #x45)
  (eessess 2 . #x45)
  (eses 2 . #x45)
  (essess 2 . #x45)
  (fisis 3 . #x44)
  (fississ 3 . #x44)
  (feses 3 . #x45)
  (fessess 3 . #x45)
  (gisis 4 . #x44)
  (gississ 4 . #x44)
  (geses 4 . #x45)
  (gessess 4 . #x45)
  (aisis 5 . #x44)
  (aississ 5 . #x44)
  (aeses 5 . #x45)
  (aessess 5 . #x45)
  (ases 5 . #x45)
  (assess 5 . #x45)
  (hisis 6 . #x44)
  (hississ 6 . #x44)
  (bes 6 . #x45)
  (bess 6 . #x45)
  (cisisih 0 . #x50)
  (cississih 0 . #x50)
  (ceseseh 0 . #x51)
  (cessesseh 0 . #x51)
  (disisih 1 . #x50)
  (dississih 1 . #x50)
  (deseseh 1 . #x51)
  (dessesseh 1 . #x51)
  (eisisih 2 . #x50)
  (eississih 2 . #x50)
  (eeseseh 2 . #x51)
  (eessesseh 2 . #x51)
  (eseseh 2 . #x51)
  (essesseh 2 . #x51)
  (fisisih 3 . #x50)
  (fississih 3 . #x50)
  (feseseh 3 . #x51)
  (fessesseh 3 . #x51)
  (gisisih 4 . #x50)
  (gississih 4 . #x50)
  (geseseh 4 . #x51)
  (gessesseh 4 . #x51)
  (aisisih 5 . #x50)
  (aississih 5 . #x50)
  (aeseseh 5 . #x51)
  (aessesseh 5 . #x51)
  (aseseh 5 . #x51)
  (assesseh 5 . #x51)
  (hisisih 6 . #x50)
  (hississih 6 . #x50)
  (beseh 6 . #x51)
  (besseh 6 . #x51)))

;; Finnish names by Heikki Junes <heikki.junes@hut.fi>
;; Torsten Hämmerle <torsten.haemmerle@web.de>  quarter-tones added
(suomi . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (h 6 . 0)
  (cis 0 . #x28)
  (ces 0 . #x29)
  (dis 1 . #x28)
  (des 1 . #x29)
  (eis 2 . #x28)
  (es 2 . #x29)
  (fis 3 . #x28)
  (fes 3 . #x29)
  (gis 4 . #x28)
  (ges 4 . #x29)
  (ais 5 . #x28)
  (as 5 . #x29)
  (his 6 . #x28)
  (b 6 . #x29)
  (cih 0 . #x1A)
  (ceh 0 . #x1B)
  (dih 1 . #x1A)
  (deh 1 . #x1B)
  (eih 2 . #x1A)
  (eeh 2 . #x1B)
  (fih 3 . #x1A)
  (feh 3 . #x1B)
  (gih 4 . #x1A)
  (geh 4 . #x1B)
  (aih 5 . #x1A)
  (aeh 5 . #x1B)
  (hih 6 . #x1A)
  (heh 6 . #x1B)
  (ciseh 0 . #x21A)
  (cesih 0 . #x21B)
  (diseh 1 . #x21A)
  (desih 1 . #x21B)
  (eiseh 2 . #x21A)
  (esih 2 . #x21B)
  (fiseh 3 . #x21A)
  (fesih 3 . #x21B)
  (giseh 4 . #x21A)
  (gesih 4 . #x21B)
  (aiseh 5 . #x21A)
  (asih 5 . #x21B)
  (hiseh 6 . #x21A)
  (bih 6 . #x21B)
  (cisih 0 . #x36)
  (ceseh 0 . #x37)
  (disih 1 . #x36)
  (deseh 1 . #x37)
  (eisih 2 . #x36)
  (eseh 2 . #x37)
  (fisih 3 . #x36)
  (feseh 3 . #x37)
  (gisih 4 . #x36)
  (geseh 4 . #x37)
  (aisih 5 . #x36)
  (asah 5 . #x37)
  (aseh 5 . #x37)
  (hisih 6 . #x36)
  (beh 6 . #x37)
  (cisiseh 0 . #x236)
  (cesesih 0 . #x237)
  (disiseh 1 . #x236)
  (desesih 1 . #x237)
  (eisiseh 2 . #x236)
  (esesih 2 . #x237)
  (fisiseh 3 . #x236)
  (fesesih 3 . #x237)
  (gisiseh 4 . #x236)
  (gesesih 4 . #x237)
  (aisiseh 5 . #x236)
  (asasih 5 . #x237)
  (asesih 5 . #x237)
  (hisiseh 6 . #x236)
  (besih 6 . #x237)
  (hesesih 6 . #x237)
  (cisis 0 . #x44)
  (ceses 0 . #x45)
  (disis 1 . #x44)
  (deses 1 . #x45)
  (eisis 2 . #x44)
  (eses 2 . #x45)
  (fisis 3 . #x44)
  (feses 3 . #x45)
  (gisis 4 . #x44)
  (geses 4 . #x45)
  (aisis 5 . #x44)
  (asas 5 . #x45)
  (ases 5 . #x45)
  (hisis 6 . #x44)
  (bes 6 . #x45)
  (heses 6 . #x45)
  (cisisih 0 . #x50)
  (ceseseh 0 . #x51)
  (disisih 1 . #x50)
  (deseseh 1 . #x51)
  (eisisih 2 . #x50)
  (eseseh 2 . #x51)
  (fisisih 3 . #x50)
  (feseseh 3 . #x51)
  (gisisih 4 . #x50)
  (geseseh 4 . #x51)
  (aisisih 5 . #x50)
  (asasah 5 . #x51)
  (aseseh 5 . #x51)
  (hisisih 6 . #x50)
  (beseh 6 . #x51)
  (heseseh 6 . #x51)))

;; Swedish names by Mats Bengtsson <mabe@violin.s3.kth.se>
;; Torsten Hämmerle <torsten.haemmerle@web.de>  quarter-tones added
(svenska . (
  (c 0 . 0)
  (d 1 . 0)
  (e 2 . 0)
  (f 3 . 0)
  (g 4 . 0)
  (a 5 . 0)
  (h 6 . 0)
  (ciss 0 . #x28)
  (cess 0 . #x29)
  (diss 1 . #x28)
  (dess 1 . #x29)
  (eiss 2 . #x28)
  (ess 2 . #x29)
  (fiss 3 . #x28)
  (fess 3 . #x29)
  (giss 4 . #x28)
  (gess 4 . #x29)
  (aiss 5 . #x28)
  (ass 5 . #x29)
  (hiss 6 . #x28)
  (b 6 . #x29)
  (cih 0 . #x1A)
  (ceh 0 . #x1B)
  (dih 1 . #x1A)
  (deh 1 . #x1B)
  (eih 2 . #x1A)
  (eeh 2 . #x1B)
  (fih 3 . #x1A)
  (feh 3 . #x1B)
  (gih 4 . #x1A)
  (geh 4 . #x1B)
  (aih 5 . #x1A)
  (aeh 5 . #x1B)
  (hih 6 . #x1A)
  (heh 6 . #x1B)
  (cisseh 0 . #x21A)
  (cessih 0 . #x21B)
  (disseh 1 . #x21A)
  (dessih 1 . #x21B)
  (eisseh 2 . #x21A)
  (essih 2 . #x21B)
  (fisseh 3 . #x21A)
  (fessih 3 . #x21B)
  (gisseh 4 . #x21A)
  (gessih 4 . #x21B)
  (aisseh 5 . #x21A)
  (assih 5 . #x21B)
  (hisseh 6 . #x21A)
  (hessih 6 . #x21B)
  (cissih 0 . #x36)
  (cesseh 0 . #x37)
  (dissih 1 . #x36)
  (desseh 1 . #x37)
  (eissih 2 . #x36)
  (esseh 2 . #x37)
  (fissih 3 . #x36)
  (fesseh 3 . #x37)
  (gissih 4 . #x36)
  (gesseh 4 . #x37)
  (aissih 5 . #x36)
  (asseh 5 . #x37)
  (hissih 6 . #x36)
  (hesseh 6 . #x37)
  (cississeh 0 . #x236)
  (cessessih 0 . #x237)
  (dississeh 1 . #x236)
  (dessessih 1 . #x237)
  (eississeh 2 . #x236)
  (essessih 2 . #x237)
  (fississeh 3 . #x236)
  (fessessih 3 . #x237)
  (gississeh 4 . #x236)
  (gessessih 4 . #x237)
  (aississeh 5 . #x236)
  (assessih 5 . #x237)
  (hississeh 6 . #x236)
  (hessessih 6 . #x237)
  (cississ 0 . #x44)
  (cessess 0 . #x45)
  (dississ 1 . #x44)
  (dessess 1 . #x45)
  (eississ 2 . #x44)
  (essess 2 . #x45)
  (fississ 3 . #x44)
  (fessess 3 . #x45)
  (gississ 4 . #x44)
  (gessess 4 . #x45)
  (aississ 5 . #x44)
  (assess 5 . #x45)
  (hississ 6 . #x44)
  (hessess 6 . #x45)
  (cississih 0 . #x50)
  (cessesseh 0 . #x51)
  (dississih 1 . #x50)
  (dessesseh 1 . #x51)
  (eississih 2 . #x50)
  (essesseh 2 . #x51)
  (fississih 3 . #x50)
  (fessesseh 3 . #x51)
  (gississih 4 . #x50)
  (gessesseh 4 . #x51)
  (aississih 5 . #x50)
  (assesseh 5 . #x51)
  (hississih 6 . #x50)
  (hessesseh 6 . #x51)))

;; Vlaams names by Hendrik Maryns <hendrik.maryns@ugent.be>
;; Torsten Hämmerle <torsten.haemmerle@web.de>  quarter-tones added
(vlaams . (
  (do 0 . 0)
  (re 1 . 0)
  (mi 2 . 0)
  (fa 3 . 0)
  (sol 4 . 0)
  (la 5 . 0)
  (si 6 . 0)
  (dok 0 . #x28)
  (dob 0 . #x29)
  (rek 1 . #x28)
  (reb 1 . #x29)
  (mik 2 . #x28)
  (mib 2 . #x29)
  (fak 3 . #x28)
  (fab 3 . #x29)
  (solk 4 . #x28)
  (solb 4 . #x29)
  (lak 5 . #x28)
  (lab 5 . #x29)
  (sik 6 . #x28)
  (sib 6 . #x29)
  (dohk 0 . #x1A)
  (dohb 0 . #x1B)
  (rehk 1 . #x1A)
  (rehb 1 . #x1B)
  (mihk 2 . #x1A)
  (mihb 2 . #x1B)
  (fahk 3 . #x1A)
  (fahb 3 . #x1B)
  (solhk 4 . #x1A)
  (solhb 4 . #x1B)
  (lahk 5 . #x1A)
  (lahb 5 . #x1B)
  (sihk 6 . #x1A)
  (sihb 6 . #x1B)
  (dokhb 0 . #x21A)
  (dobhk 0 . #x21B)
  (rekhb 1 . #x21A)
  (rebhk 1 . #x21B)
  (mikhb 2 . #x21A)
  (mibhk 2 . #x21B)
  (fakhb 3 . #x21A)
  (fabhk 3 . #x21B)
  (solkhb 4 . #x21A)
  (solbhk 4 . #x21B)
  (lakhb 5 . #x21A)
  (labhk 5 . #x21B)
  (sikhb 6 . #x21A)
  (sibhk 6 . #x21B)
  (dokhk 0 . #x36)
  (dobhb 0 . #x37)
  (rekhk 1 . #x36)
  (rebhb 1 . #x37)
  (mikhk 2 . #x36)
  (mibhb 2 . #x37)
  (fakhk 3 . #x36)
  (fabhb 3 . #x37)
  (solkhk 4 . #x36)
  (solbhb 4 . #x37)
  (lakhk 5 . #x36)
  (labhb 5 . #x37)
  (sikhk 6 . #x36)
  (sibhb 6 . #x37)
  (dokkhb 0 . #x236)
  (dobbhk 0 . #x237)
  (rekkhb 1 . #x236)
  (rebbhk 1 . #x237)
  (mikkhb 2 . #x236)
  (mibbhk 2 . #x237)
  (fakkhb 3 . #x236)
  (fabbhk 3 . #x237)
  (solkkhb 4 . #x236)
  (solbbhk 4 . #x237)
  (lakkhb 5 . #x236)
  (labbhk 5 . #x237)
  (sikkhb 6 . #x236)
  (sibbhk 6 . #x237)
  (dokk 0 . #x44)
  (dobb 0 . #x45)
  (rekk 1 . #x44)
  (rebb 1 . #x45)
  (mikk 2 . #x44)
  (mibb 2 . #x45)
  (fakk 3 . #x44)
  (fabb 3 . #x45)
  (solkk 4 . #x44)
  (solbb 4 . #x45)
  (lakk 5 . #x44)
  (labb 5 . #x45)
  (sikk 6 . #x44)
  (sibb 6 . #x45)
  (dokkhk 0 . #x50)
  (dobbhb 0 . #x51)
  (rekkhk 1 . #x50)
  (rebbhb 1 . #x51)
  (mikkhk 2 . #x50)
  (mibbhb 2 . #x51)
  (fakkhk 3 . #x50)
  (fabbhb 3 . #x51)
  (solkkhk 4 . #x50)
  (solbbhb 4 . #x51)
  (lakkhk 5 . #x50)
  (labbhb 5 . #x51)
  (sikkhk 6 . #x50)
  (sibbhb 6 . #x51)))
)


% Notation tables
ekmNotations = #'(

;; Stein / Couper notation
(stc . (
  (#x00 #xE261)
  (#x1A #xE282)
  (#x1B #xE284)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE283)
  (#x37 #xE489)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE282 #xE263)
  (#x51 #xE284 #xE264)
  (#x21A #xE284 #xE262)
  (#x21B #xE282 #xE260)
  (#x236 #xE284 #xE263)
  (#x237 #xE282 #xE264)))

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
  (#x51 #xE284 #xE264)
  (#x21A #xE284 #xE262)
  (#x21B #xE282 #xE260)
  (#x236 #xE284 #xE263)
  (#x237 #xE282 #xE264)))

;; Gould notation
(go . (
  (#x00 #xE261)
  (#x1A #xE272)
  (#x1B #xE273)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE274)
  (#x37 #xE271)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE276)
  (#x51 #xE279)
  (#x21A #xE275)
  (#x21B #xE270)
  (#x236 #xE277)
  (#x237 #xE278)))

;; Stein / Van Blankenburg / Tartini notation
(stvt . (
  (#x00 #xE261)
  (#x1A #xE282)
  (#x1B #xE488)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE283)
  (#x37 #xE487)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE282 #xE263)
  (#x51 #xE488 #xE264)
  (#x21A #xE488 #xE262)
  (#x21B #xE282 #xE260)
  (#x236 #xE488 #xE263)
  (#x237 #xE282 #xE264)))

;; Arrow notation
(arrow . (
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
  (#x51 #xE27B #xE264)
  (#x21A #xE27B #xE262)
  (#x21B #xE27A #xE260)
  (#x236 #xE27B #xE263)
  (#x237 #xE27A #xE264)))

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
  (#x51 #xE30B #xE264)
  (#x21A #xE30B #xE262)
  (#x21B #xE30A #xE260)
  (#x236 #xE30B #xE47D)
  (#x237 #xE30A #xE264)))

;; Arabic notation
(arabic . (
  (#x00 #xED34)
  (#x1A #xED35)
  (#x1B #xED33)
  (#x28 #xED36)
  (#x29 #xED32)
  (#x36 #xED37)
  (#x37 #xED31)
  (#x44 #xED38)
  (#x45 #xED30)
  (#x50 #xED35 #xED38)
  (#x51 #xED33 #xED30)
  (#x21A #xED33 #xED36)
  (#x21B #xED35 #xED32)
  (#x236 #xED33 #xED38)
  (#x237 #xED35 #xED30)))

;; Persian notation (Koron,Sori)
(persian . (
  (#x00 #xE261)
  (#x1A #xE461)
  (#x1B #xE460)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE262 #xE461)
  (#x37 #xE260 #xE460)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE263 #xE461)
  (#x51 #xE264 #xE460)
  (#x21A #xE262 #xE460)
  (#x21B #xE260 #xE461)
  (#x236 #xE263 #xE460)
  (#x237 #xE264 #xE461)))

;; Digit 4 notation
(four . (
  (#x00 #xE261)
  (#x1A #xE47E)
  (#x1B #xE47F)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xE47E #xE262)
  (#x37 #xE47F #xE260)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xE47E #xE263)
  (#x51 #xE47F #xE264)
  (#x21A #xE47F #xE262)
  (#x21B #xE47E #xE260)
  (#x236 #xE47F #xE263)
  (#x237 #xE47E #xE264)))

;; Hába notation
(haba . (
  (#x00 #xE261)
  (#x1A #xEE64)
  (#x1B #xEE67)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x36 #xEE66)
  (#x37 #xEE69)
  (#x44 #xE263)
  (#x45 #xE264)
  (#x50 #xEE64 #xE263)
  (#x51 #xEE67 #xE264)
  (#x21A #xEE68)
  (#x21B #xEE65)
  (#x236 #xEE67 #xE263)
  (#x237 #xEE64 #xE264)))
)


\include "ekmel-main.ily"


% Alteration order for key signatures with quarter tones
\layout {
  \context {
    \Score
    keyAlterationOrder = #'(
      (6 . -1/2) (2 . -1/2) (5 . -1/2) (1 . -1/2) (4 . -1/2) (0 . -1/2) (3 . -1/2)
      (3 .  1/2) (0 .  1/2) (4 .  1/2) (1 .  1/2) (5 .  1/2) (2 .  1/2) (6 .  1/2)
      (6 . -1/4) (2 . -1/4) (5 . -1/4) (1 . -1/4) (4 . -1/4) (0 . -1/4) (3 . -1/4)
      (3 .  1/4) (0 .  1/4) (4 .  1/4) (1 .  1/4) (5 .  1/4) (2 .  1/4) (6 .  1/4)
      (6 . -3/4) (2 . -3/4) (5 . -3/4) (1 . -3/4) (4 . -3/4) (0 . -3/4) (3 . -3/4)
      (3 .  3/4) (0 .  3/4) (4 .  3/4) (1 .  3/4) (5 .  3/4) (2 .  3/4) (6 .  3/4)
      (6 .   -1) (2 .   -1) (5 .   -1) (1 .   -1) (4 .   -1) (0 .   -1) (3 .   -1)
      (3 .    1) (0 .    1) (4 .    1) (1 .    1) (5 .    1) (2 .    1) (6 .    1)
    )
  }
}
