"""Test sphinxcontrib.video extension."""

from logging import Logger

import pytest
from bs4 import BeautifulSoup, formatter

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


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
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


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_wrong_height(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_height.rst"])

    assert 'The provided height ("12em") is ignored' in warning.getvalue()

    # test the video is still existing
    html = (app.outdir / "wrong_height.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_wrong_width(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_width.rst"])

    assert 'The provided width ("12em") is ignored' in warning.getvalue()

    # test the video is still existing
    html = (app.outdir / "wrong_width.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_wrong_preload(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_preload.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_preload.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_wrong_controlslist(app, status, warning, file_regression):
    """Build a video with badly designed option and check it's ignored."""
    app.builder.build_specific([app.srcdir / "wrong_controlslist.rst"])

    # test the video is still existing
    html = (app.outdir / "wrong_controlslist.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_px_dimensions(app, status, warning):
    """Build a video with valid decimal px dimensions and verify they render correctly."""
    app.builder.build_specific([app.srcdir / "px_dimensions.rst"])

    html = (app.outdir / "px_dimensions.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0]
    assert video.attrs["width"] == "640.5px"
    assert video.attrs["height"] == "320.25px"


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_negative_px_width(app, status, warning, file_regression):
    """Build a video with negative px width and check it's rejected."""
    app.builder.build_specific([app.srcdir / "negative_px_width.rst"])

    assert 'The provided width ("-5px") is ignored' in warning.getvalue()

    html = (app.outdir / "negative_px_width.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_negative_px_height(app, status, warning, file_regression):
    """Build a video with negative px height and check it's rejected."""
    app.builder.build_specific([app.srcdir / "negative_px_height.rst"])

    assert 'The provided height ("-5px") is ignored' in warning.getvalue()

    html = (app.outdir / "negative_px_height.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0].prettify(formatter=fmt)
    file_regression.check(video, basename="video_no_options", extension=".html")


@pytest.mark.sphinx(testroot="video-warnings", freshenv=True)
def test_pct_width_ignores_height(app, status, warning):
    """Build a video with percentage width and height; height must be ignored."""
    app.builder.build_specific([app.srcdir / "pct_width_ignores_height.rst"])

    warnings_text = warning.getvalue()
    assert "height" in warnings_text and "ignored" in warnings_text

    html = (app.outdir / "pct_width_ignores_height.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0]
    assert video.attrs["width"] == "50%"
    assert "height" not in video.attrs


@pytest.mark.sphinx(testroot="video-secondary", freshenv=True)
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
