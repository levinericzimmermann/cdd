import cdd

for chapter, content in cdd.constants.CHAPTER_TO_LYRICS_DICT.items():
    print(chapter)
    print(repr(content))
    print(content)
    print('')
