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


@pytest.mark.sphinx(testroot="video-escape")
def test_video_special_chars_escaped(app, status, warning):
    """Build a video with special characters in options and verify proper HTML escaping."""
    app.builder.build_specific([app.srcdir / "special.rst"])

    raw_html = (app.outdir / "special.html").read_text(encoding="utf8")
    soup = BeautifulSoup(raw_html, "html.parser")

    # The video element must exist and be parseable (injection did not break structure)
    videos = soup.select("video")
    assert len(videos) == 1
    video = videos[0]

    # poster attribute with & and = must be preserved as attribute value
    assert video.get("poster") == "https://example.com/p.png?a=1&b=2"

    # class attribute with " must be preserved (not breaking out of the attribute)
    classes = video.get("class", [])
    assert 'my"class' in classes

    # alt text must appear as text content, not as HTML tags
    assert "<b>bold</b>" not in str(video)
    assert "<b>" not in str(video)
    assert "bold" in video.get_text()
    assert "&" in video.get_text()  # literal & in text

    # caption must appear as text, not as injected tags
    figure = soup.select("figure")
    assert len(figure) == 1
    caption_text = figure[0].select("figcaption")[0].get_text()
    # BeautifulSoup decodes entities, so get_text() returns "<script>" as text
    # We need to verify in the raw HTML that it's escaped
    assert "&lt;script&gt;" in raw_html or "&lt;script&gt" in raw_html
    assert "alert" in caption_text
    assert "&" in caption_text
    assert '"caption"' in caption_text

    # source tag must exist with proper src
    source = video.select("source")[0]
    assert source.get("type") == "video/mp4"

    # Verify the raw HTML does not contain unescaped injection patterns
    assert "<b>bold</b>" not in raw_html.split("<video")[1].split("</video>")[0]
    # Check that <script>alert (the XSS payload) does not appear as a real tag
    # (the Sphinx theme may include its own <script> tags, so be specific)
    assert "<script>alert" not in raw_html


@pytest.mark.sphinx(testroot="video-escape")
def test_video_no_double_escape(app, status, warning):
    """Build a video with normal values and verify they are not double-escaped."""
    app.builder.build_specific([app.srcdir / "normal.rst"])

    raw_html = (app.outdir / "normal.html").read_text(encoding="utf8")
    soup = BeautifulSoup(raw_html, "html.parser")

    video = soup.select("video")[0]

    # Normal poster URL should not be mangled (no &amp; in the attribute value)
    assert video.get("poster") == "https://example.com/poster.png"

    # Class should be preserved as-is
    assert "normal-class" in video.get("class", [])

    # Alt text should appear as plain text without HTML entities
    alt_text = video.get_text()
    assert "Normal alt text" in alt_text
    assert "&amp;" not in alt_text

    # Caption should appear as plain text without HTML entities
    figure = soup.select("figure")
    assert len(figure) == 1
    caption_text = figure[0].select("figcaption")[0].get_text()
    assert "Normal caption text" in caption_text
    assert "&amp;" not in caption_text

    # Verify no double-escaped entities in raw HTML
    assert "&amp;amp;" not in raw_html
