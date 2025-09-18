import csv, os  # ファイル先頭のimportにcsvを追加

def cmd_csv(out_path: str, with_hours: bool):
    sessions = load_sessions()
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    fieldnames = ["index", "start", "end", "task", "seconds"]
    if with_hours:
        fieldnames.append("hours")

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for i, s in enumerate(sessions, start=1):
            secs = s.get("seconds")
            secs = int(secs) if isinstance(secs, (int, float)) else 0
            row = {
                "index": i,
                "start": s.get("start"),
                "end": s.get("end"),
                "task": s.get("task"),
                "seconds": secs,
            }
            if with_hours:
                row["hours"] = secs / 3600 if secs else 0
            w.writerow(row)
    print(f"💾 CSVを書き出しました: {out_path}")