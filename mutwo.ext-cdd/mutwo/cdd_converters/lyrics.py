import re

import pyphen

from mutwo import cdd_parameters
from mutwo import core_converters
from mutwo import music_parameters


__all__ = ("LyricsStringToLyrics",)


class LyricsStringToLyrics(core_converters.abc.Converter):
    def _add_sentence_string(
        self,
        lyric: cdd_parameters.NestedLanguageBasedLyric,
        sentence_string: str,
        punctuation: str,
        pyphen_dic,
    ):
        regex_latin_letter = re.compile(r"[^a-zA-Z\s?]")
        hyphen_string = "-"
        if letter_only_sentence_string := regex_latin_letter.sub("", sentence_string):
            word_list = letter_only_sentence_string.split(" ")
            sentence = cdd_parameters.Sentence([], punctuation)
            for word in filter(bool, word_list):
                syllable_list = []
                syllable_string_list = pyphen_dic.inserted(word, hyphen_string).split(
                    hyphen_string
                )
                is_last_syllable = True
                for syllable in reversed(syllable_string_list):
                    syllable_list.append(
                        music_parameters.LanguageBasedSyllable(
                            is_last_syllable, syllable
                        )
                    )
                    is_last_syllable = False
                if syllable_list:
                    sentence.append(cdd_parameters.Word(list(reversed(syllable_list))))
            lyric.append(sentence)

    def convert(
        self, lyrics_string: str, language_code: str = "pt"
    ) -> cdd_parameters.NestedLanguageBasedLyric:
        regex_punctuation = re.compile(r"[\?\.\!\…]")

        pyphen_dic = pyphen.Pyphen(lang=language_code)

        lyric = cdd_parameters.NestedLanguageBasedLyric([])
        index = 0
        for match in re.finditer(regex_punctuation, lyrics_string):
            sentence_string = lyrics_string[index : match.start()]
            index = match.end()
            punctuation = match.group()
            self._add_sentence_string(lyric, sentence_string, punctuation, pyphen_dic)
        lyric_count = len(lyric)
        if lyric_count > index:
            self._add_sentence_string(lyric, lyrics_string[index:], ".", pyphen_dic)
        return lyric
