import os
import sqlite3
import zipfile
from datetime import datetime
from xml.sax.saxutils import escape

from src.store_sqlite import DB_PATH


def _column_name(index: int) -> str:
    name = ""
    while index > 0:
        index, rem = divmod(index - 1, 26)
        name = chr(65 + rem) + name
    return name


def _build_sheet_xml(rows: list[list[object]]) -> str:
    sheet_rows: list[str] = []
    for ridx, row in enumerate(rows, start=1):
        cells: list[str] = []
        for cidx, value in enumerate(row, start=1):
            ref = f"{_column_name(cidx)}{ridx}"
            if value is None:
                cells.append(f'<c r="{ref}"/>')
            else:
                text = escape(str(value))
                cells.append(f'<c r="{ref}" t="inlineStr"><is><t>{text}</t></is></c>')
        sheet_rows.append(f"<row r=\"{ridx}\">{''.join(cells)}</row>")

    return (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<worksheet xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\">"
        "<sheetData>"
        f"{''.join(sheet_rows)}"
        "</sheetData>"
        "</worksheet>"
    )


def build_excel_report(snapshot_date: str) -> str:
    os.makedirs("data", exist_ok=True)
    output_path = os.path.join("data", f"movie_data_{snapshot_date}.xlsx")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute(
        """
        SELECT snapshot_date, source, tmdb_id, rank, title, year, url
        FROM daily_snapshot
        ORDER BY snapshot_date DESC, rank ASC
        """
    )
    snapshot_rows = [
        ["snapshot_date", "source", "tmdb_id", "rank", "title", "year", "url"],
        *[list(row) for row in cur.fetchall()],
    ]

    cur.execute(
        """
        SELECT sent_date, tmdb_id, title, year
        FROM sent_log
        ORDER BY sent_date DESC, rowid DESC
        """
    )
    sent_rows = [["sent_date", "tmdb_id", "title", "year"], *[list(row) for row in cur.fetchall()]]

    meta_rows = [["generated_at"], [datetime.now().isoformat()]]
    conn.close()

    workbook_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<workbook xmlns=\"http://schemas.openxmlformats.org/spreadsheetml/2006/main\" "
        "xmlns:r=\"http://schemas.openxmlformats.org/officeDocument/2006/relationships\">"
        "<sheets>"
        '<sheet name="daily_snapshot" sheetId="1" r:id="rId1"/>'
        '<sheet name="sent_log" sheetId="2" r:id="rId2"/>'
        '<sheet name="meta" sheetId="3" r:id="rId3"/>'
        "</sheets>"
        "</workbook>"
    )

    workbook_rels_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>'
        '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet2.xml"/>'
        '<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet3.xml"/>'
        "</Relationships>"
    )

    root_rels_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Relationships xmlns=\"http://schemas.openxmlformats.org/package/2006/relationships\">"
        '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>'
        "</Relationships>"
    )

    content_types_xml = (
        "<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"yes\"?>"
        "<Types xmlns=\"http://schemas.openxmlformats.org/package/2006/content-types\">"
        '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
        '<Default Extension="xml" ContentType="application/xml"/>'
        '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
        '<Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet2.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        '<Override PartName="/xl/worksheets/sheet3.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
        "</Types>"
    )

    with zipfile.ZipFile(output_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml)
        zf.writestr("_rels/.rels", root_rels_xml)
        zf.writestr("xl/workbook.xml", workbook_xml)
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_xml)
        zf.writestr("xl/worksheets/sheet1.xml", _build_sheet_xml(snapshot_rows))
        zf.writestr("xl/worksheets/sheet2.xml", _build_sheet_xml(sent_rows))
        zf.writestr("xl/worksheets/sheet3.xml", _build_sheet_xml(meta_rows))

    return output_path
