import typing

import abjad
import expenvelope

from mutwo import abjad_converters
from mutwo import cdd_converters
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
            mutwo_pitch_to_abjad_pitch_converter=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            # No need for dynamics here
            mutwo_volume_to_abjad_attachment_dynamic_converter=None,
            tempo_envelope_to_abjad_attachment_tempo_converter=None,
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
            sequential_event_to_quantized_abjad_container_converter=abjad_converters.RMakersSequentialEventToQuantizedAbjadContainer(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
            **kwargs,
        )

    def convert(
        self, event_to_convert, repetition_count: int, absolute_time_in_seconds: float
    ) -> abjad.Score:
        abjad_staff = super().convert(event_to_convert)
        start_time_markup = abjad.Markup(
            r"\typewriter { \smaller { start at "
            f"{cdd.utilities.duration_in_seconds_to_readable_duration(absolute_time_in_seconds)}"
            "} }",
            direction="up",
        )
        first_leaf = abjad.get.leaf(abjad_staff[0], 0)
        abjad.attach(start_time_markup, first_leaf)
        if repetition_count > 1:
            abjad.attach(abjad.Repeat(repeat_count=repetition_count), abjad_staff[0])
        abjad.attach(
            abjad.LilyPondLiteral(
                (
                    f"\\set Staff.instrumentName = \\markup {{ "
                    r" \normalsize { \caps {"
                    f"sing {repetition_count}x }} }}"
                    r"}"
                )
            ),
            first_leaf,
        )
        abjad_score = abjad.Score([abjad_staff])
        return abjad_score


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
            sequential_event_to_quantized_abjad_container_converter=abjad_converters.RMakersSequentialEventToDurationLineBasedQuantizedAbjadContainerConverter(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            ),
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

        readable_duration = cdd.utilities.duration_in_seconds_to_readable_duration(
            absolute_time_in_seconds
        )
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


class ClarinetPitchSetScoreListToLilyPondFile(
    cdd_converters.AbjadScoreListToLilyPondFile
):
    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_block.items.append(
            r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 1 in) (* 1 in))) paper-alist))
#(set-paper-size "my size")
"""
        )
        return paper_block


def notate_soprano(chapter: cdd.chapters.Chapter):
    instrument = "soprano"
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
        ).convert(soprano_sequential_event, repetition_count, absolute_time_in_seconds)
        for soprano_sequential_event, repetition_count, absolute_time_in_seconds in zip(
            chapter.soprano_sequential_event_tuple,
            chapter.soprano_repetition_count_tuple,
            chapter.soprano_sequential_event_absolute_time_tuple,
        )
    ]

    last_score = abjad_score_list[-1]

    for staff in last_score:
        first_leaf = abjad.get.leaf(staff, 0)
        abjad.attach(abjad.StartHairpin(">"), first_leaf)
        last_leaf = abjad.get.leaf(staff, -1)
        abjad.attach(abjad.StopHairpin(), last_leaf)
        cdd.utilities.add_last_bar_line(last_leaf)

    notation_file_path = chapter.get_notation_path(instrument)
    lilypond_file_path_base = f"{notation_file_path}_lilypond"
    lilypond_file_path_list = []
    for index, abjad_score in enumerate(abjad_score_list):
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [abjad_score], add_ekmelily=True, add_book_preamble=True, margin=0
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
    instrument = "clarinet"
    clarinet_sequential_event_to_abjad_score = ClarinetSequentialEventToAbjadScore()
    lilypond_file_and_width_list = [
        (
            ClarinetPitchSetScoreListToLilyPondFile().convert(
                [
                    clarinet_sequential_event_to_abjad_score.convert(
                        chapter.CLARINET.pedal_tone_sequential_event
                    )
                ],
                add_ekmelily=True,
                add_book_preamble=False,
                margin=0,
            ),
            0.15,
        )
    ]

    for hyperchromatic_index, hyperchromatic in enumerate(
        chapter.CLARINET.microtonal_movement_sequential_event_tuple
    ):
        cdd.utilities.add_cent_deviation_to_sequential_event(hyperchromatic)
        reversed_hyperchromatic = core_events.SequentialEvent(
            list(reversed(hyperchromatic.copy()))
        )
        notation_indicator_content = (
            r"\normalsize { \caps { hyperchromatic melody "
            f"no. {hyperchromatic_index + 1}"
        )
        if hyperchromatic_index == 0:
            notation_indicator_content += " (rhythm is free; can be varied)"
        notation_indicator_content += "} }"
        hyperchromatic[
            0
        ].notation_indicator_collection.rehearsal_mark.markup = abjad.Markup(
            notation_indicator_content
        )
        reversed_hyperchromatic[
            0
        ].notation_indicator_collection.margin_markup.content = (
            r"\normalsize { \caps { or } }"
        )
        for hyperchromatic_variant in (hyperchromatic, reversed_hyperchromatic):
            lilypond_file = AbjadScoreListToLilyPondFile().convert(
                clarinet_sequential_event_to_abjad_score.convert(
                    hyperchromatic_variant
                ),
                add_ekmelily=True,
                add_book_preamble=True,
                margin=0,
            )
            lilypond_file_and_width_list.append((lilypond_file, 1))

    notation_file_path = chapter.get_notation_path(instrument)
    lilypond_file_path_base = f"{notation_file_path}_lilypond"
    lilypond_file_path_to_width_dict = {}
    for index, lilypond_file_and_width in enumerate(lilypond_file_and_width_list):
        lilypond_file, width = lilypond_file_and_width
        lilypond_file_path = f"{lilypond_file_path_base}_{index}.pdf"
        abjad.persist.as_pdf(lilypond_file, lilypond_file_path)
        lilypond_file_path_to_width_dict.update(
            {lilypond_file_path.split("/")[-1]: width}
        )

    chapter_to_latex_document = cdd_converters.PreciseScoreListChapterToLatexDocument(
        lilypond_file_path_to_width_dict,
        instruction_text=chapter.CLARINET.instruction_text,
        width=0.25,
        # hspace="1.30cm",
    )
    latex_document = chapter_to_latex_document.convert(chapter, instrument)
    latex_document.generate_pdf(chapter.get_notation_path(instrument), clean_tex=True)


def notate_clavichord(chapter: cdd.chapters.Chapter):
    instrument = "clavichord"
    notation_file_path = chapter.get_notation_path(instrument)
    lilypond_file_path_base = f"{notation_file_path}_lilypond"
    abjad_score_list_to_lilypond_file = AbjadScoreListToLilyPondFile()

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

    for score in abjad_score_list:
        for staff in score[0]:
            last_leaf = abjad.get.leaf(staff, -1)
            cdd.utilities.add_last_bar_line(last_leaf, "|")

    for staff in abjad_score_list[-1][0]:
        last_leaf = abjad.get.leaf(staff, -1)
        cdd.utilities.add_last_bar_line(last_leaf)

    lilypond_file_path_list = []
    for index, abjad_score in enumerate(abjad_score_list):
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [abjad_score], add_ekmelily=False, add_book_preamble=True, margin=0
        )
        local_lilypond_file_path = f"{lilypond_file_path_base}_{index}.pdf"
        abjad.persist.as_pdf(lilypond_file, local_lilypond_file_path)

        lilypond_file_path_list.append(local_lilypond_file_path.split("/")[-1])

    chapter_to_latex_document = cdd_converters.ScoreListChapterToLatexDocument(
        lilypond_file_path_list,
        instruction_text=chapter.CLAVICHORD.instruction_text,
        width=0.92,
        hspace="-0.0cm",
        vspace="0.3cm",
    )
    latex_document = chapter_to_latex_document.convert(chapter, instrument)
    latex_document.generate_pdf(chapter.get_notation_path(instrument), clean_tex=False)


def main(chapter: cdd.chapters.Chapter):
    notate_clarinet(chapter)
    notate_clavichord(chapter)
    notate_soprano(chapter)
