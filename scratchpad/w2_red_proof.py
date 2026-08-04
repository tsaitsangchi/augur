"""#35 先驗紅：對 reconcile_channel_columns 之每個受保護行為逐一注入突變，親證自測會紅。

每個突變＝把「宣稱被保護的行為」故意弄壞；若自測仍 rc=0，該鎖就是恆真假斷言。
"""
import contextlib
import io
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
import reconcile_channel_columns as M  # noqa: E402


def run_selftest_rc() -> int:
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        rc = M._selftest()
    return rc, buf.getvalue()


MUTANTS = []


def mutant(name, why):
    def deco(fn):
        MUTANTS.append((name, why, fn))
        return fn
    return deco


@mutant("M1 只回第一個問題碼", "壓成單一 verdict 會靜默吃掉第二個問題（type_unregistered+pk_mismatch）")
def m1():
    orig = M.reconcile_column
    M.reconcile_column = lambda c, l: orig(c, l)[:1]
    return lambda: setattr(M, "reconcile_column", orig)


@mutant("M2 兩側皆無時靜默回「對得上」", "fail-open：不存在之欄被判為對得上")
def m2():
    orig = M.reconcile_column

    def broken(c, l):
        if c is None and l is None:
            return ()
        return orig(c, l)
    M.reconcile_column = broken
    return lambda: setattr(M, "reconcile_column", orig)


@mutant("M3 型別比對永遠放行", "把 type_mismatch 拿掉＝catalog 型別漂移查不出來")
def m3():
    orig = M.reconcile_column
    M.reconcile_column = lambda c, l: tuple(i for i in orig(c, l) if i != "type_mismatch")
    return lambda: setattr(M, "reconcile_column", orig)


@mutant("M4 auto_pairable 只看有無問題、不看桶", "多值表會被誤判為可機械自動配對")
def m4():
    orig = M.auto_pairable
    M.auto_pairable = lambda bucket, issues: not issues
    return lambda: setattr(M, "auto_pairable", orig)


@mutant("M5 auto_pairable 忽略唱讀問題", "catalog 這把尺自己對不上時仍自動配對＝把錯欄名寫進 Registry")
def m5():
    orig = M.auto_pairable
    M.auto_pairable = lambda bucket, issues: bucket == "B2_單值欄"
    return lambda: setattr(M, "auto_pairable", orig)


@mutant("M6 桶邊界 off-by-one", "5 值欄被歸進 B3＝難度分佈失真、外推跟著錯")
def m6():
    orig = M.expansion_bucket

    def broken(n_live, n_value):
        if n_live and 0 < n_value <= 5:
            return "B3_2-4值欄" if n_value > 1 else "B2_單值欄"
        return orig(n_live, n_value)
    M.expansion_bucket = broken
    return lambda: setattr(M, "expansion_bucket", orig)


@mutant("M7 allocate_strata 寫死配置", "不再按母體比例＝分層抽樣是裝飾品")
def m7():
    orig = M.allocate_strata
    M.allocate_strata = lambda counts, n: {k: (1 if i < min(n, len(counts)) else 0)
                                           for i, k in enumerate(sorted(counts))}
    return lambda: setattr(M, "allocate_strata", orig)


@mutant("M8 allocate_strata 無視 n 上限", "n 大於母體時虛報樣本數")
def m8():
    orig = M.allocate_strata

    def broken(counts, n):
        total = sum(counts.values())
        if total == 0 or n == 0:
            return {k: 0 for k in counts}
        return {k: max(1, round(v * n / total)) for k, v in counts.items()}
    M.allocate_strata = broken
    return lambda: setattr(M, "allocate_strata", orig)


@mutant("M9 sample_order 忽略 seed", "seed 不參與雜湊＝『可復現抽樣』宣稱是假的")
def m9():
    orig = M.sample_order
    M.sample_order = lambda ids, seed: sorted(ids)
    return lambda: setattr(M, "sample_order", orig)


@mutant("M10 table_absent 不標記", "無實體表之通道被當成正常通道計入可展開面")
def m10():
    orig = M._reconcile_binding

    def broken(b, live, cat):
        r = orig(b, live, cat)
        r["issues"] = tuple(i for i in r["issues"] if i != "table_absent")
        return r
    M._reconcile_binding = broken
    return lambda: setattr(M, "_reconcile_binding", orig)


def main():
    base_rc, _ = run_selftest_rc()
    print(f"基線（未突變）自測 rc={base_rc}  {'✓ 綠' if base_rc == 0 else '✗ 基線就紅，先修'}")
    if base_rc != 0:
        return 1
    print(f"\n{'突變':<34}{'rc':<5}{'結果':<8}為何這個鎖必須紅")
    print("-" * 118)
    all_red = True
    for name, why, setup in MUTANTS:
        restore = setup()
        rc, out = run_selftest_rc()
        restore()
        red = rc != 0
        all_red &= red
        nfail = out.count("✗")
        print(f"{name:<34}{rc:<5}{('紅 ✓ (' + str(nfail) + ' 條失敗)') if red else '綠 ✗ 恆真!':<8}  {why}")
    post_rc, _ = run_selftest_rc()
    print("-" * 118)
    print(f"還原後自測 rc={post_rc}（須回綠，證明突變已完全還原）")
    print(f"\n總結：{len(MUTANTS)} 個突變全部驗紅＝{all_red}；還原回綠＝{post_rc == 0}")
    return 0 if (all_red and post_rc == 0) else 1


if __name__ == "__main__":
    sys.exit(main())
