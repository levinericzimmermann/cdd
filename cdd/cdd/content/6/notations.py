import typing

import abjad
import expenvelope
import quicktions as fractions

from mutwo import abjad_converters
from mutwo import cdd_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events

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
            sequential_event_to_quantized_abjad_container_converter=abjad_converters.RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            # No need for dynamics here
            mutwo_volume_to_abjad_attachment_dynamic_converter=None,
            tempo_envelope_to_abjad_attachment_tempo_converter=None,
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
            # abjad.attach(abjad.LilyPondLiteral(r"\numericTimeSignature"), first_leaf)
            # abjad.attach(abjad.LilyPondLiteral(r"\cadenzaOn"), first_leaf)
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\set Score.proportionalNotationDuration = #(ly:make-moment 1/32)"
                ),
                first_leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\override Score.SpacingSpanner.strict-note-spacing = ##t"
                ),
                first_leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(r"\omit StaffGroup.SystemStartBrace"),
                first_leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\override StaffGroup.SystemStartBracket.collapse-height = #100"
                ),
                first_leaf,
            )
            abjad.attach(abjad.LilyPondLiteral(r"\omit Staff.BarLine"), first_leaf)
        # We don't want any duration lines here
        voice._consists_commands = []
        staff = abjad.Staff([voice], lilypond_type="RhythmicStaff", name=tag)
        staff.remove_commands.append("Time_signature_engraver")
        abjad_converters.AddInstrumentName(
            instrument_name_font_size="small", short_instrument_name_font_size="small"
        )(event_to_convert, staff)
        return staff


class TextSequentialEventToRhythmicStaff(SequentialEventToRhythmicStaff):
    def convert(self, *args, **kwargs):
        rhythmic_staff = super().convert(*args, **kwargs)
        # rhythmic_staff.remove_commands.append("Staff_symbol_engraver")
        rhythmic_staff[0].remove_commands.append("Note_heads_engraver")
        # if rhythmic_staff[0]:
        #     first_leaf = abjad.get.leaf(rhythmic_staff, 0)
        #     # abjad.attach(abjad.LilyPondLiteral(r"\magnifyStaff #(magstep -50)"), first_leaf)
        #     # abjad.attach(abjad.LilyPondLiteral(r"\stopStaff"), first_leaf)

        return rhythmic_staff


class SopranoSequentialEventToRhythmicStaff(TextSequentialEventToRhythmicStaff):
    def convert(self, *args, **kwargs):
        rhythmic_staff = super().convert(*args, **kwargs)
        rhythmic_staff.remove_commands.append("Staff_symbol_engraver")
        return rhythmic_staff


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
                sequential_event_to_rhythmic_staff_class = (
                    SequentialEventToRhythmicStaff
                )
            else:
                short_instrument_name = (
                    cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                        instrument_name
                    ]
                )
                if instrument_name == "soprano":
                    sequential_event_to_rhythmic_staff_class = (
                        SopranoSequentialEventToRhythmicStaff
                    )
                else:
                    sequential_event_to_rhythmic_staff_class = (
                        TextSequentialEventToRhythmicStaff
                    )
            sequential_event_to_rhythmic_staff = (
                sequential_event_to_rhythmic_staff_class(
                    time_signature_sequence=time_signature_sequence,
                    tempo_envelope=tempo_envelope,
                )
            )
            tag_to_complex_event_to_abjad_container_converter.update(
                {short_instrument_name: sequential_event_to_rhythmic_staff}
            )

        tag_to_complex_event_to_abjad_container_converter.update(
            {"empty": sequential_event_to_rhythmic_staff}
        )

        super().__init__(
            nested_complex_event_to_complex_event_to_abjad_container_converters_converter=abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
                tag_to_complex_event_to_abjad_container_converter=tag_to_complex_event_to_abjad_container_converter
            ),
            abjad_container_class=abjad.StaffGroup,
            lilypond_type_of_abjad_container="StaffGroup",
        )

    def convert(self, simultaneous_event, *args, **kwargs) -> abjad.Score:
        simultaneous_event = simultaneous_event.copy()
        # simultaneous_event[0].instrument_name = ""
        empty_sequential_event = core_events.TaggedSequentialEvent([], tag="empty")
        event_count = int(simultaneous_event.duration)
        for _ in range(event_count):
            empty_sequential_event.append(
                music_events.NoteLike(fractions.Fraction(1, 1))
            )
        simultaneous_event.append(empty_sequential_event)
        abjad_staff_group = super().convert(simultaneous_event, *args, **kwargs)
        abjad_score = abjad.Score([abjad_staff_group])
        abjad_score.remove_commands.append("Bar_number_engraver")
        for staff in abjad_score:
            last_leaf = staff[0][-1][-1]
            try:
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\override StaffGroup.SystemStartBracket.collapse-height = #0"
                    ),
                    last_leaf,
                )
                abjad.attach(
                    abjad.LilyPondLiteral(
                        r"\undo \omit Staff.BarLine", format_slot="after"
                    ),
                    last_leaf,
                )
                abjad.attach(abjad.BarLine("|."), last_leaf)
            except Exception:
                pass
        return abjad_score


class AbjadScoreListToLilyPondFile(cdd_converters.AbjadScoreListToLilyPondFile):
    def get_layout_block(self, margin: float = 1) -> abjad.Block:
        layout_block = super().get_layout_block(margin)
        layout_block.items.append(
            r"""
\context {
    \Lyrics
      \override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing.basic-distance = #0
      \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.basic-distance = #0
      \override VerticalAxisGroup.default-staff-staff-spacing.basic-distance = #0
}
\context {
    \RhythmicStaff
      \override VerticalAxisGroup.default-staff-staff-spacing =
        #'((basic-distance . 4)
         (minimum-distance . 4)
         (padding . 0))
      \override VerticalAxisGroup.staff-staff-spacing.basic-distance = #0
      \override VerticalAxisGroup.nonstaff-unrelatedstaff-spacing.basic-distance = #0
      \override VerticalAxisGroup.nonstaff-relatedstaff-spacing.basic-distance = #0
      \override VerticalAxisGroup.default-staff-staff-spacing.basic-distance = #0
}
"""
        )
        return layout_block

    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_block.items.append(
            r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 15 in) (* 17 in))) paper-alist))
#(set-paper-size "my size")
system-system-spacing = #'((basic-distance . 7.5) (padding . 0))
"""
        )
        return paper_block


def main(chapter: cdd.chapters.Chapter):
    abjad_score_list_to_lilypond_file = AbjadScoreListToLilyPondFile()
    simultaneous_event_to_abjad_score = SimultaneousEventToAbjadScore(
        time_signature_sequence=chapter.time_signature_sequence,
        tempo_envelope=chapter.tempo_envelope,
    )
    abjad_score_list = [
        simultaneous_event_to_abjad_score.convert(chapter.simultaneous_event)
    ]
    abjad.attach(
        abjad.Markup("duration: circa 3'15", direction="^"),
        abjad.get.leaf(abjad_score_list[0], 0),
    )
    lilypond_file = abjad_score_list_to_lilypond_file.convert(
        abjad_score_list, add_ekmelily=False, add_book_preamble=False, margin=0
    )
    notation_file_path = chapter.get_notation_path("clarinet")
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
    chapter_to_latex_document = cdd_converters.ScoreChapterToLatexDocument(
        lilypond_file_path.split("/")[-1],
        instruction_text=chapter.instruction_text,
        width=1.2,
        hspace="-1.5cm",
    )
    latex_document = chapter_to_latex_document.convert(chapter, "clarinet")
    latex_document.generate_pdf(chapter.get_notation_path("clarinet"), clean_tex=False)
