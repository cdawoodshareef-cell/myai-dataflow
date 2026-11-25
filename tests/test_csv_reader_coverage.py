import pytest
from csv_reader import read_csv

@pytest.mark.parametrize("payload", [
    b"Name,Amount\nAcme,100\n",
    bytearray(b"Name,Amount\nAcme,100\n"),
])
def test_bytes_and_bytearray_input(payload):
    assert read_csv(payload) == (["Name", "Amount"], [["Acme", "100"]])

def test_invalid_utf8_binary_input_raises_value_error():
    with pytest.raises(ValueError, match="UTF-8 encoded CSV"):
        read_csv(b"Name\n\xff\n")

def test_invalid_utf8_text_stream_raises_value_error():
    class InvalidTextStream:
        def read(self, size=0): return ""
        def seek(self, position): pass
        def __iter__(self):
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
    with pytest.raises(ValueError, match="UTF-8 encoded CSV"):
        read_csv(InvalidTextStream())

def test_unsupported_input_type_raises_type_error():
    with pytest.raises(TypeError, match="file-like object or bytes"):
        read_csv(None)
