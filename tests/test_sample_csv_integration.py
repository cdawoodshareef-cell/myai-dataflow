import csv
import io
from pathlib import Path

from csv_reader import read_csv
from exporter import generate_clean_csv, generate_review_report
from validator import validate_rows


def test_sample_csv_complete_validation_and_export_workflow():
    sample_path = Path(__file__).resolve().parents[1] / "sample_data.csv"
    assert sample_path.is_file(), "sample_data.csv must exist"

    column_names, data_rows = read_csv(sample_path.read_bytes())
    result = validate_rows(column_names, data_rows)

    assert result.total_count == len(data_rows)
    assert result.clean_count == len(result.clean_rows)
    assert result.flagged_count == len(result.flagged_rows)
    assert result.clean_count + result.flagged_count == result.total_count

    clean_bytes = generate_clean_csv(column_names, result.clean_rows)
    review_bytes = generate_review_report(column_names, result.flagged_rows)

    clean_output = list(csv.reader(io.StringIO(clean_bytes.decode("utf-8"))))
    review_output = list(csv.reader(io.StringIO(review_bytes.decode("utf-8"))))

    assert clean_output[0] == column_names
    assert clean_output[1:] == result.clean_rows
    assert len(clean_output) == result.clean_count + 1

    expected_review_header = column_names + [
        "Original Row Number",
        "Flag Reason",
        "Excel Row Number",
        "Duplicate of Excel Row",
    ]
    assert review_output[0] == expected_review_header
    assert len(review_output[0]) == len(column_names) + 4
    assert len(review_output) == result.flagged_count + 1

    for exported_row, flagged_row in zip(review_output[1:], result.flagged_rows):
        expected_values = (
            flagged_row.row_values
            + [""] * max(0, len(column_names) - len(flagged_row.row_values))
        )[:len(column_names)]

        assert exported_row[:len(column_names)] == expected_values
        assert exported_row[len(column_names)] == str(flagged_row.row_number)
        assert exported_row[len(column_names) + 1] == flagged_row.reason
        assert exported_row[len(column_names) + 2] == str(flagged_row.row_number + 1)

        expected_duplicate = (
            str(flagged_row.duplicate_of_row + 1)
            if flagged_row.duplicate_of_row is not None
            else ""
        )
        assert exported_row[len(column_names) + 3] == expected_duplicate
