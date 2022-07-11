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
        # explicit  definition to avoid buildout having
        # version conflicts
        "numpy==1.22",
        # to fetch soundfile information (overkill, I admit)
        "pyo==1.0.4",
        # to split soundfiles
        "SoundFile>=0.10.3.post1",
        # to analyse soundfiles
        "librosa==0.9.2",
        # mutwo libs
        "mutwo.ext-core>=0.59.0, <0.60.0",
        "mutwo.ext-music>=0.16.0, <0.17.0",
        "mutwo.ext-midi>=0.7.0, <0.8.0",
        "mutwo.ext-abjad>=0.9.0, <0.10.0",
        "mutwo.ext-ekmelily>=0.6.0, <0.7.0",
        "mutwo.ext-isis>=0.7.0, <0.8.0",
        "mutwo.ext-csound>=0.4.0, <0.5.0",
        "mutwo.ext-mbrola==0.2.0",
        # for auto reading pessoa text from ebook
        "EbookLib==0.17.1",  # (this is for loading the html content of epub file)
        "beautifulsoup4==4.10.0",  # (this is to parse the content of the epub file)
        "lxml==4.8.0",  # (this is for beautiful soup)
        # for hyphenation of pessoa text (in order to create lyrics)
        "pyphen==0.12.0",
        # to pickle pitches
        "cloudpickle==2.0.0",
        # To create score papers
        "pylatex==1.4.1",
        # to write portugese numbers
        "num2words==0.5.10",
        # To convert csound jinja orchestras
        "jinja2>=3.1.2, <4.0.0",
    ],
    extras_require=extras_require,
    python_requires=">=3.9, <4",
)
