---
name: quota-error-discipline
description: "限額錯誤處置紀律 — API 限額錯誤≠定論,先請用戶看儀表再下判斷;失誤成本實例 2026-07-04"
metadata: 
  node_type: memory
  type: feedback
  originSessionId: 9009c955-58bc-46c5-904b-ed515e2be723
---

2026-07-04 實證教訓:workflow 代理收到「out of usage credits · resets Jul 10」API 錯誤,我如實轉述但**框架成「7/10 前不能再開 agent/workflow」的定論**——用戶因此多買了 $45 credits;事後其儀表顯示 session 56%/weekly 52%(有餘裕)。

**Why**:AI 讀不到用量儀表(CLAUDE #28 明文),API 限額錯誤訊息的「池別」與「重置點」措辭可能與用戶儀表看到的錶不同支(session 5h/weekly/加購 credits 是不同錶);單次錯誤也可能是暫時性。把單一錯誤訊息當定論=以偏概全,會驅動用戶做出花錢決策。

**How to apply**:撞任何 Claude 限額錯誤時——(1) 停止 fan-out(#28 護欄照舊);(2) 回報時**明說「我讀不到儀表,這是 API 錯誤原文,請以你面板為準」**,不宣稱「X 時間前不能用」;(3) 幾分鐘後用最小成本探測代理重試一次再定調;(4) 重型 workflow 一次只跑一個、不併發疊加(當日兩次 session 撞頂皆因百萬 token 級 workflow 排太密)。相關:[[augur-project-map]]。
