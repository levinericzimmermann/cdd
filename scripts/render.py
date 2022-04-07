import warnings


def render(render_method_list=["render_notation", "render_sound"]):
    import cdd

    for chapter_to_render_name in cdd.configurations.CHAPTER_TO_RENDER_TUPLE:
        try:
            chapter = getattr(cdd.content, str(chapter_to_render_name)).CHAPTER
        except AttributeError:
            warnings.warn(
                f"Can't find chapter: {chapter_to_render_name}.", RuntimeWarning
            )
        else:
            for render_method in render_method_list:
                getattr(chapter, render_method)()


if __name__ == "__main__":
    render()
