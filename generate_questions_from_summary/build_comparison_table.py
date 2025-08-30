import os
import re
from collections import OrderedDict


def parse_mapping(md_path: str) -> list[tuple[str, str]]:
    rows: list[tuple[str, str]] = []
    if not os.path.exists(md_path):
        return rows
    with open(md_path, 'r', encoding='utf-8') as f:
        for raw in f:
            line = raw.strip()
            if not line.startswith('|'):
                continue
            if line.startswith('|---'):
                continue
            if 'Source Point' in line:
                continue
            parts = [p.strip() for p in line.strip('|').split('|')]
            if len(parts) < 2:
                continue
            point_text = parts[0].replace('\\|', '|').strip()
            id_list = parts[1].strip()
            rows.append((point_text, id_list))
    return rows


def build_comparison_table() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    openai_md = os.path.join(base_dir, 'points_to_questions.md')
    gemini_md = os.path.join(base_dir, 'points_to_questions_gemini.md')
    mistral_md = os.path.join(base_dir, 'points_to_questions_mistral.md')

    openai_txt = os.path.join(base_dir, 'summary_questions_openai.txt')
    gemini_txt = os.path.join(base_dir, 'summary_questions_gemini.txt')
    mistral_txt = os.path.join(base_dir, 'summary_questions_mistral.txt')

    openai_rows = parse_mapping(openai_md)
    gemini_rows = parse_mapping(gemini_md)
    mistral_rows = parse_mapping(mistral_md)

    openai_map = {pt: ids for pt, ids in openai_rows}
    gemini_map = {pt: ids for pt, ids in gemini_rows}
    mistral_map = {pt: ids for pt, ids in mistral_rows}

    # Parse MCQ blocks to map labels like "1a" -> full MCQ text block
    openai_blocks = parse_mcq_blocks(openai_txt)
    gemini_blocks = parse_mcq_blocks(gemini_txt)
    mistral_blocks = parse_mcq_blocks(mistral_txt)

    # Row order: OpenAI first, then any extra points from Gemini/Mistral preserving discovery order
    ordered_points: "OrderedDict[str, None]" = OrderedDict()
    for pt, _ in openai_rows:
        ordered_points.setdefault(pt, None)
    for pt, _ in gemini_rows:
        ordered_points.setdefault(pt, None)
    for pt, _ in mistral_rows:
        ordered_points.setdefault(pt, None)

    header = "| S.no | Point | openai | gemini | mistral |"
    sep = "|---:|---|---|---|---|"
    lines = [header, sep]

    for idx, pt in enumerate(ordered_points.keys(), start=1):
        safe_point = pt.replace('|', '\\|')
        openai_cell = format_cell_from_ids(openai_map.get(pt), openai_blocks)
        gemini_cell = format_cell_from_ids(gemini_map.get(pt), gemini_blocks)
        mistral_ids = mistral_map.get(pt)
        if mistral_ids:
            mistral_cell = format_cell_from_ids(mistral_ids, mistral_blocks)
        else:
            mistral_cell = format_cell_from_row_index(idx, mistral_blocks)
        lines.append(f"| {idx} | {safe_point} | {openai_cell} | {gemini_cell} | {mistral_cell} |")

    return "\n".join(lines)


def html_escape(s: str) -> str:
    return (
        s.replace("&", "&amp;")
         .replace("<", "&lt;")
         .replace(">", "&gt;")
    )


def build_comparison_html() -> str:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    openai_md = os.path.join(base_dir, 'points_to_questions.md')
    gemini_md = os.path.join(base_dir, 'points_to_questions_gemini.md')
    mistral_md = os.path.join(base_dir, 'points_to_questions_mistral.md')

    openai_txt = os.path.join(base_dir, 'summary_questions_openai.txt')
    gemini_txt = os.path.join(base_dir, 'summary_questions_gemini.txt')
    mistral_txt = os.path.join(base_dir, 'summary_questions_mistral.txt')

    openai_rows = parse_mapping(openai_md)
    gemini_rows = parse_mapping(gemini_md)
    mistral_rows = parse_mapping(mistral_md)

    openai_map = {pt: ids for pt, ids in openai_rows}
    gemini_map = {pt: ids for pt, ids in gemini_rows}
    mistral_map = {pt: ids for pt, ids in mistral_rows}

    openai_blocks = parse_mcq_blocks(openai_txt)
    gemini_blocks = parse_mcq_blocks(gemini_txt)
    mistral_blocks = parse_mcq_blocks(mistral_txt)

    ordered_points: "OrderedDict[str, None]" = OrderedDict()
    for pt, _ in openai_rows:
        ordered_points.setdefault(pt, None)
    for pt, _ in gemini_rows:
        ordered_points.setdefault(pt, None)
    for pt, _ in mistral_rows:
        ordered_points.setdefault(pt, None)

    rows_html: list[str] = []
    for idx, pt in enumerate(ordered_points.keys(), start=1):
        openai_cell = format_cell_from_ids_html(openai_map.get(pt), openai_blocks)
        gemini_cell = format_cell_from_ids_html(gemini_map.get(pt), gemini_blocks)
        mistral_ids = mistral_map.get(pt)
        if mistral_ids:
            mistral_cell = format_cell_from_ids_html(mistral_ids, mistral_blocks)
        else:
            mistral_cell = format_cell_from_row_index_html(idx, mistral_blocks)
        rows_html.append(
            (
                "<tr>"
                f"<td class=\"col-sno\">{idx}</td>"
                f"<td class=\"col-point\">{html_escape(pt)}</td>"
                f"<td class=\"col-model\">{openai_cell}</td>"
                f"<td class=\"col-model\">{gemini_cell}</td>"
                f"<td class=\"col-model\">{mistral_cell}</td>"
                "</tr>"
            )
        )

    html = f"""
<!DOCTYPE html>
<html lang=\"en\"> 
<head>
  <meta charset=\"utf-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
  <title>MCQ Comparison Table</title>
  <style>
    :root {{
      --border: #e2e2e2;
      --header: #fafafa;
      --text: #1a1a1a;
      --muted: #666;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; padding: 16px; font-family: system-ui, -apple-system, Segoe UI, Roboto, Arial, sans-serif; color: var(--text);
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      table-layout: fixed;
    }}
    thead th {{
      position: sticky; top: 0; background: var(--header);
      border: 1px solid var(--border);
      padding: 10px; text-align: left;
    }}
    tbody td {{
      border: 1px solid var(--border);
      padding: 10px; vertical-align: top;
      overflow-wrap: anywhere;
    }}
    .col-sno {{ width: 72px; text-align: right; }}
    .col-point {{ width: 28%; }}
    .col-model {{ width: auto; }}
    .mcq {{
      margin-bottom: 12px;
      border: 1px solid var(--border);
      border-radius: 6px;
      background: #ffffff;
      padding: 8px 10px;
    }}
    .mcq:last-child {{ margin-bottom: 0; }}
    .mcq .label {{ color: var(--muted); font-weight: 600; margin-bottom: 4px; }}
    .mcq pre {{ margin: 0; white-space: pre-wrap; line-height: 1.25; }}
  </style>
  </head>
  <body>
    <table>
      <thead>
        <tr>
          <th class=\"col-sno\">S.no</th>
          <th class=\"col-point\">Point</th>
          <th>openai</th>
          <th>gemini</th>
          <th>mistral</th>
        </tr>
      </thead>
      <tbody>
        {''.join(rows_html)}
      </tbody>
    </table>
  </body>
</html>
"""
    return html

def parse_mcq_blocks(txt_path: str) -> dict[str, str]:
    blocks: dict[str, str] = {}
    if not os.path.exists(txt_path):
        return blocks
    with open(txt_path, 'r', encoding='utf-8') as f:
        content = f.read().strip()
    if not content:
        return blocks
    # Split on two or more newlines to get each MCQ block
    raw_blocks = re.split(r"(?:\r?\n){2,}", content)
    label_pat = re.compile(r"^\s*(\d+[abc])\.\s", re.IGNORECASE)
    for blk in raw_blocks:
        if not blk.strip():
            continue
        first_line = None
        for line in blk.splitlines():
            if line.strip():
                first_line = line
                break
        if first_line is None:
            continue
        m = label_pat.match(first_line)
        if not m:
            continue
        label = m.group(1).lower()
        blocks[label] = blk.strip()
    return blocks


def format_cell_from_ids(id_list_str: str | None, label_to_block: dict[str, str]) -> str:
    if not id_list_str:
        return "-"
    ids = [s.strip().lower() for s in id_list_str.split(',') if s.strip()]
    parts: list[str] = []
    for _id in ids:
        blk = label_to_block.get(_id)
        if not blk:
            continue
        # Escape pipes and convert newlines to <br/>
        safe_blk = blk.replace('|', '\\|').replace('\n', '<br/>')
        parts.append(safe_blk)
    return '<br/><br/>'.join(parts) if parts else "-"


def format_cell_from_ids_html(id_list_str: str | None, label_to_block: dict[str, str]) -> str:
    if not id_list_str:
        return "-"
    ids = [s.strip().lower() for s in id_list_str.split(',') if s.strip()]
    parts: list[str] = []
    for _id in ids:
        blk = label_to_block.get(_id)
        if not blk:
            continue
        parts.append(f"<div class=\"mcq\"><pre>{html_escape(blk)}</pre></div>")
    return ''.join(parts) if parts else "-"


def format_cell_from_row_index(row_index: int, label_to_block: dict[str, str]) -> str:
    labels = [f"{row_index}a", f"{row_index}b", f"{row_index}c"]
    parts: list[str] = []
    for lab in labels:
        blk = label_to_block.get(lab)
        if blk:
            parts.append(blk.replace('|', '\\|').replace('\n', '<br/>'))
    return '<br/><br/>'.join(parts) if parts else "-"


def format_cell_from_row_index_html(row_index: int, label_to_block: dict[str, str]) -> str:
    labels = [f"{row_index}a", f"{row_index}b", f"{row_index}c"]
    parts: list[str] = []
    for lab in labels:
        blk = label_to_block.get(lab)
        if blk:
            parts.append(f"<div class=\"mcq\"><pre>{html_escape(blk)}</pre></div>")
    return ''.join(parts) if parts else "-"


def main() -> None:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(base_dir, 'comparison_table.md')
    table = build_comparison_table()
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(table)
    print(f"Wrote {out_path}")

    html_out = os.path.join(base_dir, 'comparison_table.html')
    html = build_comparison_html()
    with open(html_out, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Wrote {html_out}")


if __name__ == '__main__':
    main()


