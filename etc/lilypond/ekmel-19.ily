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
%% File: ekmel-19.ily  -  Include file for the 19-EDO tuning
%% Version: 3.7
%%
%% Note names derived from the semitone names in LilyPond 2.22
%% Copyright (C) 2010--2020 Valentin Villenave <valentin@villenave.net> et al.
%%

\version "2.19.22"


% Tuning table
ekmTuning = #'(
  (-1     0 18/19 36/19 48/19 66/19 84/19 102/19)
  (#x28 . 6/19)
  (#x44 . 12/19))


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
  (hes 6 . #x29)
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
  (heses 6 . #x45)))

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
  (bff 6 . #x45)))

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
  (beses 6 . #x45)))

;; Catalan names by Jaume Obrador <jobrador@ipc4.uib.es>
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
  (sibb 6 . #x45)))

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
  (sibb 6 . #x45)))

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
  (sibb 6 . #x45)))

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
  (sibb 6 . #x45)))

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
  (sibb 6 . #x45)))

;; Norwegian names by Arvid Grøtting <arvidg@ifi.uio.no>
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
  (hes 6 . #x29)
  (hess 6 . #x29)
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
  (heses 6 . #x45)
  (hessess 6 . #x45)))

;; Finnish names by Heikki Junes <heikki.junes@hut.fi>
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
  (hes 6 . #x29)
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
  (heses 6 . #x45)))

;; Swedish names by Mats Bengtsson <mabe@violin.s3.kth.se>
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
  (hess 6 . #x29)
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
  (hessess 6 . #x45)))

;; Vlaams names by Hendrik Maryns <hendrik.maryns@ugent.be>
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
  (sibb 6 . #x45)))
)


% Notation tables
ekmNotations = #'(

;; Standard notation
(std . (
  (#x00 #xE261)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x44 #xE263)
  (#x45 #xE264)))

;; Sagittal notation
(sag . (
  (#x00 #xE261)
  (#x28 #xE318)
  (#x29 #xE319)
  (#x44 #xE334)
  (#x45 #xE335)))

;; Mixed Sagittal notation
(msag . (
  (#x00 #xE261)
  (#x28 #xE262)
  (#x29 #xE260)
  (#x44 #xE47D)
  (#x45 #xE264)))
)


\include "ekmel-main.ily"
