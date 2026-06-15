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


# ---------------------------------------------------------------------------
# Focused unit tests for get_video() remote-vs-local detection
# ---------------------------------------------------------------------------
from unittest.mock import MagicMock, call
from sphinxcontrib.video import get_video


def _make_fake_env():
    """Return a lightweight fake BuildEnvironment for get_video()."""
    env = MagicMock()
    env.docname = "index"
    # relfn2path returns (relative_src, absolute_fullpath)
    env.relfn2path = MagicMock(side_effect=lambda src, docname: (src, "/fake/" + src))
    return env


class TestGetVideoLocal:
    """Local paths must trigger relfn2path / note_dependency / images.add_file."""

    def test_relative_path(self):
        env = _make_fake_env()
        src, mime, is_remote = get_video("_static/video.mp4", env)

        assert is_remote is False
        assert mime == "video/mp4"
        env.relfn2path.assert_called_once_with("_static/video.mp4", "index")
        env.note_dependency.assert_called_once_with("/fake/_static/video.mp4")
        env.images.add_file.assert_called_once_with("index", "_static/video.mp4")

    def test_unc_backslash_path(self):
        env = _make_fake_env()
        src, mime, is_remote = get_video("\\\\server\\share\\clip.mp4", env)

        assert is_remote is False
        env.relfn2path.assert_called_once()
        env.note_dependency.assert_called_once()
        env.images.add_file.assert_called_once()


class TestGetVideoRemote:
    """Remote URLs must NOT touch relfn2path / note_dependency / images.add_file."""

    def test_https_url(self):
        env = _make_fake_env()
        src, mime, is_remote = get_video("https://example.com/clip.mp4", env)

        assert is_remote is True
        assert mime == "video/mp4"
        env.relfn2path.assert_not_called()
        env.note_dependency.assert_not_called()
        env.images.add_file.assert_not_called()

    def test_http_url(self):
        env = _make_fake_env()
        src, mime, is_remote = get_video("http://example.com/clip.mp4", env)

        assert is_remote is True
        env.relfn2path.assert_not_called()
        env.note_dependency.assert_not_called()
        env.images.add_file.assert_not_called()

    def test_protocol_relative_url(self):
        env = _make_fake_env()
        src, mime, is_remote = get_video("//cdn.example.com/clip.mp4", env)

        assert is_remote is True
        env.relfn2path.assert_not_called()
        env.note_dependency.assert_not_called()
        env.images.add_file.assert_not_called()
