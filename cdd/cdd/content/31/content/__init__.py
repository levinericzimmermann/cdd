__all__ = ("Chapter",)

import cdd

class Chapter(cdd.chapters.Chapter):
    from . import constants
    from . import bells

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bell_csound_sequential_event = self.bells.main(self)
