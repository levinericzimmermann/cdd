import os

# CHAPTER_TO_RENDER_TUPLE = ("6", "12", "60", "146")
# CHAPTER_TO_RENDER_TUPLE = ("146",)
CHAPTER_TO_RENDER_TUPLE = ("12",)
# CHAPTER_TO_RENDER_TUPLE = ("31",)


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
PATH.BUILDS.SCORES = "scores"
PATH.BUILDS.MIDI = "midi"
PATH.BUILDS.SOUND_FILES = "sound_files"
PATH.BUILDS.PICKLED = "pickled"
PATH.BUILDS.REAPER = "reaper"

PATH.CDD = "cdd"
PATH.CDD.DATA = "data"
PATH.CDD.DATA.FADO = "fado"
PATH.CDD.DATA.PESSOA = "pessoa"
PATH.CDD.DATA.PESSOA.BOOK = "Livro_do_Desassossego.epub"

PATH.ETC = "etc"
PATH.ETC.CSOUND = "csound"
PATH.ETC.ISIS = "isis"

PATH.WALKMAN = "walkman"
PATH.WALKMAN.TAPES = "tapes"

FORCE_TO_COMPUTE_FADO = False
FORCE_TO_COMPUTE_PESSOA = True


# IMPROVE_WESTERN_PITCH_LIST_ITERATION_COUNT = 150000
IMPROVE_WESTERN_PITCH_LIST_ITERATION_COUNT = 100

# del os, Path

RENDER_METHOD_LIST = ["render_notation", "render_sound"]
