import math
import typing

import abjad
import expenvelope
import quicktions as fractions

from mutwo import abjad_converters
from mutwo import core_converters
from mutwo import core_events
from mutwo import core_parameters
from mutwo import cdd_converters
from mutwo import music_events
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
    def __init__(
        self,
        *args,
        add_bar_line: bool = True,
        add_cent_deviation: bool = True,
        **kwargs,
    ):
        super().__init__(
            *args,
            mutwo_pitch_to_abjad_pitch=abjad_converters.MutwoPitchToHEJIAbjadPitch(),
            mutwo_volume_to_abjad_attachment_dynamic=None,
            mutwo_lyric_to_abjad_string=MutwoLyricToAbjadString(),
            **kwargs,
        )
        self._add_bar_line = add_bar_line
        self._add_cent_deviation = add_cent_deviation

    def convert(
        self, event_to_convert: core_events.SequentialEvent, *args, **kwargs
    ) -> abjad.Staff:
        if self._add_cent_deviation:
            cdd.utilities.add_cent_deviation_to_sequential_event(event_to_convert)
        voice = super().convert(event_to_convert, *args, **kwargs)
        process_espressivo(voice)
        if voice:
            first_leaf = abjad.get.leaf(voice, 0)
            abjad.attach(
                abjad.LilyPondLiteral((r'\accidentalStyle "dodecaphonic" ')),
                first_leaf,
            )
            last_leaf = abjad.get.leaf(voice, -1)

            if self._add_bar_line:
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
        time_signature_sequence: typing.Sequence = [abjad.TimeSignature((4, 4))],
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

    def convert(self, *args, **kwargs):
        staff = super().convert(*args, **kwargs)
        first_leaf = abjad.get.leaf(staff, 0)
        abjad.attach(
            abjad.LilyPondLiteral(
                (
                    # r"\omit Staff.BarLine "
                    r"\override Score.BarLine.transparent = ##t "
                    r"\set Score.proportionalNotationDuration = #(ly:make-moment 1/4) "
                )
            ),
            first_leaf,
        )
        staff.remove_commands.append("Time_signature_engraver")
        return staff


class SustainingSequentialEventToStaff(SequentialEventToDurationLineBasedStaff):
    def convert(self, *args, **kwargs):
        staff = super().convert(*args, **kwargs)
        return staff


class EnvironmentSequentialEventToStaff(SequentialEventToDurationLineBasedStaff):
    def convert(self, *args, **kwargs):
        staff = super().convert(*args, **kwargs)
        voice = staff[0]
        # no duration line engraver
        del voice.consists_commands[0]
        return staff


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

    def convert(self, sequential_event: core_events.SequentialEvent, *args, **kwargs):
        note_head_style = "petrucci"
        is_first = True
        for note_like in sequential_event:
            if hasattr(note_like, "notation_indicator_collection"):
                if is_first:
                    if not note_like.notation_indicator_collection.note_head.style:
                        note_like.notation_indicator_collection.note_head.style = (
                            note_head_style
                        )
                    is_first = False
                note_like.notation_indicator_collection.note_head.default_style = (
                    note_head_style
                )

        staff = super().convert(sequential_event, *args, **kwargs)
        first_leaf = abjad.get.leaf(staff, 0)
        abjad.attach(
            abjad.LilyPondLiteral(
                (
                    r"\numericTimeSignature "
                    r"\override Staff.TimeSignature.style = #'single-digit "
                    # r'\override Staff.BarLine.glyph = "!" '  # doesn't work :(
                    r"\override Staff.BarLine.hair-thickness = #0.1 "
                )
            ),
            first_leaf,
        )
        return staff


class SequentialEventToRhythmicStaff(SequentialEventToRhythmBasedStaff):
    def convert(self, *args, **kwargs):
        staff = super().convert(*args, **kwargs)
        staff.lilypond_type = "RhythmicStaff"
        return staff


class SopranoSequentialEventToAbjadStaff(SequentialEventToDurationLineBasedStaff):
    pass


class ClarinetSequentialEventToAbjadStaff(SequentialEventToDurationLineBasedStaff):
    pass


class ClavichordSequentialEventToAbjadStaff(SequentialEventToRhythmBasedStaff):
    pass


class ClavichordSequentialEventToAbjadStaffGroup(core_converters.abc.Converter):
    def __init__(
        self,
        *args,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
        **kwargs,
    ):
        self.sequential_event_to_abjad_staff = ClavichordSequentialEventToAbjadStaff(
            *args,
            time_signature_sequence=time_signature_sequence,
            tempo_envelope=tempo_envelope,
            add_cent_deviation=False,
            add_bar_line=False,
            **kwargs,
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


class MetronomeSimultaneousEventToAbjadStaffGroup(core_converters.abc.Converter):
    def __init__(
        self,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
    ):
        self.sequential_event_to_rhythmic_staff = SequentialEventToRhythmicStaff(
            time_signature_sequence=time_signature_sequence,
            tempo_envelope=tempo_envelope,
        )

    def convert(
        self, simultaneous_event_to_convert: core_events.SimultaneousEvent
    ) -> abjad.StaffGroup:
        staff_group = abjad.StaffGroup([], tag=abjad.Tag("tape-metronome"))
        for sequential_event in simultaneous_event_to_convert:
            staff_group.append(
                self.sequential_event_to_rhythmic_staff(sequential_event)
            )
        return staff_group


class ClavichordAndMetronomeToAbjadScore(core_converters.abc.Converter):
    def __init__(
        self,
        time_signature_sequence: typing.Sequence = [],
        tempo_envelope: expenvelope.Envelope = expenvelope.Envelope.from_points(
            [2, core_parameters.TempoPoint(60)]
        ),
    ):
        self.metronome_sequential_event_to_abjad_staff = SequentialEventToRhythmicStaff(
            time_signature_sequence=time_signature_sequence,
            tempo_envelope=tempo_envelope,
        )
        # self.metronome_simultaneous_event_to_abjad_staff_group = (
        #     MetronomeSimultaneousEventToAbjadStaffGroup(
        #         time_signature_sequence=time_signature_sequence,
        #         tempo_envelope=tempo_envelope,
        #     )
        # )
        self.clavichord_sequential_event_to_abjad_staff_group = (
            ClavichordSequentialEventToAbjadStaffGroup(
                time_signature_sequence=time_signature_sequence,
                tempo_envelope=tempo_envelope,
            )
        )

    def convert(
        self,
        clavichord_sequential_event: core_events.SequentialEvent,
        # metronome_simultaneous_event: core_events.SimultaneousEvent,
        metronome_sequential_event: core_events.SequentialEvent,
        *args,
        **kwargs,
    ) -> abjad.Score:
        abjad_score = abjad.Score(
            [
                # self.metronome_simultaneous_event_to_abjad_staff_group(
                #     metronome_simultaneous_event
                # ),
                self.metronome_sequential_event_to_abjad_staff(
                    metronome_sequential_event
                ),
                self.clavichord_sequential_event_to_abjad_staff_group(
                    clavichord_sequential_event
                ),
            ]
        )

        for metronome_staff in abjad_score[0]:
            first_metronome_leaf = abjad.get.leaf(metronome_staff, 0)
            abjad.attach(
                abjad.LilyPondLiteral("\\magnifyStaff #(magstep -3.5)"),
                first_metronome_leaf,
            )

        for abjad_staff_or_abjad_staff_group, instrument_name_tuple in zip(
            abjad_score, (("tape", "t."), ("clavichord", "c."))
        ):
            sequential_event = core_events.SequentialEvent([])
            (
                sequential_event.instrument_name,
                sequential_event.short_instrument_name,
            ) = instrument_name_tuple
            abjad_converters.AddInstrumentName(
                instrument_name_font_size=r"small \typewriter",
                short_instrument_name_font_size=r"small \typewriter",
            )(sequential_event, abjad_staff_or_abjad_staff_group)
        return abjad_score


class ClavichordTimeBracketToAbjadScore(core_converters.abc.Converter):
    def convert(
        self,
        clavichord_time_bracket,
    ) -> abjad.Score:
        clavichord_sequential_event = (
            clavichord_time_bracket.get_sequential_event().copy()
        )

        time_signature_sequence = clavichord_time_bracket.time_signature_sequence

        repetition_count = getattr(clavichord_sequential_event, "repetition_count", 0)
        if repetition_count > 0:
            clavichord_sequential_event = clavichord_sequential_event[:1]
            clavichord_sequential_event[
                0
            ].notation_indicator_collection.markup.content = (
                r"\normalsize { play " f"{repetition_count}x " "}"
            )
            clavichord_sequential_event[
                0
            ].notation_indicator_collection.markup.direction = "up"
            duration = fractions.Fraction(clavichord_sequential_event.duration)
            time_signature_sequence = (
                abjad.TimeSignature((duration.numerator, duration.denominator)),
            )

        clavichord_sequential_event_to_abjad_staff_group_kwargs = {
            "tempo_envelope": clavichord_time_bracket.tempo_envelope,
            "time_signature_sequence": time_signature_sequence,
        }
        if len(clavichord_sequential_event) < 2 and repetition_count < 1:
            clavichord_sequential_event_to_abjad_staff_group_kwargs.update(
                {"tempo_envelope_to_abjad_attachment_tempo": None}
            )
        clavichord_sequential_event_to_abjad_staff_group = (
            ClavichordSequentialEventToAbjadStaffGroup(
                **clavichord_sequential_event_to_abjad_staff_group_kwargs
            )
        )

        abjad_staff_group = clavichord_sequential_event_to_abjad_staff_group(
            clavichord_sequential_event
        )
        for index, abjad_staff in enumerate(abjad_staff_group):
            first_leaf = abjad.get.leaf(abjad_staff, 0)
            abjad.attach(
                abjad.LilyPondLiteral(r"\set PianoStaff.connectArpeggios = ##t"),
                first_leaf,
            )
            selection = abjad.select(abjad_staff)
            if not selection.notes() and not selection.chords():
                del abjad_staff_group[index]
            else:
                if not clavichord_time_bracket.notate_metronome:
                    abjad_staff.remove_commands.append("Time_signature_engraver")
                if repetition_count > 0:
                    # first_leaf = abjad.get.leaf(abjad_staff, 0)
                    abjad.attach(abjad.Repeat(), abjad_staff)
        # first_leaf = abjad.get.leaf(abjad_staff, 0)
        # abjad.attach(abjad.LilyPondLiteral(r'\omit TimeSignature

        cdd_converters.AddTimeBracketMarks(clavichord_time_bracket.start_time, None)(
            None, abjad_staff_group[0]
        )

        abjad_score = abjad.Score([abjad_staff_group])
        if clavichord_time_bracket.notate_metronome:
            metronome_sequential_event_to_abjad_staff = SequentialEventToRhythmicStaff(
                **clavichord_sequential_event_to_abjad_staff_group_kwargs
            )
            metronome_sequential_event = (
                clavichord_time_bracket.metronome_sequential_event
            )
            metronome_staff_group = metronome_sequential_event_to_abjad_staff.convert(
                metronome_sequential_event
            )
            abjad_score.insert(0, metronome_staff_group)

            for abjad_staff_or_abjad_staff_group, instrument_name_tuple in zip(
                abjad_score, (("tape", "t."), ("clavichord", "c."))
            ):
                sequential_event = core_events.SequentialEvent([])
                (
                    sequential_event.instrument_name,
                    sequential_event.short_instrument_name,
                ) = instrument_name_tuple
                abjad_converters.AddInstrumentName(
                    instrument_name_font_size=r"small \typewriter",
                    short_instrument_name_font_size=r"small \typewriter",
                )(sequential_event, abjad_staff_or_abjad_staff_group)

        return abjad_score


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


class SustainingInstrumentDataToAbjadScore(core_converters.abc.Converter):
    def __init__(self):
        self.sustaining_sequential_event_to_abjad_staff = (
            SustainingSequentialEventToStaff(
                tempo_envelope_to_abjad_attachment_tempo=None, add_bar_line=False
            )
        )
        self.environment_sequential_event_to_abjad_staff = (
            EnvironmentSequentialEventToStaff(
                add_cent_deviation=False,
                tempo_envelope_to_abjad_attachment_tempo=None,
                add_bar_line=False,
            )
        )

    def convert(
        self,
        sustaining_instrument_data: tuple[
            float,
            float,
            core_events.SequentialEvent,  # sustaining instrument
            core_events.SequentialEvent,  # environment
            bool,
        ],
        instrument_name: str,
    ) -> abjad.Score:
        (
            start,
            end,
            sustaining_sequential_event,
            environment_sequential_event,
            does_next_event_follows_immediately,
        ) = sustaining_instrument_data

        sustaining_sequential_event = sustaining_sequential_event.copy()
        environment_sequential_event = environment_sequential_event.copy()

        # if does_next_event_follows_immediately:
        #     end_style = "arrow"
        # else:
        #     end_style = "hook"
        # sustaining_sequential_event[
        #     -1
        # ].notation_indicator_collection.duration_line.end_style = end_style
        # sustaining_sequential_event[
        #     -1
        # ].notation_indicator_collection.duration_line.hook_direction = "DOWN"

        for sequential_event in (
            sustaining_sequential_event,
            environment_sequential_event,
        ):
            hidden_note_rest = music_events.NoteLike("c", fractions.Fraction(1, 4))
            hidden_note_rest.notation_indicator_collection.duration_line.style = "none"
            sequential_event.append(hidden_note_rest)

            # rest = music_events.NoteLike([], fractions.Fraction(1, 64))
            # sequential_event.append(rest)

        ts0_duration = fractions.Fraction(2, 1)

        remaining_duration = sequential_event.duration - ts0_duration

        time_signature_sequence = [
            abjad.TimeSignature(
                (
                    ts0_duration.numerator,
                    ts0_duration.denominator,
                )
            ),
            abjad.TimeSignature(
                (
                    remaining_duration.numerator,
                    remaining_duration.denominator,
                )
            ),
        ]

        # time_signature_sequence = [
        #     abjad.TimeSignature(
        #         (
        #             sequential_event.duration.numerator,
        #             sequential_event.duration.denominator,
        #         )
        #     ),
        # ]

        for sequential_event_to_abjad_staff in (
            self.sustaining_sequential_event_to_abjad_staff,
            self.environment_sequential_event_to_abjad_staff,
        ):
            sequential_event_to_abjad_staff._sequential_event_to_quantized_abjad_container._time_signature_tuple = tuple(
                time_signature_sequence
            )

        if instrument_name == cdd.constants.CLARINET:
            sustaining_sequential_event = (
                cdd.utilities.clarinet_event_to_notatable_clarinet_event(
                    sustaining_sequential_event
                )
            )

        sustaining_abjad_staff = self.sustaining_sequential_event_to_abjad_staff(
            sustaining_sequential_event
        )

        environment_abjad_staff = self.environment_sequential_event_to_abjad_staff(
            environment_sequential_event
        )

        # for staff in (sustaining_abjad_staff, environment_abjad_staff):
        #     staff.append(abjad.Rest(fractions.Fraction(1, 32)))

        process_espressivo(sustaining_abjad_staff[0])
        last_leaf = abjad.get.leaf(sustaining_abjad_staff, -1)
        abjad.attach(abjad.StopHairpin(), last_leaf)

        cdd_converters.AddTimeBracketMarks(start, end)(None, sustaining_abjad_staff)

        first_environment_leaf = abjad.get.leaf(environment_abjad_staff, 0)
        first_sustaining_leaf = sustaining_abjad_staff[0][0][0]

        if does_next_event_follows_immediately:
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"^ \markup { \hspace #12 "
                    r"\draw-line #'(25 . 0) "
                    r"\hspace #-0.75 "
                    r"\arrow-head #X #RIGHT ##t }",
                ),
                first_sustaining_leaf,
            )

        if abjad.get.before_grace_container(first_sustaining_leaf):
            grace_note_container = abjad.BeforeGraceContainer("c''4")
            abjad.attach(grace_note_container, first_environment_leaf)
            first_environment_leaf = grace_note_container[0]
            abjad.attach(
                abjad.LilyPondLiteral(
                    r"\hideNotes",
                ),
                first_environment_leaf,
            )
            abjad.attach(
                abjad.LilyPondLiteral(r"\unHideNotes", format_slot="after"),
                first_environment_leaf,
            )

        abjad.attach(
            abjad.LilyPondLiteral("\\magnifyStaff #(magstep -3.5)"),
            first_environment_leaf,
        )
        abjad_score = abjad.Score(
            [
                sustaining_abjad_staff,
                environment_abjad_staff,
            ]
        )

        for staff in abjad_score:
            last_leaf = abjad.select(staff).notes()[-1]
            abjad.attach(abjad.LilyPondLiteral(r"\hideNotes"), last_leaf)
            abjad.attach(abjad.TimeSignature((9, 4)), abjad.get.leaf(staff[0][1], 0))
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


class SustainingInstrumentScoreListToLilyPondFile(
    cdd_converters.AbjadScoreListToLilyPondFile
):
    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_size = r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 4 in) (* 1.5 in))) paper-alist))
#(set-paper-size "my size")
system-system-spacing = #'((basic-distance . 7.5) (padding . 0))
"""
        paper_block.items.append(paper_size)
        return paper_block


class ClavichordInstrumentScoreListToLilyPondFileSmall(
    cdd_converters.AbjadScoreListToLilyPondFile
):
    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_size = r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 2 in) (* 2 in))) paper-alist))
#(set-paper-size "my size")
system-system-spacing = #'((basic-distance . 7.5) (padding . 0))
"""
        paper_block.items.append(paper_size)
        return paper_block


class ClavichordInstrumentScoreListToLilyPondFileBig(
    cdd_converters.AbjadScoreListToLilyPondFile
):
    def get_paper_block(self, *args, **kwargs) -> abjad.Block:
        paper_block = super().get_paper_block(*args, **kwargs)
        paper_size = r"""
#(set! paper-alist
  (cons '("my size" . (cons (* 9 in) (* 4.35 in))) paper-alist))
#(set-paper-size "my size")
system-system-spacing = #'((basic-distance . 0) (padding . 0))
"""
        paper_block.items.append(paper_size)
        return paper_block


def process_espressivo(abjad_voice: abjad.Voice):
    leaves = abjad.select(abjad_voice).leaves()
    start = None
    espressivo_list = []
    for index, leaf in enumerate(leaves):
        if start is not None and not [
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
            start = index

    if start is not None:
        espressivo_list.append((start, len(leaves) - 1))

    for start, end in espressivo_list:
        span = end - start
        center = int(math.ceil(span / 2) + start)
        # # This is a hack and only valid for staves with only one event
        # if start != 0:
        #     start = 0
        #     center += 1
        start_leaf = leaves[start]
        center_leaf = leaves[center]
        abjad.attach(
            abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t"),
            start_leaf,
        )
        abjad.attach(abjad.StartHairpin("<"), start_leaf)
        abjad.attach(
            abjad.LilyPondLiteral(r"\once \override Hairpin.circled-tip = ##t"),
            center_leaf,
        )
        abjad.attach(abjad.StartHairpin(">"), center_leaf)


def _notate_sustaining_instrument(chapter: cdd.chapters.Chapter, instrument_name: str):
    notation_file_path = chapter.get_notation_path(instrument_name)
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    sustaining_instrument_data_to_abjad_score = SustainingInstrumentDataToAbjadScore()
    abjad_score_list = [
        sustaining_instrument_data_to_abjad_score(
            sustaining_instrument_data, instrument_name
        )
        for sustaining_instrument_data in chapter.sustaining_instrument_dict[
            instrument_name
        ]
    ]
    abjad_score_list_to_lilypond_file = SustainingInstrumentScoreListToLilyPondFile()

    lilypond_file_path_list = []
    for score_index, abjad_score in enumerate(abjad_score_list):
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [abjad_score],
            add_ekmelily=True,
            add_fancy_glissando=True,
            # add_book_preamble=True,
            add_book_preamble=False,
            margin=0,
        )
        local_lilypond_file_path = f"{lilypond_file_path}_{score_index}.pdf"
        abjad.persist.as_pdf(lilypond_file, local_lilypond_file_path)
        lilypond_file_path_list.append(local_lilypond_file_path.split("/")[-1])

    chapter_to_latex_document = cdd_converters.ScoreListChapterToLatexDocument(
        lilypond_file_path_list,
        instruction_text=chapter.instrument_name_to_instruction_text[instrument_name],
        width=0.5,
        # hspace="-0.8cm",
        hspace="0.0cm",
        vspace="0.1cm",
    )

    latex_document = chapter_to_latex_document.convert(chapter, instrument_name)
    latex_document.generate_pdf(notation_file_path, clean_tex=True)


def notate_soprano(chapter: cdd.chapters.Chapter):
    _notate_sustaining_instrument(chapter, cdd.constants.SOPRANO)


def notate_clarinet(chapter: cdd.chapters.Chapter):
    _notate_sustaining_instrument(chapter, cdd.constants.CLARINET)


def notate_clavichord(chapter: cdd.chapters.Chapter):
    instrument_name = "clavichord"
    notation_file_path = chapter.get_notation_path(instrument_name)
    lilypond_file_path = f"{notation_file_path}_lilypond.pdf"
    abjad_score_list = [
        ClavichordTimeBracketToAbjadScore()(clavichord_time_bracket)
        for clavichord_time_bracket in chapter.clavichord_time_bracket_container
    ]
    abjad_score_list_to_lilypond_file_small = (
        ClavichordInstrumentScoreListToLilyPondFileSmall()
    )
    abjad_score_list_to_lilypond_file_big = (
        ClavichordInstrumentScoreListToLilyPondFileBig()
    )
    lilypond_file_path_list = []
    for score_index, clavichord_time_bracket, abjad_score in zip(
        range(len(abjad_score_list)),
        chapter.clavichord_time_bracket_container,
        abjad_score_list,
    ):
        if clavichord_time_bracket.notate_metronome:
            abjad_score_list_to_lilypond_file = abjad_score_list_to_lilypond_file_big
            width = 0.95
            margin = 13
            dynamic_change_indication = abjad.StartTextSpan(
                left_text=abjad.Markup("rit.")
            )

            for staff_group in abjad_score:
                for staff in staff_group:
                    first_leaf = abjad.get.leaf(staff, 0)
                    last_leaf = abjad.get.leaf(staff, -1)
                    abjad.attach(dynamic_change_indication, first_leaf)
                    abjad.attach(abjad.StopTextSpan(), last_leaf)
        else:
            abjad_score_list_to_lilypond_file = abjad_score_list_to_lilypond_file_small
            width = 0.25
            margin = 0
        lilypond_file = abjad_score_list_to_lilypond_file.convert(
            [abjad_score],
            add_ekmelily=False,
            # add_book_preamble=True,
            add_book_preamble=False,
            margin=margin,
        )
        local_lilypond_file_path = f"{lilypond_file_path}_{score_index}.pdf"
        abjad.persist.as_pdf(lilypond_file, local_lilypond_file_path)
        formated_local_lilypond_file_path = local_lilypond_file_path.split("/")[-1]
        lilypond_file_path_list.append(
            (formated_local_lilypond_file_path, float(width))
        )

    chapter_to_latex_document = cdd_converters.ScoreListChapterToLatexDocument(
        lilypond_file_path_list,
        instruction_text=chapter.instrument_name_to_instruction_text[instrument_name],
        width=0.25,
        hspace="0.0cm",
        vspace="-0.2cm",
    )

    latex_document = chapter_to_latex_document.convert(chapter, instrument_name)
    latex_document.generate_pdf(notation_file_path, clean_tex=True)


def notate_noise(chapter: cdd.chapters.Chapter):
    pass


def main(chapter: cdd.chapters.Chapter):
    # notate_soprano(chapter)
    # notate_clarinet(chapter)
    notate_clavichord(chapter)
