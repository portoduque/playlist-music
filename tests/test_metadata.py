"""Metadata writes keep the original audio bytes when optional data fails."""

from mutagen.id3 import ID3

from playlist_music import metadata


def test_writes_title_artist_album_and_png_cover(tmp_path) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")
    cover = tmp_path / "cover.png"
    cover.write_bytes(
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0dIDATx\x9cc\xf8\xcf\xc0\xf0"
        b"\x1f\x00\x05\x00\x01\xff\x89\x99=\x1d\x00\x00\x00\x00IEND\xaeB`\x82"
    )

    result = metadata.write_metadata(audio, "Title", "Artist", "Album", cover)
    tags = ID3(audio)

    assert result.issues == []
    assert tags.get("TIT2").text == ["Title"]
    assert tags.get("TPE1").text == ["Artist"]
    assert tags.get("TALB").text == ["Album"]
    assert tags.getall("APIC")[0].mime == "image/png"
    assert audio.read_bytes().endswith(b"audio")


def test_reports_invalid_cover_without_losing_written_tags(tmp_path) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")
    cover = tmp_path / "cover.txt"
    cover.write_bytes(b"not an image")

    result = metadata.write_metadata(audio, "Title", None, None, cover)

    assert result.issues == ["Cover must be a JPEG or PNG file."]
    assert ID3(audio).get("TIT2").text == ["Title"]
    assert audio.read_bytes().endswith(b"audio")


def test_writes_a_jpeg_cover(tmp_path) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")
    cover = tmp_path / "cover.jpg"
    cover.write_bytes(b"\xff\xd8\xff\xe0jpeg data")

    result = metadata.write_metadata(audio, None, None, None, cover)

    assert result.issues == []
    assert ID3(audio).getall("APIC")[0].mime == "image/jpeg"


def test_reports_tag_write_failure_without_losing_audio(tmp_path, monkeypatch) -> None:
    audio = tmp_path / "song.mp3"
    original = b"audio"
    audio.write_bytes(original)

    def fail_save(self, *_args, **_kwargs) -> None:
        raise OSError("disk error")

    monkeypatch.setattr(metadata.ID3, "save", fail_save)

    result = metadata.write_metadata(audio, "Title", None, None)

    assert result.issues == ["Could not write audio tags."]
    assert audio.read_bytes() == original


def test_allows_missing_optional_metadata(tmp_path) -> None:
    audio = tmp_path / "song.mp3"
    audio.write_bytes(b"audio")

    result = metadata.write_metadata(audio, None, None, None)

    assert result.issues == []
    assert audio.read_bytes() == b"audio"
