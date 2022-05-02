import math
import typing

import abjad
import expenvelope

from mutwo import abjad_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import cdd_converters
from mutwo import music_parameters

import cdd


class MutwoLyricToAbjadString(abjad_converters.MutwoLyricToAbjadString):
    def convert(self, mutwo_lyric_to_convert: music_parameters.abc.Lyric) -> str:
        lyric = super().convert(mutwo_lyric_to_convert)
        new_lyric = []
        for letter in lyric:
            is_added = False
            if letter not in ("_", "-", " "):
                if letter not in ("a", "e", "o", "u", "i", "é"):
                    is_added = True
                    new_lyric.append(f"({letter})")
            if not is_added:
                new_lyric.append(letter)
        return "".join(new_lyric).replace(")(", "")


class SequentialEventToAbjadStaff(abjad_converters.SequentialEventToAbjadVoice):
    def __init__(self, *args, add_cent_deviation: bool = True, **kwargs):
        super().__init__(
            *args,
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            mutwo_lyric_to_abjad_string=MutwoLyricToAbjadString(),
            **kwargs,
        )
        self._add_cent_deviation = add_cent_deviation

    def process_espressivo(self, abjad_voice: abjad.Voice):
        leaves = abjad.select(abjad_voice).leaves()
        start = None
        espressivo_list = []
        for index, leaf in enumerate(leaves):
            if start and not [
                indicator
                for indicator in abjad.get.indicators(leaf)
                if hasattr(indicator, "argument") and indicator.argument == "\\-"
            ]:
                end = index + 1

                try:
                    next_leaf = leaves[index + 1]
                except IndexError:
                    pass
                else:
                    if isinstance(next_leaf, (abjad.Skip, abjad.Rest)):
                        end += 1

                espressivo_list.append((start, end))
                start = None
            if abjad.detach(abjad.Articulation("espressivo"), leaf):
                abjad.attach(
                    abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t"),
                    leaf,
                )
                abjad.attach(abjad.StartHairpin("<"), leaf)
                start = index

        for start, end in espressivo_list:
            span = end - start
            center = int(math.ceil(span / 2) + start)
            center_leaf = leaves[center]
            abjad.attach(
                abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t"),
                center_leaf,
            )
            abjad.attach(abjad.StartHairpin(">"), center_leaf)
            # not necessary: already done in classes.py
            # stop_leaf = leaves[end + 1]
            # abjad.attach(abjad.StopHairpin(), stop_leaf)

    def convert(
        self, event_to_convert: core_events.SequentialEvent, *args, **kwargs
    ) -> abjad.Staff:
        if self._add_cent_deviation:
            cdd.utilities.add_cent_deviation_to_sequential_event(event_to_convert)
        voice = super().convert(event_to_convert, *args, **kwargs)
        self.process_espressivo(voice)
        if voice:
            first_leaf = abjad.get.leaf(voice, 0)
            abjad.attach(
                abjad.LilyPondLiteral(
                    (
                        r'\accidentalStyle "dodecaphonic" '
                        r"\numericTimeSignature "
                        r"\override Staff.TimeSignature.style = #'single-digit "
                        # r"\omit Staff.BarLine "
                        # r'\override Staff.BarLine.glyph = "!" '  # doesn't work :(
                        r"\override Staff.BarLine.hair-thickness = #0.1 "
                        # r"\override NoteHead.style = #'neomensural "
                        r"\override NoteHead.style = #'petrucci "
                    )
                ),
                first_leaf,
            )
            last_leaf = abjad.get.leaf(voice, -1)

            abjad.attach(
                abjad.LilyPondLiteral((r'\bar "|." '), format_slot="closing"),
                last_leaf,
            )
        staff = abjad.Staff([voice])
        return staff


class SequentialEventToDurationLineBasedStaff(SequentialEventToAbjadStaff):
    def __init__(
        self,
        *args,
        time_signature_sequence: typing.Sequence = [abjad.TimeSignature((8, 4))],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
        **kwargs,
    ):
        super().__init__(
            *args,
            sequential_event_to_quantized_abjad_container=abjad_converters.RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainer(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            **kwargs,
        )


class SequentialEventToRhythmBasedStaff(SequentialEventToAbjadStaff):
    def __init__(
        self,
        *args,
        time_signature_sequence: typing.Sequence = [abjad.TimeSignature((8, 4))],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
        **kwargs,
    ):
        super().__init__(
            *args,
            sequential_event_to_quantized_abjad_container=abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            **kwargs,
        )


class SopranoSequentialEventToAbjadStaff(SequentialEventToDurationLineBasedStaff):
    pass


class ClarinetSequentialEventToAbjadStaff(SequentialEventToDurationLineBasedStaff):
    pass


class ClavichordSequentialEventToAbjadStaff(SequentialEventToRhythmBasedStaff):
    pass


class ClavichordSequentialEventToAbjadStaffGroup(object):
    def __init__(
        self,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
    ):
        self.sequential_event_to_abjad_staff = ClavichordSequentialEventToAbjadStaff(
            time_signature_sequence=time_signature_sequence,
            tempo_envelope=tempo_envelope,
            add_cent_deviation=False,
        )

    def convert(
        self, sequential_event_to_convert: core_events.SequentialEvent
    ) -> abjad.StaffGroup:
        tabulatura_sequential_event = (
            cdd.constants.CLAVICHORD_SEQUENTIAL_EVENT_TO_TABULATURA_BASED_EVENT(
                sequential_event_to_convert
            )
        )

        simultaneous_event = (
            cdd_converters.SequentialEventToSplitSequentialEvent().convert(
                tabulatura_sequential_event
            )
        )
        # simultaneous_event = [tabulatura_sequential_event, tabulatura_sequential_event]

        piano_staff = abjad.StaffGroup([], lilypond_type="PianoStaff")
        for sequential_event in simultaneous_event:
            abjad_staff = self.sequential_event_to_abjad_staff.convert(sequential_event)
            piano_staff.append(abjad_staff)

        first_leaf_bass = abjad.get.leaf(piano_staff[1], 0)
        abjad.attach(abjad.Clef("bass"), first_leaf_bass)

        return piano_staff


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
        tag_to_complex_event_to_abjad_container_converter = {
            "soprano": SopranoSequentialEventToAbjadStaff,
            "clarinet": ClarinetSequentialEventToAbjadStaff,
            "clavichord": ClavichordSequentialEventToAbjadStaffGroup,
        }

        for tag, converter in tag_to_complex_event_to_abjad_container_converter.items():
            tag_to_complex_event_to_abjad_container_converter[tag] = converter(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            )

        super().__init__(
            nested_complex_event_to_complex_event_to_abjad_container_converters_converter=abjad_converters.TagBasedNestedComplexEventToComplexEventToAbjadContainers(
                tag_to_abjad_converter_dict=tag_to_complex_event_to_abjad_container_converter
            ),
            abjad_container_class=abjad.Score,
            lilypond_type_of_abjad_container="Score",
        )

    def convert(self, simultaneous_event, *args, **kwargs) -> abjad.Score:
        abjad_score = super().convert(simultaneous_event, *args, **kwargs)
        for abjad_staff_or_abjad_staff_group, sequential_event in zip(
            abjad_score, simultaneous_event
        ):
            sequential_event.instrument_name = sequential_event.tag
            sequential_event.short_instrument_name = (
                cdd.constants.INSTRUMENT_NAME_TO_SHORT_INSTRUMENT_NAME[
                    sequential_event.instrument_name
                ]
            )
            abjad_converters.AddInstrumentName(
                instrument_name_font_size=r"small \typewriter",
                short_instrument_name_font_size=r"small \typewriter",
            )(sequential_event, abjad_staff_or_abjad_staff_group)
        # abjad_score.remove_commands.append("Bar_number_engraver")
        return abjad_score


class AbjadScoreListToLilyPondFile(cdd_converters.AbjadScoreListToLilyPondFile):
    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_size = r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 10 in) (* 10 in))) paper-alist))
#(set-paper-size "my size")
system-system-spacing = #'((basic-distance . 7.5) (padding . 0))
"""
        paper_block.items.append(paper_size)
        return paper_block


def main(chapter: cdd.chapters.Chapter):
    for tagged_sequential_event in chapter.simultaneous_event:
        instrument_name = tagged_sequential_event.tag

        notation_file_path = chapter.get_notation_path(instrument_name)
        lilypond_file_path = f"{notation_file_path}_lilypond.pdf"

        abjad_score_list_to_lilypond_file = AbjadScoreListToLilyPondFile()
        simultaneous_event_to_abjad_score = SimultaneousEventToAbjadScore(
            time_signature_sequence=chapter.time_signature_sequence,
            tempo_envelope=chapter.tempo_envelope,
        )
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [simultaneous_event_to_abjad_score.convert(chapter.simultaneous_event)],
            add_ekmelily=True,
            # add_book_preamble=True,
            add_book_preamble=False,
            margin=15,
        )

        abjad.persist.as_pdf(lilypond_file, lilypond_file_path)

        chapter_to_latex_document = cdd_converters.ScoreChapterToLatexDocument(
            lilypond_file_path.split("/")[-1],
            instruction_text=chapter.instrument_name_to_instruction_text[
                instrument_name
            ],
            width=1,
            hspace="0.5cm",
        )

        latex_document = chapter_to_latex_document.convert(chapter, instrument_name)
        latex_document.generate_pdf(notation_file_path, clean_tex=True)
