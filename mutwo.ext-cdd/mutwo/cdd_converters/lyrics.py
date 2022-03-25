import re

import pyphen

from mutwo import cdd_parameters
from mutwo import core_converters


__all__ = ("LyricsStringToLyrics",)


class LyricsStringToLyrics(core_converters.abc.Converter):
    def convert(
        self, lyrics_string: str, language_code: str = "pt"
    ) -> cdd_parameters.Lyrics:
        regex = re.compile(r'[^a-zA-Z\s?]')

        pyphen_dic = pyphen.Pyphen(lang=language_code)
        hyphen_string = "-"

        sentence_list = lyrics_string.split(".")
        lyrics = cdd_parameters.Lyrics([])
        for sentence in sentence_list:
            if sentence := regex.sub('', sentence):
                word_list = sentence.split(" ")
                sentence = cdd_parameters.Sentence([])
                for word in word_list:
                    if word:
                        sentence.append(
                            cdd_parameters.Word(
                                [
                                    cdd_parameters.Sylablle(sylablle)
                                    for sylablle in pyphen_dic.inserted(
                                        word, hyphen_string
                                    ).split(hyphen_string)
                                ]
                            )
                        )
                lyrics.append(sentence)
        return lyrics
