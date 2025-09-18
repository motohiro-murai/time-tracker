# -*- coding: utf-8 -*-
import os
os.environ["TK_SILENCE_DEPRECATION"] = "1"

import sys, traceback
def _err_hook(t, v, tb):
    print("===== GUI例外検出 =====")
    traceback.print_exception(t, v, tb)
sys.excepthook = _err_hook

import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# CLI本体を読み込み（失敗したらダイアログ表示）
try:
    import time_tracker as tt
except Exception:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("import error", traceback.format_exc())
    raise


class TrackerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Time Tracker")
        self.geometry("800x560")
        self.minsize(760, 520)

        # macっぽいスタイル設定
        self.setup_style()

        # --- 上段: 入力とボタン ---
        top = ttk.Frame(self, padding=(12, 10))
        top.pack(fill="x")

        ttk.Label(top, text="タスク名:").pack(side="left")
        self.task_var = tk.StringVar()
        ttk.Entry(top, textvariable=self.task_var, width=30).pack(side="left", padx=(8, 16))

        # 左側の操作ボタン
        btns = ttk.Frame(top)
        btns.pack(side="left")
        ttk.Button(btns, text="開始", command=self.on_start).pack(side="left", padx=(0, 6))
        ttk.Button(btns, text="停止", command=self.on_stop).pack(side="left", padx=6)
        ttk.Button(btns, text="状態", command=self.on_status).pack(side="left", padx=6)

        # 右側の操作ボタン
        right = ttk.Frame(top)
        right.pack(side="right")
        ttk.Button(right, text="再読み込み", command=self.safe_refresh).pack(side="left", padx=(0, 8))
        ttk.Button(right, text="CSV出力", command=self.on_csv).pack(side="left")

        # --- ステータス行 ---
        self.status_var = tk.StringVar(value="⏸ いまは稼働していません。")
        ttk.Label(self, textvariable=self.status_var, padding=(14, 6)).pack(anchor="w")

        # --- ログ一覧 ---
        cols = ("start", "end", "dur", "task")
        self.tree = ttk.Treeview(self, columns=cols, show="headings", height=16)
        self.tree.heading("start", text="開始")
        self.tree.heading("end", text="終了")
        self.tree.heading("dur", text="時間")
        self.tree.heading("task", text="タスク")

        self.tree.column("start", width=240, anchor="w")
        self.tree.column("end", width=240, anchor="w")
        self.tree.column("dur", width=90, anchor="center")
        self.tree.column("task", width=260, anchor="w")

        self.tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

        # ゼブラ模様
        self.tree.tag_configure("odd", background="#FAFAFA")
        self.tree.tag_configure("even", background="#FFFFFF")

        # 初期データ更新
        self.safe_refresh()

    # --- mac風スタイル設定 ---
    def setup_style(self):
        style = ttk.Style(self)
        try:
            style.theme_use("aqua")
        except Exception:
            style.theme_use("clam")

        base_font = ("SF Pro Text", 12)
        style.configure(".", font=base_font)

        style.configure("TLabel", padding=(2, 2))
        style.configure("TButton", padding=(10, 6))
        style.configure("Treeview", rowheight=28, font=base_font)
        style.configure("Treeview.Heading", font=("SF Pro Text", 12, "bold"))
        style.configure("TEntry", padding=(6, 4))

    # --- 安全な更新 ---
    def safe_refresh(self):
        try:
            self.refresh_log()
            self.on_status()
        except Exception:
            messagebox.showerror("初期化エラー", traceback.format_exc())

    # --- ハンドラ ---
    def on_start(self):
        task = self.task_var.get().strip()
        if not task:
            messagebox.showwarning("入力不足", "タスク名を入力してください。")
            return
        try:
            tt.cmd_start(task)
            self.task_var.set("")
            self.safe_refresh()
        except Exception:
            messagebox.showerror("開始エラー", traceback.format_exc())

    def on_stop(self):
        try:
            tt.cmd_stop()
            self.safe_refresh()
        except Exception:
            messagebox.showerror("停止エラー", traceback.format_exc())

    def on_status(self):
        sessions = tt.load_sessions()
        running = next((s for s in reversed(sessions) if s.get("end") is None), None)
        if running:
            self.status_var.set(f"🟢 稼働中: {running.get('task')}（開始 {running.get('start')}）")
        else:
            self.status_var.set("⏸ いまは稼働していません。")

    def refresh_log(self):
        # 一旦クリア
        for i in self.tree.get_children():
            self.tree.delete(i)

        sessions = tt.load_sessions()
        for idx, s in enumerate(sessions):
            start = s.get("start") or "-"
            end = s.get("end") or "-"
            secs = s.get("seconds")
            dur = tt.fmt_dur(secs) if isinstance(secs, int) else "-"
            task = s.get("task") or "(不明)"
            tag = "odd" if idx % 2 else "even"
            self.tree.insert("", "end", values=(start, end, dur, task), tags=(tag,))

    def on_csv(self):
        initial = os.path.join("data", "log_all.csv")
        path = filedialog.asksaveasfilename(
            title="CSVを書き出し",
            initialfile=os.path.basename(initial),
            initialdir=os.path.dirname(initial),
            defaultextension=".csv",
            filetypes=[("CSV", "*.csv")]
        )
        if not path:
            return
        try:
            tt.cmd_csv(path, with_hours=True)
            messagebox.showinfo("完了", f"CSVを書き出しました:\n{path}")
        except Exception:
            messagebox.showerror("CSV出力エラー", traceback.format_exc())


if __name__ == "__main__":
    app = TrackerGUI()
    app.mainloop()