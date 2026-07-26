"""🎯 evolution 隔離負向測試(V2 Phase 2.1/I3):證明「0 違規」是「有在看」而非「沒在看」。

四條負向+一條正向:故意造出違規檔 → 掃描器必須抓到(紅);真樹 → 必須綠。
2026-07-26 前 `src/augur/evolution/` 是三重盲區(PIPELINE 不含/FORBIDDEN 不含/LITERALS 無 local_model_
字面),check_isolation() 回 0 違規是空집合誤讀;本測試把「掃描器真的會咬」固化為回歸鎖(#15)。
守 #15(負向實證)· I2/I3/I5(v2 §3.5)。執行:pytest tests/test_evolution_isolation.py -q
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "src"))

from augur.audit.import_isolation import (  # noqa: E402
    EVOLUTION_PANEL_LITERALS,
    EVOLUTION_SRC_FORBIDDEN_IMPORTS,
    FORBIDDEN,
    LAIEVO_LITERALS,
    _ast_import_scan,
    _string_ref_violations,
    check_isolation,
)


def test_real_tree_is_clean():
    """正向:現行真樹零違規(本測試存在的前提;紅了=有人真的打穿隔離,先修樹再談測試)。"""
    assert check_isolation() == []


def test_pipeline_importing_evolution_is_caught(tmp_path):
    """負向1:預測管線 import augur.evolution → 必須紅(I3;augur.evolution 已入 FORBIDDEN)。"""
    assert "augur.evolution" in FORBIDDEN
    bad = tmp_path / "sneaky_feature.py"
    bad.write_text("from augur.evolution.behavior_rubric import judge\n", encoding="utf-8")
    hits = _ast_import_scan([tmp_path], FORBIDDEN, "import", "test")
    assert len(hits) == 1 and "augur.evolution" in hits[0]


def test_pipeline_touching_local_model_literal_is_caught(tmp_path):
    """負向2:預測管線字面觸及 local_model_* 表 → 必須紅(LAIEVO 帳本=行為樣本非真兆,界線-A)。"""
    bad = tmp_path / "sneaky_sql.py"
    bad.write_text('Q = "SELECT gold_answer FROM local_model_gold_sample"\n', encoding="utf-8")
    hits = _string_ref_violations([tmp_path], LAIEVO_LITERALS, "laievo")
    assert hits and "local_model_" in hits[0]


def test_evolution_importing_pipeline_is_caught(tmp_path):
    """負向3:evolution 反向 import 預測管線(I2 單向依賴)→ 必須紅。"""
    bad = tmp_path / "sneaky_reverse.py"
    bad.write_text("from augur.features import panel\n", encoding="utf-8")
    hits = _ast_import_scan([tmp_path], EVOLUTION_SRC_FORBIDDEN_IMPORTS, "evolution-import", "test")
    assert len(hits) == 1 and "augur.features" in hits[0]


def test_evolution_touching_panel_literal_is_caught(tmp_path):
    """負向4:evolution 字面觸及 feature_values/prodset(I2 零寫入之字面前哨)→ 必須紅。"""
    bad = tmp_path / "sneaky_panel.py"
    bad.write_text('Q = "INSERT INTO feature_values VALUES (1)"\n', encoding="utf-8")
    hits = _string_ref_violations([tmp_path], EVOLUTION_PANEL_LITERALS, "evolution-panel")
    assert hits and "feature_values" in hits[0]


def test_ddl_home_exemption_voids_on_purity_loss():
    """負向5:DDL 住所豁免綁純度——同名檔一旦 import augur.core 即失豁免(定義≠存取)。"""
    from augur.audit.import_isolation import _DDL_HOME, _is_exempt
    pure = "LEDGER = ('local_model_eval_run',)\n"
    impure = "from augur.core import db\nLEDGER = ('local_model_eval_run',)\n"
    assert _is_exempt(_DDL_HOME, pure) is True
    assert _is_exempt(_DDL_HOME, impure) is False
