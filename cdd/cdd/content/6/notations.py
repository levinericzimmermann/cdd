import typing

import abjad
import expenvelope

from mutwo import abjad_converters
from mutwo import cdd_converters
from mutwo import core_converters
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
        super().__init__(
            nested_complex_event_to_complex_event_to_abjad_container_converters_converter=abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
                tag_to_complex_event_to_abjad_container_converter={
                    cdd.constants.ADDED_INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "percussion"
                    ]: SequentialEventToRhythmicStaff(
                        time_signature_sequence=time_signature_sequence,
                        tempo_envelope=tempo_envelope,
                    ),
                    cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "soprano"
                    ]: SequentialEventToRhythmicStaff(
                        time_signature_sequence=time_signature_sequence,
                        tempo_envelope=tempo_envelope,
                    ),
                    cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "clarinet"
                    ]: SequentialEventToRhythmicStaff(
                        time_signature_sequence=time_signature_sequence,
                        tempo_envelope=tempo_envelope,
                    ),
                    cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        "clavichord"
                    ]: SequentialEventToRhythmicStaff(
                        time_signature_sequence=time_signature_sequence,
                        tempo_envelope=tempo_envelope,
                    ),
                }
            ),
            abjad_container_class=abjad.Score,
            lilypond_type_of_abjad_container="Score",
        )


class SimultaneousEventToLilyPondFile(core_converters.abc.Converter):
    def __init__(self, *args, **kwargs):
        self.simultaneous_event_toabjad_score = SimultaneousEventToAbjadScore(
            *args, **kwargs
        )

    def convert(self, *args, **kwargs) -> abjad.LilyPondFile:
        margin = 1
        abjad_score = self.simultaneous_event_toabjad_score.convert(*args, **kwargs)
        score_block = abjad.Block("score")
        score_block.items.append(abjad_score)
        layout_block = abjad.Block("layout")
        layout_block.items.append(r"short-indent = {}\mm".format(margin))
        layout_block.items.append(r"ragged-last = ##f")
        layout_block.items.append(r"indent = {}\mm".format(margin))
        paper_block = abjad.Block("paper")
        paper_block.items.append(
            r"""#(define fonts
        (make-pango-font-tree "EB Garamond"
                            "Nimbus Sans"
                            "Luxi Mono"
                            (/ staff-height pt 20)))"""
        )
        paper_block.items.append(
            r"""score-system-spacing =
    #'((basic-distance . 30)
    (minimum-distance . 18)
    (padding . 1)
    (stretchability . 12))"""
        )
        includes = []
        includes.append("lilypond-book-preamble.ly")

        lilypond_file = abjad.LilyPondFile(includes=includes)
        lilypond_file.items.extend([score_block, paper_block, layout_block])

        return lilypond_file


def main(chapter: cdd.chapters.Chapter):
    lilypond_file = SimultaneousEventToLilyPondFile(
        time_signature_sequence=chapter.time_signature_sequence
    ).convert(chapter.simultaneous_event)
    notation_file_path = chapter.get_notation_path("clarinet")
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
    chapter_to_latex_document = cdd_converters.ScoreChapterToLatexDocument(
        lilypond_file_path.split("/")[-1], instruction_text=chapter.instruction_text
    )
    latex_document = chapter_to_latex_document.convert(chapter, "clarinet")
    latex_document.generate_pdf(chapter.get_notation_path("clarinet"), clean_tex=False)
