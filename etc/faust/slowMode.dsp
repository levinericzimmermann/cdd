declare name        "slowModeFilter";
declare version     "1.0";
declare options 	"[midi:on][nvoices:16]";

//      Filter instrument

import("stdfaust.lib");

baseFreq = hslider("freq",200,20,20000,0.01);
bend = ba.semi2ratio(hslider("bend[midi:pitchwheel]",0,-2,2,0.01));
freq = baseFreq * bend;
gain = hslider("gain", 0.25, 0, 1, 0.001);
gate = button("gate");
// envelope = en.adsre(8, 0.01, 0.6, 4, gate) * gain;
envelope = en.adsre(8, 0.01, 0.6, 4, gate) * gain;
attackReleaseEnv = en.smoothEnvelope(4, gate);

slowModeFilter(modeLfoFreq, originalGainLfoFreq) = _ <: modeFilter * envelope, originalFilteredSignal * envelope : bandpassFilter, _ : compressor, _ :> _ * attackReleaseEnv
with {
  originalFilteredSignal = fi.bandpass(2, freq * 0.7, freq * 1.35) * 0.5;
  modeDuration = ((os.lf_triangle(modeLfoFreq) + 1) * 1) + 1;
  modeFilter = pm.modeFilter(freq, modeDuration, 1) * 0.01;
  bandpassFilter = fi.bandpass(4, freq * 0.8, freq * 1.35);
  compressor = co.compressor_mono(18, -17, 0.05, 0.08);
};

// leftModeLfoFreqGenerator = (no.sparse_noise(0.01) + 1.2) * 0.3;
// RightModeLfoFreqGenerator = (no.sparse_noise(0.04) + 1.2) * 0.3;
// 
// leftOriginalGainFreqGenerator = (no.sparse_noise(0.05) + 1.2) * 0.2;
// RightOriginalGainFreqGenerator = (no.sparse_noise(0.04) + 1.2) * 0.2;
// 
// process = _, _ : slowModeFilter(leftModeLfoFreqGenerator, leftOriginalGainFreqGenerator), slowModeFilter(RightModeLfoFreqGenerator, RightOriginalGainFreqGenerator);
process = _, _ : slowModeFilter(1.2, 0.31), slowModeFilter(0.9, 0.57);
