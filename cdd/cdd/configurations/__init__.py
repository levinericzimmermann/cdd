import os

CHAPTER_TO_RENDER_TUPLE = tuple([])

class Path(str):
    def __setattr__(self, path_name: str, path: str):
        path = f"{str(self)}/{path}"
        try:
            os.mkdir(path)
        except FileExistsError:
            pass
        super().__setattr__(path_name, type(self)(path))


PATH = Path(".")

PATH.BUILDS = "builds"

PATH.BUILDS.ILLUSTRATIONS = "illustrations"
PATH.BUILDS.NOTATIONS = "notations"
PATH.BUILDS.MIDI = "midi"
PATH.BUILDS.SOUND_FILES = "sound_files"

PATH.CDD = "cdd"
PATH.CDD.DATA = "data"
PATH.CDD.DATA.FADO = "fado"
PATH.CDD.DATA.PESSOA = "pessoa"
PATH.CDD.DATA.PESSOA.BOOK = "Livro_do_Desassossego.epub"


del os, Path
