import typing

import abjad
import expenvelope

from mutwo import abjad_converters
from mutwo import cdd_converters
from mutwo import core_events
from mutwo import core_parameters

import cdd


class SequentialEventToRhythmicStaff(abjad_converters.SequentialEventToAbjadVoice):
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
            abjad.attach(abjad.Clef("percussion"), first_leaf)
            abjad.attach(abjad.LilyPondLiteral(r"\numericTimeSignature"), first_leaf)
        staff = abjad.Staff([voice], lilypond_type="RhythmicStaff", name=tag)
        abjad_converters.AddInstrumentName(
            instrument_name_font_size="small", short_instrument_name_font_size="small"
        )(event_to_convert, staff)
        return staff


class SimultaneousEventToAbjadScore(
    abjad_converters.NestedComplexEventToAbjadContainer
):
    def __init__(
        self,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
    ):
        tag_to_complex_event_to_abjad_container_converter = {}

        for instrument_name in ("percussion", "soprano", "clarinet", "clavichord"):
            if (
                instrument_name
                in cdd.constants.ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME
            ):
                short_instrument_name = (
                    cdd.constants.ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        instrument_name
                    ]
                )
            else:
                short_instrument_name = (
                    cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        instrument_name
                    ]
                )
            sequential_event_to_rhythmic_staff = SequentialEventToRhythmicStaff(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            )
            tag_to_complex_event_to_abjad_container_converter.update(
                {short_instrument_name: sequential_event_to_rhythmic_staff}
            )

        super().__init__(
            nested_complex_event_to_complex_event_to_abjad_container_converters_converter=abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
                tag_to_complex_event_to_abjad_container_converter=tag_to_complex_event_to_abjad_container_converter
            ),
            abjad_container_class=abjad.Score,
            lilypond_type_of_abjad_container="Score",
        )


def main(chapter: cdd.chapters.Chapter):
    abjad_score_list_to_lilypond_file = cdd_converters.AbjadScoreListToLilyPondFile()
    simultaneous_event_to_abjad_score = SimultaneousEventToAbjadScore(
        time_signature_sequence=chapter.time_signature_sequence,
        tempo_envelope=chapter.tempo_envelope,
    )
    abjad_score_list = [
        simultaneous_event_to_abjad_score.convert(chapter.simultaneous_event)
    ]
    lilypond_file = abjad_score_list_to_lilypond_file.convert(
        abjad_score_list, add_ekmelily=False, add_book_preamble=True, margin=1
    )
    notation_file_path = chapter.get_notation_path("clarinet")
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
    chapter_to_latex_document = cdd_converters.ScoreChapterToLatexDocument(
        lilypond_file_path.split("/")[-1], instruction_text=chapter.instruction_text
    )
    latex_document = chapter_to_latex_document.convert(chapter, "clarinet")
    latex_document.generate_pdf(chapter.get_notation_path("clarinet"), clean_tex=False)
