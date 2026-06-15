"""Test sphinxcontrib.video extension."""

from logging import Logger

import pytest
from bs4 import BeautifulSoup, formatter

from sphinxcontrib.video import validate_figwidth

logger = Logger("sphinxcontrib.video.tests.test_build")

fmt = formatter.HTMLFormatter(indent=2, void_element_close_prefix=" /")


@pytest.mark.sphinx("latex", testroot="video")
def test_video_latex(app, status, warning, file_regression):
    """Build a latex output (unsupported)."""
    app.builder.build_all()

    assert "unsupported output format (node skipped)" in warning.getvalue()


@pytest.mark.sphinx(testroot="video")
def test_video(app, status, warning, file_regression):
    """Build a video without options."""
    app.builder.build_specific([app.srcdir / "mp4.rst"])

    html = (app.outdir / "mp4.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video")
def test_video_options(app, status, warning, file_regression):
    """Build a video without all options activated."""
    app.builder.build_specific([app.srcdir / "mp4_options.rst"])

    html = (app.outdir / "mp4_options.html").read_text(encoding="utf8")
    print(html)
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0]
    video.attrs["controlslist"] = " ".join(sorted(video.attrs["controlslist"].split()))
    video = video.prettify(formatter=fmt)
    file_regression.check(video, basename="video_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings")
def test_wrong_format(app, status, warning, file_regression):
    """Build a video with  a non supported format and check the error message."""
    app.builder.build_specific([app.srcdir / "wrong_format.rst"])

    assert (
        'The provided file type (".mkv") is not a supported format. defaulting to ""'
        in warning.getvalue()
    )

    # test the video is still existing
    html = (app.outdir / "wrong_format.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_wrong_format", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings")
def test_wrong_height(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_height.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_height.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings")
def test_wrong_width(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_width.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_width.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings")
def test_wrong_preload(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_preload.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_preload.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings")
def test_wrong_controlslist(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_controlslist.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_controlslist.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-secondary")
def test_video_force_secondary(app, status, warning, file_regression):
    """Build a latex output (unsuported)."""
    app.builder.build_specific([app.srcdir / "mp4_secondary.rst"])

    assert (
        'A secondary source should be provided for "_static/video.mp4"'
        in warning.getvalue()
    )

    html = (app.outdir / "mp4_secondary.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_secondary", extension=".html")


# ── figwidth validation ───────────────────────────────────────────────────────


@pytest.mark.parametrize(
    "value,expected",
    [
        # Valid values
        ("640px", True),
        ("50%", True),
        ("10em", True),
        ("1rem", True),
        ("12pt", True),
        ("100pc", True),
        ("2in", True),
        ("5cm", True),
        ("10mm", True),
        ("0px", True),
        (" 640px ", True),  # whitespace stripped
        # Invalid values
        ("", False),  # empty
        ("640", False),  # no unit
        ("-10px", False),  # negative
        ("10.5em", False),  # float
        ("100%; color: red", False),  # semicolon / CSS injection
        ("calc(100%)", False),  # CSS function with parentheses
        ("100'px", False),  # single quote
        ('100"px', False),  # double quote
        ("10px 20px", False),  # compound expression
        ("expression(alert(1))", False),  # XSS attempt
        ("100% ", True),  # trailing whitespace stripped → valid
        (": 100px", False),  # colon prefix
        ("100px;", False),  # trailing semicolon
        ("rgb(0,0,0)", False),  # CSS function
        ("auto", False),  # keyword not a length
        ("inherit", False),  # keyword not a length
    ],
)
def test_validate_figwidth(value, expected):
    """Unit-test the figwidth validator for safe and unsafe values."""
    assert validate_figwidth(value) == expected


@pytest.mark.sphinx(testroot="video")
def test_valid_figwidth(app, status, warning):
    """Valid figwidth with caption should produce a style attribute on the figure."""
    app.builder.build_specific([app.srcdir / "mp4_caption_figwidth.rst"])

    html = (app.outdir / "mp4_caption_figwidth.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    figure = soup.select("figure")[0]
    assert figure.get("style") == "width: 640px"
    # No warning should be emitted for a valid figwidth
    assert "figwidth" not in warning.getvalue().lower()


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_invalid_figwidth(app, status, warning):
    """Invalid figwidth should be warned and ignored (no style in output)."""
    app.builder.build_specific([app.srcdir / "wrong_figwidth.rst"])

    # A warning mentioning figwidth must be present
    assert "figwidth" in warning.getvalue().lower()

    html = (app.outdir / "wrong_figwidth.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    figure = soup.select("figure")[0]
    # figwidth was rejected → no style attribute on the figure
    assert "style" not in figure.attrs


@pytest.mark.sphinx(testroot="video")
def test_figwidth_no_caption(app, status, warning):
    """figwidth without caption should be silently ignored (no style output)."""
    app.builder.build_specific([app.srcdir / "mp4_figwidth_no_caption.rst"])

    html = (app.outdir / "mp4_figwidth_no_caption.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    container = soup.select("div.sphinx-contrib-video-container")[0]
    # No figure (no caption) and no style attribute
    assert "style" not in container.attrs
    assert soup.select("figure") == []
    # No warning should be emitted — figwidth is simply ignored without caption
    assert "figwidth" not in warning.getvalue().lower()


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_width_height_validation_unchanged(app, status, warning, file_regression):
    """Confirm existing width/height validation is not loosened."""
    # wrong_width still produces a warning and renders without width
    app.builder.build_specific([app.srcdir / "wrong_width.rst"])
    assert "width" in warning.getvalue().lower()

    html = (app.outdir / "wrong_width.html").read_text(encoding="utf8")
    soup = BeautifulSoup(html, "html.parser")
    video = soup.select("video")[0]
    assert "width" not in video.attrs
