"""scripts 個別可執行 bootstrap — 把專案 src/ 插入 sys.path,讓每支 script 不需 PYTHONPATH 前置即可直接執行。

🎯 每支 script 於 import augur 前 `import _bootstrap` 即可個別執行(任何 cwd、任何呼叫方式)。
守 #12(路徑邏輯單一住此)。與 `pip install -e .` 並存相容(已裝則本檔為 no-op 等效)。

執行指令矩陣：
  python scripts/_bootstrap.py           # 印用途＋確認 src/ 已插入 sys.path（副作用＝path 插入）
  # 本檔非業務 CLI；消費方式＝其他 scripts 於 import augur 前 `import _bootstrap`
"""
import sys
from pathlib import Path

_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))


if __name__ == "__main__":
    print("augur scripts/_bootstrap：把 repo 之 src/ 插入 sys.path（#12 單一住所）")
    print(f"  src={_src}")
    print(f"  in_sys_path={str(_src) in sys.path}")
    print("消費：其他 scripts 於 import augur 前 `import _bootstrap`；已 pip install -e . 時等效 no-op")
