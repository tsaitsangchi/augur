# AUTO-LIFT 常駐旗 · GO

date: 2026-08-12  
kind: ops_go  
status: GO  
open: kh_opt_stepwise **K3**  
prior: `audits/AUTO-LIFT-1C-PILOT-GO-20260812.md`（試點禁 systemd）

## 授權（覆寫試點禁令）
1. advisor **常駐** `AUGUR_KH0_ANSWER_AUTO_LIFT=1`（systemd Environment／`install_services.sh`）  
2. 碼預設仍 **off**（無 env＝關；單元測／裸行程不誤開）  
3. 可一鍵關：drop-in 刪或 `Environment=…=0` 後 reload  

## 禁
默裝 ingest timer；web／對話 approve；抬 >KH2；silent promote。
