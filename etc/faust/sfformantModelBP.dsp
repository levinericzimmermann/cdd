declare name        "sfformantModel";
declare version     "1.0";
declare author      "Levin Eric Zimmermann";
declare options 	"[midi:on][nvoices:12]";


import("stdfaust.lib");

gate = button("gate");
baseFreq = hslider("freq",200,20,20000,0.01);
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]",0,-2,2,0.0001)) : si.polySmooth(gate,0.999,1);
extra_bend = ba.semi2ratio(hslider("extra_bend",0,-2,2,0.0001));
voice_type = hslider("voice_type",0,0,4,0.001);
vowel = hslider("vowel",0,0,4,0.001);
extype_slider = hslider("extype",0,0,1,0.001);
freq = baseFreq * bend * extra_bend;
minimalGain = 0.1;
gain = hslider("gain", 0.25, 0, 1, 0.001);

filter_envelope_duration = hslider("filter_envelope_duration",4.95,0.5,6,0.001);
tremolo_envelope_duration = hslider("tremolo_envelope_duration",2,0.25,3,0.001);
extype_envelope_duration = hslider("z_extype_envelope_duration",2,0.05,4,0.001);

envelope = en.adsr(2, 1.5, 0.8, 4, gate);
filter_envelope = en.adsre(filter_envelope_duration, 1.5, 0.8, filter_envelope_duration + 1.05, gate) + 0.01;
tremolo_envelope = en.asr(tremolo_envelope_duration * 2, 1, tremolo_envelope_duration, gate);

tremolo_frequency = ((os.lf_triangle(0.2) + 1) / 2) + 0.85;
tremolo = (((os.lf_triangle(tremolo_frequency) + 1) / 2) * abs(tremolo_envelope - 1)) + tremolo_envelope;
extype_envelope = abs(en.asr(extype_envelope_duration, 1, extype_envelope_duration, gate) - 1);

extype = extype_envelope + extype_slider;

// formant_synthesis = pm.SFFormantModelBP(voice_type, vowel, extype, freq, gain);
// formant_synthesis = pm.SFFormantModelFofCycle(voice_type, vowel, freq, gain);
// formant_filter = pm.formantFilterFofCycle;
// formant_filterbank = pm.formantFilterbank(voice_type, vowel, formant_filter, freq);


lowfrequency_osc_modulator0_frequency = hslider("lowfrequency_osc_modulator0_frequency",0.18,0.05,0.25,0.000001);
lowfrequency_osc_modulator1_frequency = hslider("lowfrequency_osc_modulator1_frequency",0.15,0.05,0.25,0.000001);
lowfrequency_osc_modulator2_frequency = hslider("lowfrequency_osc_modulator2_frequency",0.2,0.05,0.25,0.000001);

lowfrequency_osc_modulator0 = (((no.lfnoise(lowfrequency_osc_modulator0_frequency) + 1) / 2) * 0.65) + 0.09 : si.smoo;
lowfrequency_osc_modulator1 = (((no.lfnoise(lowfrequency_osc_modulator1_frequency) + 1) / 2) * 0.5) + 0.12 : si.smoo;
lowfrequency_osc_modulator2 = (((no.lfnoise(lowfrequency_osc_modulator2_frequency) + 1) / 2) * 0.4) + 0.1 : si.smoo;

source_selector = (os.lf_triangle(lowfrequency_osc_modulator1) + 1) / 2 : _;
source_selector_2 = (os.lf_triangle(lowfrequency_osc_modulator0) + 1) / 2 : _;
source_selector_big = (os.lf_triangle(lowfrequency_osc_modulator2) + 1) / 2 : _;
saw_wave_amp_oscilator = (os.lf_triangle(2) + 1) / 2 : _;

saw_wave = os.sawtooth(freq) * (saw_wave_deep * 0.1 * saw_wave_amp_oscilator);
saw_wave_deep = os.sawtooth(freq * 0.5);
square_wave = (os.imptrain(freq) * 0.75) + (saw_wave_deep * 0.25) + (saw_wave * 0.25);
sine_wave_pure = os.oscsin(freq);
sine_wave = (sine_wave_pure * 0.35) + (saw_wave * 0.7);
sine_wave_deep = os.oscsin(freq * 0.5);
formant_synthesis_source_0 = saw_wave, sine_wave : si.interpolate(source_selector);
formant_synthesis_source = formant_synthesis_source_0, square_wave: si.interpolate(source_selector_2);
formant_synthesis_complex = pm.SFFormantModel(
	voice_type, vowel, extype, freq, gain, formant_synthesis_source, pm.formantFilterbankBP, 0
);
formant_synthesis_basic = (pm.SFFormantModelFofSmooth(
	voice_type, vowel, freq, gain
) * 12) + (formant_synthesis_complex * 0.2) + (sine_wave_deep * 0.1);
formant_synthesis = formant_synthesis_complex, formant_synthesis_basic: si.interpolate(source_selector_big);

filter_partial = (((no.lfnoise(3) + 1) / 2) * 22) + 35;
filtered_formant_synthesis = formant_synthesis : fi.lowpass6e(freq * filter_partial * filter_envelope) : fi.highpass3e(freq * 0.75);

process = filtered_formant_synthesis * envelope * tremolo;
