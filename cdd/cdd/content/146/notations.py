import typing

import abjad
import expenvelope
import pylatex

from mutwo import abjad_converters
from mutwo import cdd_converters
from mutwo import cdd_utilities
from mutwo import core_events
from mutwo import core_parameters
from mutwo import music_events

import cdd


class SequentialEventToAbjadVoice(abjad_converters.SequentialEventToAbjadVoice):
    def __init__(
        self,
        *args,
        **kwargs,
    ):
        super().__init__(
            *args,
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            # No need for dynamics here
            tempo_envelope_to_abjad_attachment_tempo=None,
            **kwargs,
        )

    def convert(
        self, event_to_convert: core_events.SequentialEvent, *args, **kwargs
    ) -> abjad.Staff:
        voice = super().convert(event_to_convert, *args, **kwargs)
        if voice:
            first_leaf = abjad.get.leaf(voice, 0)
            abjad.attach(
                abjad.LilyPondLiteral(r'\accidentalStyle "dodecaphonic"'), first_leaf
            )
        return voice


class SequentialEventToAbjadStaff(SequentialEventToAbjadVoice):
    def convert(
        self, event_to_convert: core_events.SequentialEvent, *args, **kwargs
    ) -> abjad.Staff:
        voice = super().convert(event_to_convert, *args, **kwargs)
        try:
            tag = event_to_convert.tag  # type: ignore
        except AttributeError:
            tag = ""
        staff = abjad.Staff([voice], name=tag)
        staff.remove_commands.append("Time_signature_engraver")
        abjad_converters.AddInstrumentName(
            instrument_name_font_size="small", short_instrument_name_font_size="small"
        )(event_to_convert, staff)
        return staff


class SopranoSequentialEventToAbjadScore(SequentialEventToAbjadStaff):
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
            sequential_event_to_quantized_abjad_container=abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            **kwargs,
        )

    def convert(
        self,
        event_to_convert,
        repetition_count: int,
        absolute_time_in_seconds: float,
        add_repetition_count: bool = True,
        start_size: str = "smaller",
    ) -> abjad.Score:
        abjad_staff = super().convert(event_to_convert)
        start_time_markup = abjad.Markup(
            f"\\typewriter {{ \\{start_size} {{ start at "
            f"{cdd_utilities.duration_in_seconds_to_readable_duration(absolute_time_in_seconds)}"
            "} }",
            direction="up",
        )
        first_leaf = abjad.get.leaf(abjad_staff[0], 0)
        abjad.attach(start_time_markup, first_leaf)
        if repetition_count > 1:
            abjad.attach(abjad.Repeat(repeat_count=repetition_count), abjad_staff[0])
        if add_repetition_count:
            abjad.attach(
                abjad.LilyPondLiteral(
                    (
                        f"\\set Staff.instrumentName = \\markup {{ "
                        # r" \normalsize { \caps {"
                        r" \smaller { \typewriter {"
                        f"sing {repetition_count}x }} }}"
                        r"}"
                    )
                ),
                first_leaf,
            )
        abjad_score = abjad.Score([abjad_staff])
        return abjad_score


class SopranoAndClarinetSimultaneousEventToAbjadScore(
    SopranoSequentialEventToAbjadScore
):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._clarinet_sequential_event_to_abjad_staff = SequentialEventToAbjadStaff(
            sequential_event_to_quantized_abjad_container=self._sequential_event_to_quantized_abjad_container,
            mutwo_volume_to_abjad_attachment_dynamic=None,
        )

    def convert(
        self, event_to_convert, *args, adjust_clarinet: bool = False, **kwargs
    ) -> abjad.Score:
        soprano, clarinet = event_to_convert

        # Either write transposed or not
        if adjust_clarinet:
            start_size = "large"
            clarinet = cdd.utilities.clarinet_event_to_notatable_clarinet_event(
                clarinet
            )
        else:
            start_size = "smaller"

        score_soprano = super().convert(
            soprano, *args, add_repetition_count=False, start_size=start_size, **kwargs
        )

        score_soprano[0].name = "soprano"
        staff_clarinet = self._clarinet_sequential_event_to_abjad_staff.convert(
            clarinet
        )
        staff_clarinet.name = "clarinet"
        score_soprano.append(staff_clarinet)

        # Make other voice smaller
        index_to_magnify = not adjust_clarinet
        staff_to_magnify = score_soprano[index_to_magnify]
        abjad.attach(
            abjad.LilyPondLiteral(
                "\\magnifyStaff #(magstep -3.5)",
                format_slot="before",
            ),
            abjad.get.leaf(staff_to_magnify, 0),
        )

        # Add instrument name markups
        abjad.detach(abjad.MarginMarkup, abjad.get.leaf(score_soprano[0][0], 0))

        for instrument_name, staff in zip(("soprano", "clarinet"), score_soprano):
            abjad.attach(
                abjad.LilyPondLiteral(
                    (
                        r"\set Staff.instrumentName = \markup { \smaller { \typewriter {"
                        f"{instrument_name}"
                        r"} } }"
                    )
                ),
                abjad.get.leaf(staff, 0),
            )

        return score_soprano


class ClavichordSequentialEventToAbjadVoice(SequentialEventToAbjadVoice):
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
            mutwo_volume_to_abjad_attachment_dynamic=None,
            **kwargs,
        )


class ClavichordSimultaneousEventToAbjadScore(SequentialEventToAbjadStaff):
    def __init__(self):
        self.sequential_event_to_abjad_voice = ClavichordSequentialEventToAbjadVoice()

    def convert(
        self,
        event_to_convert: core_events.SimultaneousEvent[core_events.SequentialEvent],
        absolute_time_in_seconds: float,
    ) -> tuple[abjad.Score, bool]:
        if not hasattr(event_to_convert[1][0], "playing_indicator_collection"):
            event_to_convert[1][0] = music_events.NoteLike(
                [], duration=event_to_convert[1][0].duration
            )
        note_with_clef = event_to_convert[1][0]
        if note_with_clef.grace_note_sequential_event:
            note_with_clef = note_with_clef.grace_note_sequential_event[0]

        note_with_clef.notation_indicator_collection.clef.name = "bass"
        is_voice_rest_tuple = tuple(
            all(list(map(cdd.utilities.is_rest, sequential_event)))
            for sequential_event in event_to_convert
        )
        voice_0, voice_1 = (
            self.sequential_event_to_abjad_voice.convert(sequential_event)
            for sequential_event in event_to_convert
        )
        is_rest = all(is_voice_rest_tuple)
        if not is_rest:
            voice_tuple = (voice_0, voice_1)
        elif is_rest:
            voice_tuple = (voice_0,)
        elif is_voice_rest_tuple[0]:
            voice_tuple = (voice_1,)
        else:
            voice_tuple = (voice_0,)

        # Fix bug: flags and stems in first grace note
        for voice in voice_tuple:
            leaf = voice[0][0]
            before_grace_note_container = abjad.get.before_grace_container(leaf)
            if before_grace_note_container and len(before_grace_note_container) > 0:
                grace_note = before_grace_note_container[0]
                abjad.attach(
                    abjad.LilyPondLiteral("\\override Staff.Dots.dot-count = #0"),
                    grace_note,
                )
                # don't write stems (Rhythm get defined by duration line)
                abjad.attach(abjad.LilyPondLiteral("\\omit Voice.Stem"), grace_note)
                # don't write flags (Rhythm get defined by duration line)
                abjad.attach(abjad.LilyPondLiteral("\\omit Voice.Flag"), grace_note)
                # don't write beams (Rhythm get defined by duration line)
                abjad.attach(abjad.LilyPondLiteral("\\omit Voice.Beam"), grace_note)

        abjad_staff_group = abjad.StaffGroup(
            [abjad.Staff([voice]) for voice in voice_tuple], lilypond_type="PianoStaff"
        )

        abjad.attach(
            abjad.LilyPondLiteral(r"\omit PianoStaff.SpanBar"),
            abjad.get.leaf(abjad_staff_group, 0),
        )
        for abjad_staff in abjad_staff_group:
            first_leaf = abjad.get.leaf(abjad_staff, 0)
            abjad.attach(
                abjad.LilyPondLiteral(r"\set PianoStaff.connectArpeggios = ##t"),
                first_leaf,
            )
            abjad.attach(abjad.LilyPondLiteral(r"\omit Staff.BarLine"), first_leaf)
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\set Score.proportionalNotationDuration = #(ly:make-moment 1/4)"
                ),
                first_leaf,
            )
            abjad_staff.remove_commands.append("Time_signature_engraver")

        readable_duration = cdd_utilities.duration_in_seconds_to_readable_duration(
            absolute_time_in_seconds
        )
        # it's redundant to print the first duration (as it's redundant to print
        # the first bar number)
        if absolute_time_in_seconds != 0:
            abjad.attach(
                abjad.RehearsalMark(
                    markup=abjad.Markup(
                        r"\typewriter { \smaller {" + readable_duration + "} }"
                    )
                ),
                abjad.get.leaf(abjad_staff_group[0], 0),
            )
        abjad_score = abjad.Score([abjad_staff_group])
        abjad_score.remove_commands.append("Bar_number_engraver")
        return abjad_score, is_rest


class ClarinetSequentialEventToAbjadScore(SequentialEventToAbjadStaff):
    def convert(self, event_to_convert) -> abjad.Score:
        abjad_staff = super().convert(
            cdd.utilities.clarinet_event_to_notatable_clarinet_event(event_to_convert)
        )
        abjad_staff.remove_commands.append("Bar_engraver")
        abjad_score = abjad.Score([abjad_staff])
        abjad_score.remove_commands.append("Bar_number_engraver")
        return abjad_score


class AbjadScoreListToLilyPondFile(cdd_converters.AbjadScoreListToLilyPondFile):
    pass


class AbjadScoreListToFlexibleLilyPondFile(cdd_converters.AbjadScoreListToLilyPondFile):
    def __init__(self, *args, x=2, y=1, **kwargs):
        self._x, self._y = x, y
        super().__init__(*args, **kwargs)

    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_block.items.append(
            f"""
#(set! paper-alist
  (cons '("my size" . (cons (* {self._x} in) (* {self._y} in))) paper-alist))
#(set-paper-size "my size")
"""
        )
        return paper_block


def convert_soprano_related_event_to_abjad_score(
    event_to_abjad_score_class,
    soprano_sequential_event,
    repetition_count,
    absolute_time_in_seconds,
    **kwargs,
):
    return event_to_abjad_score_class(
        time_signature_sequence=[
            abjad.TimeSignature(
                (
                    soprano_sequential_event.duration.numerator,
                    soprano_sequential_event.duration.denominator,
                )
            )
        ],
    ).convert(
        soprano_sequential_event, repetition_count, absolute_time_in_seconds, **kwargs
    )


def add_last_phrase_hairpin(last_score):
    for staff in last_score:
        first_leaf = abjad.get.leaf(staff, 0)
        abjad.attach(
            abjad.LilyPondLiteral(r"\override Hairpin.circled-tip = ##t"), first_leaf
        )
        abjad.attach(abjad.StartHairpin(">"), first_leaf)
        last_leaf = abjad.get.leaf(staff, -1)
        abjad.attach(abjad.StopHairpin(), last_leaf)
        cdd.utilities.add_last_bar_line(last_leaf)

        leaves = abjad.select(staff).leaves()
        leaf_8 = leaves[8]
        last_leaf = leaves[-1]

        abjad.attach(abjad.StartTextSpan(left_text=abjad.Markup("rit.")), leaf_8)
        abjad.attach(abjad.StopTextSpan(), last_leaf)


def notate_soprano(chapter: cdd.chapters.Chapter):
    instrument = "soprano"
    abjad_score_list_to_lilypond_file = AbjadScoreListToLilyPondFile()
    abjad_score_list = []

    for (
        index,
        soprano_sequential_event,
        repetition_count,
        absolute_time_in_seconds,
    ) in zip(
        range(len(chapter.soprano_sequential_event_tuple)),
        chapter.soprano_sequential_event_tuple,
        chapter.soprano_repetition_count_tuple,
        chapter.soprano_sequential_event_absolute_time_tuple,
    ):
        if index in chapter.CLARINET.unisono_part_index_tuple:
            event_to_abjad_score_class = SopranoAndClarinetSimultaneousEventToAbjadScore
            soprano_sequential_event = (
                chapter.soprano_and_clarinet_unisono_simultaneous_event_tuple[
                    chapter.CLARINET.unisono_part_index_tuple.index(index)
                ]
            )
        else:
            event_to_abjad_score_class = SopranoSequentialEventToAbjadScore

        abjad_score = convert_soprano_related_event_to_abjad_score(
            event_to_abjad_score_class,
            soprano_sequential_event,
            repetition_count,
            absolute_time_in_seconds,
        )
        abjad_score_list.append(abjad_score)

    last_score = abjad_score_list[-1]

    add_last_phrase_hairpin(last_score)

    notation_file_path = chapter.get_notation_path(instrument)
    lilypond_file_path_base = f"{notation_file_path}_lilypond"
    lilypond_file_path_list = []
    for index, abjad_score in enumerate(abjad_score_list):
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [abjad_score],
            add_ekmelily=True,
            add_book_preamble=True,
            add_fancy_glissando=True,
            margin=0,
        )
        lilypond_file_path = f"{lilypond_file_path_base}_{index}.pdf"
        abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
        lilypond_file_path_list.append(lilypond_file_path.split("/")[-1])

    chapter_to_latex_document = cdd_converters.ScoreListChapterToLatexDocument(
        lilypond_file_path_list,
        instruction_text=chapter.SOPRANO.instruction_text,
        width=0.95,
        hspace="0.0cm",
        vspace="0.2cm",
    )
    latex_document = chapter_to_latex_document.convert(chapter, instrument)
    latex_document.generate_pdf(chapter.get_notation_path(instrument), clean_tex=True)


def notate_clarinet(chapter: cdd.chapters.Chapter):
    def add_pdf(lilypond_file_path, width):
        figure = pylatex.Figure(position="h!")
        figure.append(
            pylatex.NoEscape(
                r"\includegraphics[width="
                + str(width)
                + r"\textwidth]{"
                + lilypond_file_path.split("/")[-1]
                + "}"
            )
        )
        latex_document.append(figure)

    def add_sequential_event(
        sequential_event,
        path_suffix,
        width=0.2,
        abjad_score_list_to_lilypond_file_class=AbjadScoreListToFlexibleLilyPondFile,
        abjad_score_list_to_lilypond_file_class_kwargs={},
    ):
        abjad_score = clarinet_sequential_event_to_abjad_score(sequential_event)
        lilypond_file = abjad_score_list_to_lilypond_file_class(
            **abjad_score_list_to_lilypond_file_class_kwargs
        )(
            [abjad_score],
            add_ekmelily=True,
            add_book_preamble=False,
            add_fancy_glissando=True,
            margin=0,
        )
        lilypond_file_path = f"{notation_file_path}_{path_suffix}.pdf"
        abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
        add_pdf(lilypond_file_path, width)

    instrument = "clarinet"

    clarinet_sequential_event_to_abjad_score = ClarinetSequentialEventToAbjadScore()
    notation_file_path = chapter.get_notation_path(instrument)

    soprano_and_clarinet_unisono_width = 0.9
    soprano_and_clarinet_unisono_file_path_list = []
    for index, simultaneous_event in zip(
        chapter.CLARINET.unisono_part_index_tuple,
        chapter.soprano_and_clarinet_unisono_simultaneous_event_tuple,
    ):
        repetition_count = chapter.soprano_repetition_count_tuple[index]
        absolute_time_in_seconds = chapter.soprano_sequential_event_absolute_time_tuple[
            index
        ]
        abjad_score = convert_soprano_related_event_to_abjad_score(
            SopranoAndClarinetSimultaneousEventToAbjadScore,
            simultaneous_event,
            repetition_count,
            absolute_time_in_seconds,
            adjust_clarinet=True,
        )
        if index == chapter.CLARINET.unisono_part_index_tuple[-1]:
            add_last_phrase_hairpin(abjad_score)
        lilypond_file = AbjadScoreListToLilyPondFile().convert(
            [abjad_score], add_ekmelily=True, add_book_preamble=True
        )
        lilypond_file_path = f"{notation_file_path}_unisono_{index}.pdf"
        abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
        soprano_and_clarinet_unisono_file_path_list.append(lilypond_file_path)

    chapter_to_latex_document = cdd_converters.PDFChapterToLatexDocument()
    latex_document = chapter_to_latex_document.convert(chapter, instrument)

    latex_document.append(pylatex.NoEscape(chapter.CLARINET.instruction_text_sine))

    for index, sine_note in enumerate(chapter.CLARINET.sine_note_tuple):
        sequential_event = sine_note.get_sequential_event()
        add_sequential_event(
            sequential_event,
            f"sine_{index}",
            0.25,
            abjad_score_list_to_lilypond_file_class_kwargs={"x": 2.25},
        )

    latex_document.append(pylatex.NoEscape(chapter.CLARINET.instruction_text_glissando))

    for index, glissando_note in enumerate(chapter.CLARINET.glissando_note_tuple):
        sequential_event = glissando_note.get_sequential_event()
        add_sequential_event(
            sequential_event,
            f"glissando_{index}",
            0.25,
            abjad_score_list_to_lilypond_file_class_kwargs={"x": 2.25, "y": 1.25},
        )

    latex_document.append(pylatex.NoEscape(chapter.CLARINET.instruction_text_unisono))

    for lilypond_file_path in soprano_and_clarinet_unisono_file_path_list[:3]:
        add_pdf(lilypond_file_path, soprano_and_clarinet_unisono_width)

    latex_document.append(pylatex.NoEscape(chapter.CLARINET.instruction_text_slap))

    add_sequential_event(
        chapter.CLARINET.slap_long_note.get_sequential_event(),
        "slap",
        0.35,
        abjad_score_list_to_lilypond_file_class_kwargs={"y": 0.85, "x": 3},
    )

    latex_document.append(pylatex.NoEscape(chapter.CLARINET.instruction_text_unisono))

    for lilypond_file_path in soprano_and_clarinet_unisono_file_path_list[3:]:
        add_pdf(lilypond_file_path, soprano_and_clarinet_unisono_width)

    latex_document.generate_pdf(chapter.get_notation_path(instrument), clean_tex=True)


def notate_clavichord(chapter: cdd.chapters.Chapter):
    instrument = "clavichord"
    notation_file_path = chapter.get_notation_path(instrument)
    lilypond_file_path_base = f"{notation_file_path}_lilypond"
    x = 9
    abjad_score_list_to_lilypond_file_two = AbjadScoreListToFlexibleLilyPondFile(
        x=x, y=1.5
    )
    abjad_score_list_to_lilypond_file_empty = AbjadScoreListToFlexibleLilyPondFile(
        x=x, y=0.75
    )

    abjad_score_list = []
    is_rest_list = []

    for index, sequential_event, absolute_time_in_seconds in zip(
        range(len(chapter.CLAVICHORD.sequential_event_tuple)),
        chapter.clavichord_sequential_event_tuple,
        chapter.CLAVICHORD.sequential_event_absolute_time_tuple,
    ):
        tabulatura_sequential_event = (
            cdd.constants.CLAVICHORD_SEQUENTIAL_EVENT_TO_TABULATURA_BASED_EVENT(
                sequential_event
            )
        )

        simultaneous_event = (
            cdd_converters.SequentialEventToSplitSequentialEvent().convert(
                tabulatura_sequential_event
            )
        )

        abjad_score, is_rest = ClavichordSimultaneousEventToAbjadScore().convert(
            simultaneous_event,
            absolute_time_in_seconds,
        )
        abjad_score_list.append(abjad_score)
        is_rest_list.append(is_rest)

    last_not_rest = -list(reversed(is_rest_list)).index(False)
    abjad_score_list = abjad_score_list[:last_not_rest]

    # better to avoid bar lines, so it looks more as if it
    # would continue

    # for score in abjad_score_list:
    #     for staff in score[0]:
    #         last_leaf = abjad.get.leaf(staff, -1)
    #         cdd.utilities.add_last_bar_line(last_leaf, "|")

    # Show that song ends here
    for staff in abjad_score_list[-1][0]:
        last_leaf = abjad.get.leaf(staff, -1)
        cdd.utilities.add_last_bar_line(last_leaf)

    # We can remove all clefs for the scores after the first one
    # (because the clefs don't change and the music just continues)

    for score in abjad_score_list[1:]:
        score.remove_commands.append("System_start_delimiter_engraver")
        for piano_staff in score:
            piano_staff.remove_commands.append("Clef_engraver")
            piano_staff.remove_commands.append("System_start_delimiter_engraver")
            for staff in piano_staff:
                staff.remove_commands.append("Clef_engraver")

    lilypond_file_path_list = []
    for index, abjad_score in enumerate(abjad_score_list):
        is_rest = is_rest_list[index]
        if is_rest:
            abjad_score_list_to_lilypond_file = abjad_score_list_to_lilypond_file_empty
        else:
            abjad_score_list_to_lilypond_file = abjad_score_list_to_lilypond_file_two
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            # [abjad_score], add_ekmelily=False, add_book_preamble=True, margin=0
            [abjad_score],
            add_ekmelily=False,
            add_book_preamble=False,
            margin=0,
        )
        local_lilypond_file_path = f"{lilypond_file_path_base}_{index}.pdf"
        abjad.persist.as_pdf(lilypond_file, local_lilypond_file_path)

        lilypond_file_path_list.append(local_lilypond_file_path.split("/")[-1])

    chapter_to_latex_document = cdd_converters.ScoreListChapterToLatexDocument(
        lilypond_file_path_list,
        instruction_text=chapter.CLAVICHORD.instruction_text,
        # width=0.92,
        width=0.96,
        hspace="-0.0cm",
        vspace="0cm",
    )
    latex_document = chapter_to_latex_document.convert(chapter, instrument)
    latex_document.generate_pdf(notation_file_path, clean_tex=True)


def notate_noise(chapter: cdd.chapters.Chapter):
    instrument = "noise"
    notation_file_path = chapter.get_notation_path(instrument)
    table = tuple(
        (
            cdd_utilities.duration_in_seconds_to_readable_duration(absolute_time),
            chapter.NOISE.character,
        )
        for absolute_time in chapter.NOISE.absolute_time_tuple
    )

    latex_document = cdd_converters.TableChapterToLatexDocument(
        chapter.NOISE.instruction_text,
        table,
        instruction_text_after=chapter.NOISE.instruction_text_after,
    ).convert(chapter, instrument)
    latex_document.generate_pdf(notation_file_path, clean_tex=False)


def main(chapter: cdd.chapters.Chapter):
    notate_noise(chapter)
    notate_clarinet(chapter)
    notate_clavichord(chapter)
    notate_soprano(chapter)
