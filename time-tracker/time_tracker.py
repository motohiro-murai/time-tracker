import argparse, json, os, csv
from datetime import datetime, timezone, timedelta

# 日本時間（JST）
JST = timezone(timedelta(hours=9))

# 保存先
DATA_DIR = "data"
DATA_FILE = os.path.join(DATA_DIR, "sessions.json")

# ===== ユーティリティ =====
def now_iso():
    return datetime.now(JST).isoformat(timespec="seconds")

def parse_iso(s: str) -> datetime:
    # Pythonのfromisoformatはタイムゾーン付きISOもOK
    return datetime.fromisoformat(s)

def fmt_dur(seconds: int) -> str:
    seconds = max(0, int(seconds))
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h: return f"{h}h {m}m {s}s"
    if m: return f"{m}m {s}s"
    return f"{s}s"

def ensure_store():
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=2)

def load_sessions():
    ensure_store()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sessions(sessions):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(sessions, f, ensure_ascii=False, indent=2)

# ===== コマンド =====
def cmd_start(task: str):
    sessions = load_sessions()
    sessions.append({"task": task, "start": now_iso(), "end": None, "seconds": None})
    save_sessions(sessions)
    print(f"🟢 開始: {task}")

def cmd_stop():
    sessions = load_sessions()
    for s in reversed(sessions):
        if s.get("end") is None:
            end_iso = now_iso()
            s["end"] = end_iso
            # 経過秒を計算して保存
            try:
                start_dt = parse_iso(s["start"])
                end_dt = parse_iso(end_iso)
                s["seconds"] = int((end_dt - start_dt).total_seconds())
            except Exception:
                s["seconds"] = None
            save_sessions(sessions)
            msg_dur = fmt_dur(s["seconds"]) if s.get("seconds") else "-"
            print(f"⏹ 停止: {s['task']}（{msg_dur}）")
            return
    print("⚠️ 動作中のタスクはありません。")

def cmd_status():
    sessions = load_sessions()
    for s in reversed(sessions):
        if s.get("end") is None:
            print(f"🟢 稼働中: {s['task']} （開始 {s['start']}）")
            return
    print("⏸ いまは稼働していません。")

def cmd_log(limit=None):
    sessions = load_sessions()
    count = len(sessions)
    print(f"📒 作業履歴（全{count}件）")
    if count == 0:
        return
    rows = sessions[-limit:] if limit else sessions
    print("-" * 80)
    print(f"{'開始':19}  {'終了':19}  {'時間':10}  タスク")
    print("-" * 80)
    for s in rows:
        start = s.get("start") or "-"
        end   = s.get("end") or "-"
        secs  = s.get("seconds")
        dur   = fmt_dur(secs) if isinstance(secs, int) else "-"
        task  = s.get("task") or "(不明)"
        print(f"{start:19}  {end:19}  {dur:10}  {task}")

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
    print(f" CSVを書き出しました: {out_path}")

# ===== エントリポイント =====
def main():
    parser = argparse.ArgumentParser(prog="time-tracker")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_start = sub.add_parser("start", help="作業を開始")
    p_start.add_argument("task", help="タスク名")

    sub.add_parser("stop", help="作業を停止")
    sub.add_parser("status", help="状態を表示")

    p_log = sub.add_parser("log", help="履歴を一覧表示")
    p_log.add_argument("--limit", type=int, help="末尾からN件だけ表示")
    p_log.set_defaults(func=lambda args: cmd_log(args.limit))

    p_csv = sub.add_parser("csv", help="CSVに書き出し（Excel集計用）")
    p_csv.add_argument("--out", default="data/log_all.csv", help="保存先パス")
    p_csv.add_argument("--with-hours", action="store_true", help="hours列(=秒/3600)を含める")
    p_csv.set_defaults(func=lambda args: cmd_csv(args.out, args.with_hours))

    args = parser.parse_args()

    # 既存3コマンドは分岐、追加コマンドは set_defaults で実行
    if args.cmd == "start":
        cmd_start(args.task)
    elif args.cmd == "stop":
        cmd_stop()
    elif args.cmd == "status":
        cmd_status()
    else:
        args.func(args)  # log / csv

if __name__ == "__main__":
    main()