"""augur advisor — L3 博學投資大師顧問前端(學習計畫 P5)。

把量化本體的**真實預測數字**(唯讀 PredictionPayload)+ 哲學素養庫的**逐字檢索引文**,
翻成引經據典的人話。數字 100% 唯讀轉述、引文 100% 公版逐字可溯源;
生成後過防幻覺閘(guard)。**顧問對預測/哲學表皆唯讀、零寫回**(憲章 v1.17.0 隔離)。

L3 與量化本體之界面:僅經 PredictionPayload(as-of 快照凍結、frozen);
顧問不改一個數字、不讓哲學凌駕模型結論(逆向鏡只輸出風險視角、非相反行動)。
"""
from augur.advisor.payload import PredictionPayload, StockPick
from augur.advisor.advise import advise
from augur.advisor.guard import guard

__all__ = ["PredictionPayload", "StockPick", "advise", "guard"]
