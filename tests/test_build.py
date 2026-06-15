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
def test_video_caption_escape(app, status, warning):
    """Build a video with HTML-sensitive caption and verify escaping."""
    app.builder.build_specific([app.srcdir / "mp4_caption_escape.rst"])

    raw_html = (app.outdir / "mp4_caption_escape.html").read_text(encoding="utf8")

    # Extract the figcaption section to scope assertions
    soup = BeautifulSoup(raw_html, "html.parser")
    figcaption = soup.select("figcaption")
    assert len(figcaption) == 1
    figcaption_html = str(figcaption[0])

    # Raw script tags must not appear in the figcaption
    assert "<script>" not in figcaption_html
    assert "</script>" not in figcaption_html

    # The escaped forms must be present in the raw HTML within the caption area
    # Find the caption-text span in raw HTML to check escaping
    caption_span = soup.select("span.caption-text")
    assert len(caption_span) == 1
    # BeautifulSoup decodes entities back to text, so verify the decoded text
    assert "<script>alert(1)</script> A&B" in caption_span[0].get_text()

    # Also verify the raw HTML contains escaped entities near caption-text
    # Extract the raw span content by regex
    import re

    span_match = re.search(
        r'<span class="caption-text">(.*?)</span>', raw_html, re.DOTALL
    )
    assert span_match is not None
    raw_caption = span_match.group(1)
    assert "&lt;script&gt;" in raw_caption
    assert "&lt;/script&gt;" in raw_caption
    assert "&amp;" in raw_caption

    # Structural tags must remain intact (not escaped)
    assert "<figure" in raw_html
    assert "<figcaption" in raw_html
    assert '<span class="caption-text">' in raw_html


@pytest.mark.sphinx(testroot="video")
def test_video_caption_normal(app, status, warning):
    """Build a video with a normal caption and verify it is readable."""
    app.builder.build_specific([app.srcdir / "mp4_caption_normal.rst"])

    raw_html = (app.outdir / "mp4_caption_normal.html").read_text(encoding="utf8")
    soup = BeautifulSoup(raw_html, "html.parser")

    caption_span = soup.select("span.caption-text")
    assert len(caption_span) == 1
    assert caption_span[0].get_text().strip() == "A normal caption text"
