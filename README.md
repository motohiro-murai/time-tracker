# time-tracker
Pythonで作成した作業時間記録アプリ（CLI + Tkinter GUI対応
## 特徴
- CLIからタスク開始・終了を記録
- GUIでタスクの一覧を表示
- CSVにエクスポート可能

## 使い方
### CLI
```bash
python time_tracker.py start 勉強
python time_tracker.py stop
python time_tracker.py log --csv data/log_all.csv

## GUI の使い方

以下のコマンドでGUIを起動できます。

```bash
python time_tracker_gui.py
