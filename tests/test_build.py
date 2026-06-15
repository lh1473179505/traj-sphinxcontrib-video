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
# Focused unit tests for ``get_video()`` – local vs. remote classification
# ---------------------------------------------------------------------------


class _FakeImages:
    """Minimal stand-in for ``env.images``."""

    def __init__(self):
        self.calls = []

    def add_file(self, docname, src):
        self.calls.append((docname, src))


class _FakeEnv:
    """Lightweight fake :class:`sphinx.environment.BuildEnvironment`.

    Only the attributes and methods that :func:`get_video` touches are
    implemented, so no real Sphinx build is required.
    """

    def __init__(self, docname="index"):
        self.docname = docname
        self.images = _FakeImages()
        self._relfn2path_calls = []
        self._dependency_calls = []

    def relfn2path(self, src, docname):
        self._relfn2path_calls.append((src, docname))
        return (src, f"/abs/{src}")

    def note_dependency(self, path):
        self._dependency_calls.append(path)


class TestGetVideoClassification:
    """``get_video`` must correctly separate local and remote sources.

    * **UNC paths** (``\\\\server\\share\\clip.mp4``) are *local* network
      files – they must go through ``relfn2path`` / ``note_dependency`` /
      ``images.add_file`` even though :func:`urllib.parse.urlparse` sees a
      *netloc* component on Windows.
    * **Relative / absolute file paths** are *local*.
    * **``https://``**, **``http://``**, and **protocol-relative ``//``**
      URLs are *remote* – the local-pipeline helpers must NOT be touched.
    """

    # -- UNC paths (local) ---------------------------------------------------

    def test_unc_backslash_path_is_local(self):
        """Windows UNC path with backslashes must be treated as local."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video(r"\\server\share\clip.mp4", env)

        assert is_remote is False
        assert mime == "video/mp4"
        assert len(env._relfn2path_calls) == 1
        assert len(env._dependency_calls) == 1
        assert env.images.calls == [("index", r"\\server\share\clip.mp4")]

    def test_unc_backslash_path_webm(self):
        """UNC path with a different supported extension."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video(r"\\nas\media\video.webm", env)

        assert is_remote is False
        assert mime == "video/webm"
        assert len(env._relfn2path_calls) == 1
        assert len(env._dependency_calls) == 1

    # -- Ordinary relative path (local) --------------------------------------

    def test_relative_path_is_local(self):
        """Plain relative path must go through the local pipeline."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video("videos/clip.mp4", env)

        assert is_remote is False
        assert mime == "video/mp4"
        assert len(env._relfn2path_calls) == 1
        assert env._relfn2path_calls[0] == ("videos/clip.mp4", "index")
        assert len(env._dependency_calls) == 1
        assert env.images.calls == [("index", "videos/clip.mp4")]

    # -- Remote URLs ---------------------------------------------------------

    def test_https_url_is_remote(self):
        """https URL must be treated as remote – no local side-effects."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video("https://example.com/clip.mp4", env)

        assert is_remote is True
        assert mime == "video/mp4"
        assert env._relfn2path_calls == []
        assert env._dependency_calls == []
        assert env.images.calls == []

    def test_http_url_is_remote(self):
        """http URL must be treated as remote."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video("http://cdn.example.com/video.webm", env)

        assert is_remote is True
        assert mime == "video/webm"
        assert env._relfn2path_calls == []
        assert env._dependency_calls == []
        assert env.images.calls == []

    def test_protocol_relative_url_is_remote(self):
        """``//cdn.example.com/…`` is a remote protocol-relative URL."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video("//cdn.example.com/clip.mp4", env)

        assert is_remote is True
        # NOTE: On Windows, Path('//host/share') is parsed as UNC with an
        # empty *name*, so suffix (and therefore *mime*) may be "".  The
        # critical contract here is that the URL is classified as remote
        # and the local pipeline is NOT invoked.
        assert env._relfn2path_calls == []
        assert env._dependency_calls == []
        assert env.images.calls == []

    # -- Return-value contract -----------------------------------------------

    def test_return_tuple_order(self):
        """The three-tuple order must be (src, mime_type, is_remote)."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        result = get_video("https://example.com/clip.webm", env)

        assert len(result) == 3
        src, mime, is_remote = result
        assert src == "https://example.com/clip.webm"
        assert mime == "video/webm"
        assert is_remote is True

    # -- Unsupported format warning ------------------------------------------

    def test_unsupported_format_warns_but_does_not_crash(self, caplog):
        """Unsupported extension does not crash; mime type defaults to ``""``.

        (The warning message itself is already covered by
        :func:`test_wrong_format` which runs inside a full Sphinx build.)
        """
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        src, mime, is_remote = get_video("file.mkv", env)

        assert mime == ""
        assert is_remote is False
        # Local pipeline is still invoked even for unsupported formats.
        assert len(env._relfn2path_calls) == 1
        assert len(env._dependency_calls) == 1

    # -- MIME type coverage --------------------------------------------------

    @pytest.mark.parametrize(
        "ext, expected_mime",
        [
            (".mp4", "video/mp4"),
            (".webm", "video/webm"),
            (".ogg", "video/ogg"),
            (".ogv", "video/ogg"),
            (".ogm", "video/ogg"),
        ],
    )
    def test_mime_types(self, ext, expected_mime):
        """All entries in ``SUPPORTED_MIME_TYPES`` are returned correctly."""
        from sphinxcontrib.video import get_video

        env = _FakeEnv()
        _, mime, _ = get_video(f"video{ext}", env)
        assert mime == expected_mime
