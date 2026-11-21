"""data.json の健全性チェック。異常があれば終了コード1。
使い方: python tools/check_health.py [data.json] [--now 2026-11-21T10:00:00]
"""
import json, sys
from datetime import datetime, timedelta

STALE_HOURS = 2      # この時間以上更新がなければ「止まってる」
FAIL_STREAK = 3      # 連続失敗がこの回数以上で警告

def main():
    args = sys.argv[1:]
    now = datetime.now()
    if "--now" in args:
        i = args.index("--now"); now = datetime.fromisoformat(args[i + 1]); del args[i:i + 2]
    path = args[0] if args else "data.json"
    d = json.load(open(path, encoding="utf-8"))
    problems = []
    gen = datetime.fromisoformat(d["generated_at"])
    if now - gen > timedelta(hours=STALE_HOURS):
        problems.append(f"data.json が {now - gen} 更新されていません（最終 {gen}）")
    for a in d["accounts"]:
        runs = sorted(a["runs"], key=lambda r: r["at"])
        name = a.get("handle")
        if not runs:
            problems.append(f"[{name}] 実行記録なし"); continue
        streak = 0
        for r in reversed(runs):
            if r["ok"]: break
            streak += 1
        if streak >= FAIL_STREAK:
            problems.append(f"[{name}] 直近 {streak} 回連続で失敗（最新: {runs[-1]['note'] or '理由なし'}）")
        recent = runs[-24:]
        errs = [r for r in recent if r.get("note") == "エラー"]
        print(f"[{name}] 最新実行 {runs[-1]['at']} / 直近{len(recent)}回中 成功{sum(r['ok'] for r in recent)}・エラー{len(errs)}")
    for p in problems: print("NG:", p)
    print("OK" if not problems else f"{len(problems)} 件の異常")
    sys.exit(1 if problems else 0)

if __name__ == "__main__":
    main()
