import setuptools  # type: ignore


with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

extras_require = {"testing": ["nose", "coveralls"]}

setuptools.setup(
    name="mutwo.ext-cdd",
    version="0.1.0",
    license="GPL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Levin Eric Zimmermann",
    author_email="levin.eric.zimmermann@posteo.eu",
    packages=[
        package
        for package in setuptools.find_namespace_packages(include=["mutwo.*"])
        if package[:5] != "tests"
    ],
    setup_requires=[],
    install_requires=[
        "mutwo.ext-core>=0.59.0, <0.60.0",
        "mutwo.ext-music>=0.13.0, <1.0.0",
        "mutwo.ext-midi>=0.7.0, <0.8.0",
        "mutwo.ext-abjad>=0.6.0, <0.7.0",
        "mutwo.ext-ekmelily>=0.5.0, <0.6.0",
        "mutwo.ext-isis>=0.7.0, <0.8.0",
        # for auto reading pessoa text from ebook
        "EbookLib==0.17.1",  # (this is for loading the html content of epub file)
        "beautifulsoup4==4.10.0",  # (this is to parse the content of the epub file)
        "lxml==4.8.0",  # (this is for beautiful soup)
        # for hyphenation of pessoa text (in order to create lyrics)
        "pyphen==0.12.0",
        # to pickle pitches
        "cloudpickle==2.0.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
