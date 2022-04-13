import typing

import abjad
import expenvelope

from mutwo import abjad_converters
from mutwo import cdd_converters
from mutwo import core_events
from mutwo import core_parameters

import cdd


class SequentialEventToAbjadStaff(abjad_converters.SequentialEventToAbjadVoice):
    def __init__(
        self,
        *args,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
        **kwargs,
    ):
        super().__init__(
            *args,
            sequential_event_to_quantized_abjad_container_converter=abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            mutwo_pitch_to_abjad_pitch_converter=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            # No need for dynamics here
            mutwo_volume_to_abjad_attachment_dynamic_converter=None,
            **kwargs,
        )

    def convert(
        self, event_to_convert: core_events.SequentialEvent, *args, **kwargs
    ) -> abjad.Staff:
        voice = super().convert(event_to_convert, *args, **kwargs)
        try:
            tag = event_to_convert.tag  # type: ignore
        except AttributeError:
            tag = ""
        if voice:
            first_leaf = abjad.get.leaf(voice, 0)
            abjad.attach(
                abjad.LilyPondLiteral(r'\accidentalStyle "dodecaphonic"'), first_leaf
            )
        staff = abjad.Staff([voice], name=tag)
        staff.remove_commands.append("Time_signature_engraver")
        abjad_converters.AddInstrumentName(
            instrument_name_font_size="small", short_instrument_name_font_size="small"
        )(event_to_convert, staff)
        return staff


class SopranoSequentialEventToAbjadScore(SequentialEventToAbjadStaff):
    def convert(self, event_to_convert, repetition_count: int) -> abjad.Score:
        abjad_staff = super().convert(event_to_convert)
        if repetition_count > 1:
            abjad.attach(abjad.Repeat(repeat_count=repetition_count), abjad_staff[0])
            # abjad.attach(
            #     abjad.RehearsalMark(markup=abjad.Markup(f"repeat {repetition_count - 1}x")),
            #     abjad.get.leaf(abjad_staff[0], 0),
            # )
        abjad_score = abjad.Score([abjad_staff])
        return abjad_score


class AbjadScoreListToLilyPondFile(cdd_converters.AbjadScoreListToLilyPondFile):
    pass


def main(chapter: cdd.chapters.Chapter):
    abjad_score_list_to_lilypond_file = AbjadScoreListToLilyPondFile()
    abjad_score_list = [
        SopranoSequentialEventToAbjadScore(
            time_signature_sequence=[
                abjad.TimeSignature(
                    (
                        soprano_sequential_event.duration.numerator,
                        soprano_sequential_event.duration.denominator,
                    )
                )
            ],
            tempo_envelope=tempo_envelope,
        ).convert(soprano_sequential_event, repetition_count)
        for soprano_sequential_event, repetition_count, tempo_envelope in zip(
            chapter.soprano_sequential_event_tuple,
            chapter.soprano_repetition_count_tuple,
            chapter.soprano_tempo_envelope_tuple,
        )
    ]
    lilypond_file = abjad_score_list_to_lilypond_file.convert(
        abjad_score_list, add_ekmelily=True, add_book_preamble=True, margin=0
    )
    notation_file_path = chapter.get_notation_path("soprano")
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
    # chapter_to_latex_document = cdd_converters.ScoreChapterToLatexDocument(
    #     lilypond_file_path.split("/")[-1],
    #     instruction_text=chapter.instruction_text,
    #     width=1.2,
    #     hspace="-1.5cm",
    # )
    # latex_document = chapter_to_latex_document.convert(chapter, "clarinet")
    # latex_document.generate_pdf(chapter.get_notation_path("clarinet"), clean_tex=False)
