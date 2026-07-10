"""本地審議引擎(Local Ultracode Engine)— 讓本地 AI 以「多視角提 claim × 確定性 oracle 裁決 × 自我迭代」工作。

核心鐵則(承前身計畫機械鎖):LLM(qwen)只准提「帶錨點+指定確定性 verifier」的 pending claim;
`status='confirmed'` 唯 is_deterministic=true 之 verdict 可寫;無 oracle 可驗=強制 escalate 人裁,
LLM 永不自判 confirmed。工具是誠實的,弱模型只需會提出可驗證的宣稱。
"""
