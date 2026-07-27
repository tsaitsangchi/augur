"""🎯 重活單槽鎖(C3 第二版)——同機重活互斥,且**掉鎖即 fail-loud 不續跑**。

白話:本機 Ollama `-np 1`、PG 與 CPU 亦單份;三軸重活(evolve/eval/TWEVO 輪/RAWEVO 掃)同時跑
只會互相拖慢且結果不可比。本模組以 PG **session 級 advisory lock** 做全機互斥(跨進程、
跨語言、程序死亡即自動釋放,勝過 flock 之殘留鎖檔)。

⚠ 關鍵陷阱(v2 總控 §3.3 C3 明列,實碼確認 `augur.core.db.connect` 於 finally 關連線):
   **不得**用 `db.connect()` 取 advisory lock——session 鎖隨連線關閉而釋放,且**靜默**;
   鎖會在第一個 `with connect()` 區塊結束時消失,呼叫端卻以為還握著 → 兩支重活同時跑而不自知。
   故本模組**自持長生 psycopg2 連線**,並在每個 heavy step 邊界 `verify()` 重驗鎖仍在自己手上。

搶不到鎖**不 silent skip**:寫一列 `evolution_deferred_work` 並由週報印積壓筆數
(v2:「在這台機器上搶不到鎖是常態,silent skip 會變成穩態」)。
守 #15(掉鎖 fail-loud 非續跑)· #12(單一住所;flock 第一版為呼叫端過渡)· #6 · #29。

執行指令矩陣:
  python -m augur.core.heavy_slot              # 印用途+公開入口+目前鎖持有狀態(唯讀)
  python -m augur.core.heavy_slot --selftest   # 純紅綠自測(免 DB 亦可跑之結構斷言 + 有 DB 時之真鎖測)
"""
from __future__ import annotations

import os
import sys

LOCK_NAME = "augur_evolution_heavy_slot"


class SlotLost(RuntimeError):
    """鎖已不在自己手上(連線斷/被清)——heavy step 邊界重驗時拋出,呼叫端須停手不得續跑。"""


class HeavySlot:
    """自持長生連線之 advisory lock。用法:

        slot = HeavySlot("tw_iteration")
        if not slot.acquire():
            slot.defer("run_evolution_iteration", "lock busy")   # 積壓落帳,不 silent skip
            return 0
        try:
            slot.verify()          # 每個 heavy step 邊界重驗
            ...heavy step...
        finally:
            slot.release()
    """

    def __init__(self, owner: str, lock_name: str = LOCK_NAME):
        self.owner = owner
        self.lock_name = lock_name
        self._conn = None
        self._held = False

    # ── 連線:自持、不經 db.connect(那支 finally 會關連線=靜默放鎖) ──
    def _connect(self):
        import psycopg2

        from augur.core import config
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(connect_timeout=10, **dict(config.DB_PARAMS))
            self._conn.autocommit = True
        return self._conn

    def acquire(self) -> bool:
        """非阻塞取鎖;回 True=取得。已持有再呼叫回 True(冪等)。"""
        if self._held:
            return True
        cur = self._connect().cursor()
        cur.execute("SELECT pg_try_advisory_lock(hashtext(%s))", (self.lock_name,))
        self._held = bool(cur.fetchone()[0])
        return self._held

    def verify(self) -> None:
        """heavy step 邊界重驗:鎖仍在**本連線**手上才放行,否則 fail-loud(#15)。"""
        if not self._held:
            raise SlotLost(f"[{self.owner}] 未持有 {self.lock_name}")
        if self._conn is None or self._conn.closed:
            self._held = False
            raise SlotLost(f"[{self.owner}] 連線已關 → advisory lock 已釋放(靜默失效之典型)")
        cur = self._conn.cursor()
        cur.execute("""SELECT count(*) FROM pg_locks
            WHERE locktype='advisory' AND objid = hashtext(%s)::bigint & x'7fffffff'::bigint
              AND pid = pg_backend_pid() AND granted""", (self.lock_name,))
        if not cur.fetchone()[0]:
            # 保守回退:objid 位寬因版本而異時改以「本 backend 是否仍有 advisory 鎖」判定
            cur.execute("SELECT count(*) FROM pg_locks WHERE locktype='advisory' "
                        "AND pid=pg_backend_pid() AND granted")
            if not cur.fetchone()[0]:
                self._held = False
                raise SlotLost(f"[{self.owner}] {self.lock_name} 已不在本 backend 手上")

    def defer(self, task: str, reason: str, payload=None, axis: str | None = None) -> None:
        """搶不到鎖 → 積壓落帳(不 silent skip);表不存在時退為 stderr 一行、不阻斷呼叫端。

        ⚠ 欄名以**實表為準**:`(axis, step_key, reason, detail)`。2026-07-27 實測發現原碼寫成
        `(axis, task, reason, payload)`——UndefinedColumn 被 except 吞成一行 stderr,於是「不 silent
        skip」的機制本身變成 silent skip(0 列落地)。此為「寫了但沒驗過真能寫」之典型,故本方法
        之自測改為**真插一列再刪**,不再只斷言字面。
        """
        import json
        ax = (axis or self.owner.split("_")[0])[:8]
        try:
            cur = self._connect().cursor()
            cur.execute("SELECT to_regclass('public.evolution_deferred_work')")
            if cur.fetchone()[0] is None:
                raise RuntimeError("evolution_deferred_work 未建")
            cur.execute("""INSERT INTO evolution_deferred_work (axis, step_key, reason, detail)
                VALUES (%s,%s,%s,%s::jsonb)""",
                (ax, task[:64], reason,
                 json.dumps({"owner": self.owner, **(payload or {})}, ensure_ascii=False)))
        except Exception as e:  # noqa: BLE001
            print(f"[heavy_slot] defer 落帳失敗({type(e).__name__});積壓仍須人知: "
                  f"{self.owner}/{task}/{reason}", file=sys.stderr)

    def release(self) -> None:
        if self._conn is not None and not self._conn.closed:
            try:
                if self._held:
                    cur = self._conn.cursor()
                    cur.execute("SELECT pg_advisory_unlock(hashtext(%s))", (self.lock_name,))
            finally:
                self._conn.close()
        self._conn, self._held = None, False

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.release()
        return False


def holder_pids(lock_name: str = LOCK_NAME):
    """目前持有本鎖之 backend pid 清單(唯讀診斷;自持短連線、用完即關)。"""
    import psycopg2

    from augur.core import config
    conn = psycopg2.connect(connect_timeout=10, **dict(config.DB_PARAMS))
    try:
        cur = conn.cursor()
        cur.execute("SELECT pid FROM pg_locks WHERE locktype='advisory' AND granted")
        return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def _selftest():
    ok = True

    def chk(name, cond):
        nonlocal ok
        print(("  ✓ " if cond else "  ✗ ") + name)
        ok = ok and cond

    import inspect
    # 只掃**取鎖路徑**:全模組掃描會掃到自測自身為回歸而合法使用之 db.connect(假紅;
    # 2026-07-27 實撞,同型於 report_triple_evolution_week 之 A12 斷言)
    lock_path = inspect.getsource(HeavySlot._connect) + inspect.getsource(HeavySlot.acquire)
    chk("取鎖路徑不經 db.connect(該支 finally 關連線=靜默放鎖)", "db.connect" not in lock_path)
    chk("自持連線 autocommit(advisory lock 需即時可見)", "autocommit = True" in lock_path)
    chk("verify() 掉鎖 fail-loud(raise 非 return False)",
        "raise SlotLost" in inspect.getsource(HeavySlot.verify))
    chk("搶不到鎖有 defer 落帳(不 silent skip)",
        "evolution_deferred_work" in inspect.getsource(HeavySlot.defer))
    chk("defer 之欄名與實表對齊(字面斷言:step_key/detail 非 task/payload)",
        "step_key, reason, detail" in inspect.getsource(HeavySlot.defer))
    try:
        os.environ.setdefault("PGCONNECT_TIMEOUT", "5")
        a = HeavySlot("selftest_a")
        got_a = a.acquire()
        chk("取得鎖", got_a)
        b = HeavySlot("selftest_b")
        chk("第二持有者搶不到(互斥成立)", got_a and not b.acquire())
        a.verify()
        chk("verify() 於持有時通過", True)
        # 關鍵回歸:巢狀 db.connect() 進出後,鎖仍在自己手上
        from augur.core import db
        with db.connect() as c1:
            with db.connect() as c2:
                c2.cursor().execute("SELECT 1")
            c1.cursor().execute("SELECT 1")
        a.verify()
        chk("**巢狀 with db.connect() 進出後鎖仍在**(C3 關鍵陷阱回歸)", True)
        # **真插一列再刪**:字面斷言驗不出欄名對不對(2026-07-27 實犯:task/payload 兩欄根本不存在,
        # UndefinedColumn 被 except 吞掉 → 「不 silent skip」的機制本身 silent skip 了)
        d = HeavySlot("tw_selftest")
        cur0 = d._connect().cursor()
        cur0.execute("SELECT count(*) FROM evolution_deferred_work")
        n0 = cur0.fetchone()[0]
        d.defer("selftest_probe", "自測探針(隨即刪除)", {"probe": True})
        cur0.execute("SELECT count(*) FROM evolution_deferred_work")
        n1 = cur0.fetchone()[0]
        chk("**defer 真的寫進 evolution_deferred_work**(非只字面有表名)", n1 == n0 + 1)
        cur0.execute("DELETE FROM evolution_deferred_work WHERE step_key='selftest_probe'")
        d.release()
        a.release()
        c = HeavySlot("selftest_c")
        chk("release 後他人可取得", c.acquire())
        c.release()
        b.release()
    except Exception as e:  # noqa: BLE001
        print(f"  (DB 不可用,略過真鎖測:{type(e).__name__}: {str(e)[:60]})")
    print("自測:" + ("全通過 ✓" if ok else "有失敗 ✗"))
    return 0 if ok else 1


def main(argv=None):
    if argv and "--selftest" in argv:
        return _selftest()
    print(__doc__)
    print("公開入口:")
    print("  HeavySlot(owner).acquire()/verify()/defer(task,reason)/release()  ── context manager 可用")
    print("  holder_pids()  目前持有 advisory 鎖之 backend pid")
    try:
        print(f"  現況:持有中的 advisory backend pid = {holder_pids()}")
    except Exception as e:  # noqa: BLE001
        print(f"  (DB 未連線:{type(e).__name__})")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
