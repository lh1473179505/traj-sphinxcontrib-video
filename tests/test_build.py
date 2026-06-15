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


@pytest.mark.sphinx(testroot="video")
def test_video_local_poster(app, status, warning, file_regression):
    """A local poster must be copied to the build output and rewritten to _images/."""
    app.builder.build_specific([app.srcdir / "mp4_local_poster.rst"])

    # The poster file must have been copied into the builder's image output dir.
    assert (app.outdir / "_images" / "poster.png").exists(), (
        "Local poster was not copied to the build output directory"
    )
    # The local video source must still be copied too.
    assert (app.outdir / "_images" / "video.mp4").exists(), (
        "Local video source was not copied to the build output directory"
    )

    html = (app.outdir / "mp4_local_poster.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0]

    # The poster attribute must point at the builder's rewritten path, not the
    # source-relative path "videos/poster.png".
    assert video.get("poster") == "_images/poster.png", (
        f"Local poster was not rewritten to builder imgpath, got {video.get('poster')!r}"
    )
    # The local video source must still be rewritten correctly.
    sources = video.select("source")
    assert len(sources) == 1
    assert sources[0].get("src") == "_images/video.mp4", (
        f"Local video source was not rewritten correctly, got {sources[0].get('src')!r}"
    )

    file_regression.check(
        video.prettify(formatter=fmt),
        basename="video_local_poster",
        extension=".html",
    )


@pytest.mark.sphinx(testroot="video")
def test_video_remote_poster(app, status, warning, file_regression):
    """A remote poster (http/https) must be emitted unchanged and not copied."""
    app.builder.build_specific([app.srcdir / "mp4_remote_poster.rst"])

    html = (app.outdir / "mp4_remote_poster.html").read_text(encoding="utf8")
    html = BeautifulSoup(html, "html.parser")
    video = html.select("video")[0]

    # Remote poster must pass through verbatim.
    assert video.get("poster") == "https://example.com/remote-poster.png", (
        f"Remote poster was unexpectedly modified, got {video.get('poster')!r}"
    )
    # The local video source must still be rewritten correctly.
    sources = video.select("source")
    assert len(sources) == 1
    assert sources[0].get("src") == "_images/video.mp4"

    # The remote poster image must NOT have been copied into the output tree.
    copied_files = [p.name for p in (app.outdir / "_images").glob("*")]
    assert "remote-poster.png" not in copied_files, (
        "Remote poster was unexpectedly copied to the build output directory"
    )

    file_regression.check(
        video.prettify(formatter=fmt),
        basename="video_remote_poster",
        extension=".html",
    )
