#!/usr/bin/env python3
"""Generate 4166 Orient Pharma financial & outlook HTML report. Zero network."""
from pathlib import Path

OUT = Path(__file__).resolve().parents[2] / "augur_4166_orient_pharma_financial_outlook_20260827.html"
DL = Path(__file__).resolve().parents[2] / "download_4166_orient_pharma_report.html"

HTML = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<title>4166 友霖生技｜近五年財務分析與未來五年前景・全球競爭力報告</title>
<style>
  @font-face {
    font-family: "WQY";
    src: local("WenQuanYi Micro Hei"), local("文泉驛微米黑"), local("Droid Sans Fallback");
  }
  :root {
    --ink: #1c1917;
    --muted: #57534e;
    --line: #d6d3d1;
    --paper: #faf7f2;
    --card: #ffffff;
    --navy: #1e3a4c;
    --teal: #0f6b63;
    --gold: #b0893e;
    --loss: #b45309;
    --ok: #047857;
    --soft: #eef4f3;
  }
  * { box-sizing: border-box; }
  html, body {
    margin: 0; padding: 0;
    background: var(--paper);
    color: var(--ink);
    font-family: "WQY", "Noto Sans CJK TC", "Noto Sans TC", sans-serif;
    font-size: 11.5pt;
    line-height: 1.62;
  }
  @page {
    size: A4;
    margin: 16mm 15mm 18mm 15mm;
    @bottom-center {
      content: "友霖生技 Orient Pharma  ·  2026-08-27  ·  第 " counter(page) " 頁";
      font-size: 8pt;
      color: #78716c;
    }
  }
  .page { page-break-after: always; padding: 0; }
  .page:last-child { page-break-after: auto; }
  h1, h2, h3 { font-weight: 700; color: var(--navy); letter-spacing: 0.02em; }
  h1 { font-size: 22pt; line-height: 1.28; margin: 0 0 8px; }
  h2 { font-size: 15pt; border-bottom: 2px solid var(--navy); padding-bottom: 4px; margin: 18px 0 10px; }
  h3 { font-size: 12.5pt; margin: 14px 0 6px; color: var(--teal); }
  p { margin: 0 0 8px; }
  .kicker { color: var(--gold); font-size: 10pt; letter-spacing: 0.18em; text-transform: uppercase; }
  .sub { color: var(--muted); font-size: 10.5pt; }
  .cover {
    min-height: 245mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    background: linear-gradient(165deg, #1e3a4c 0%, #0f4c4a 62%, #134e4a 100%);
    color: #faf7f2;
    padding: 28mm 18mm 18mm;
    margin: -4mm -4mm 0;
  }
  .cover h1 { color: #fff; font-size: 28pt; }
  .cover .meta { font-size: 10.5pt; color: #d6ebe8; }
  .cover-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 22px; }
  .stat {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    padding: 10px 12px;
  }
  .stat b { display: block; font-size: 16pt; color: #fde68a; }
  .stat span { font-size: 9.5pt; color: #cfe8e4; }
  .warn {
    background: #fff7ed; border-left: 4px solid var(--gold);
    padding: 8px 12px; font-size: 10pt; color: #7c2d12; margin: 10px 0 14px;
  }
  .note {
    background: var(--soft); border-left: 4px solid var(--teal);
    padding: 8px 12px; font-size: 10pt; margin: 8px 0 12px;
  }
  table { width: 100%; border-collapse: collapse; font-size: 9.6pt; margin: 8px 0 12px; }
  th { background: var(--navy); color: #fff; font-weight: 600; padding: 5px 6px; text-align: right; }
  th:first-child, td:first-child { text-align: left; }
  td { padding: 4px 6px; border-bottom: 1px solid var(--line); text-align: right; }
  tbody tr:nth-child(even) { background: #f3f1ec; }
  .neg { color: var(--loss); }
  .pos { color: var(--ok); }
  .kpi { display: grid; grid-template-columns: repeat(4, 1fr); gap: 8px; margin: 8px 0 14px; }
  .kpi div { background: var(--card); border: 1px solid var(--line); padding: 8px 10px; }
  .kpi b { display: block; font-size: 13pt; color: var(--navy); }
  .kpi span { font-size: 8.8pt; color: var(--muted); }
  ul, ol { margin: 4px 0 10px 18px; padding: 0; }
  li { margin: 0 0 4px; }
  .two { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }
  .src { font-size: 8.8pt; color: #78716c; margin-top: -4px; margin-bottom: 10px; }
  .toc a { color: var(--navy); text-decoration: none; }
  .toc td { text-align: left; border: none; padding: 3px 0; }
  .toc tr { background: transparent !important; }
  footer.disc { font-size: 8.8pt; color: #78716c; border-top: 1px solid var(--line); padding-top: 8px; margin-top: 16px; }
  .badge { display: inline-block; background: var(--teal); color: #fff; font-size: 8pt; padding: 1px 6px; margin-right: 4px; }
  svg.chart { width: 100%; height: auto; }
  .swot td { text-align: left; vertical-align: top; }
  .swot th { text-align: left; }
</style>
</head>
<body>

<section class="page cover">
  <div>
    <div class="kicker" style="color:#fde68a;">EQUITY RESEARCH NOTE  ·  PUBLIC-DATA SYNTHESIS</div>
    <p style="margin:18px 0 6px;font-size:12pt;letter-spacing:.12em;">上櫃生技醫療  ·  TPEX:4166  ·  Orient Pharma Co., Ltd.</p>
    <h1>友霖生技醫藥<br>近五年財務分析<br>與未來五年前景・全球競爭力報告</h1>
    <p class="meta" style="margin-top:16px;max-width:92%;">涵蓋 2021–2025 全年合併財報、2026 年上半年／前七月營運、產品管線、美國 P4／505(b)(2) 路徑、學名藥與中樞神經／自體免疫產業結構，以及 2026–2030 情境推演。</p>
  </div>
  <div>
    <div class="cover-grid">
      <div class="stat"><b>NT$14.00 億</b><span>2025 年營收（年增 14.5%）</span></div>
      <div class="stat"><b>EPS 0.90 元</b><span>2025 年稅後 EPS（年增 87.5%）</span></div>
      <div class="stat"><b>+18.3%</b><span>2026 年前七月累計營收年增</span></div>
      <div class="stat"><b>負債比 11.8%</b><span>2026Q2；流動比 739%</span></div>
    </div>
    <p class="meta" style="margin-top:22px;">報告日：2026-08-27（股價收盤 24.70 元）　·　資料截止：2026 年 7 月營收、2026Q2 財報<br>
    編製：公開資訊整理（Yahoo 股市／愛玩股／PChome 股市／公司與媒體揭露）　·　非投資建議</p>
  </div>
</section>

<section class="page">
  <h2>0. 使用聲明與資料邊界</h2>
  <div class="warn">
    <b>本報告不是投資建議，也不是目標價或公司官方財測。</b>
    所有量化數字均追溯至公開財報彙編或公司／主管機關／主流財經媒體揭露；五年前景為<b>情境推演</b>（self-reported 分析），不是已實現結果。學名藥分潤合約細節未公開，不得把美國終端市場規模直接當成友霖帳上營收。
  </div>
  <p>本報告撰寫當日（2026-08-27）可取得的主要來源包括：Yahoo 股市（精誠資訊轉述之合併財報季報）、愛玩股年度損益、PChome 股市財務比率、公司官網與法說／重大訊息轉述（鉅亨、聯合、MoneyDJ、工商時報、科技新報、鏡週刊）、以及產業研究機構對學名藥／Tofacitinib／ADHD 市場的公開摘要。未使用 FinMind／FRED 即時取數，亦未取得公司未公開內部帳。</p>
  <h3>目錄</h3>
  <table class="toc">
    <tr><td>一、執行摘要</td></tr>
    <tr><td>二、公司定位與商業模式</td></tr>
    <tr><td>三、近五年財務分析（2021–2025 與 2026H1）</td></tr>
    <tr><td>四、資產負債、現金流與財務體質</td></tr>
    <tr><td>五、產品組合、管線與美國收成期</td></tr>
    <tr><td>六、產業未來五年前景</td></tr>
    <tr><td>七、全球競爭力評估</td></tr>
    <tr><td>八、公司未來五年情境推演（2026–2030）</td></tr>
    <tr><td>九、風險矩陣與觀察清單</td></tr>
    <tr><td>附錄：資料來源與計算說明</td></tr>
  </table>
</section>

<section class="page">
  <h2>一、執行摘要</h2>
  <p>友霖生技（Orient Pharma，TPEX:4166）是友華集團（4120）旗下、2008 年成立的研發製造型藥廠，2025-08-21 以承銷價 28 元上櫃。策略軸不是「廣譜學名藥殺價」，而是<b>高門檻劑型</b>：Paragraph IV（P4）困難學名藥＋FDA 505(b)(2) 改良型新藥，技術平台為 SMRT（半固態多層釋放）、MUPS（多單元圓粒）與 OROS（滲透壓控制釋放）。雲林虎尾廠採 PIC/S GMP／歐盟 GMP／美國 FDA 21CFR 規格興建，並取得美國 FDA、日本 MHLW、澳洲 TGA、英國 MHRA 等查廠／認證。</p>
  <div class="kpi">
    <div><b>營收 CAGR 31.9%</b><span>2021–2025（4.63→14.00 億）</span></div>
    <div><b>2023 轉盈</b><span>淨利 0.22→2025 年 2.08 億</span></div>
    <div><b>毛利率 56.5%</b><span>2025 年；2021 年僅約 31%</span></div>
    <div><b>市值約 60 億</b><span>243 百萬股 × 24.70；P/B 2.26</span></div>
  </div>
  <p><b>財務結論（近五年）：</b>公司已走過「研發燒錢→產品放量→上櫃補血」三段。2021–2022 仍虧損；2023 轉盈；2024–2025 本業槓桿打開，毛利率跳升至五成以上、營業利益率由負轉正至約 18.6%。2025 年上櫃後負債比自約 29% 降至 2026Q2 的 11.8%，流動比 739%，利息保障倍數約 79 倍——<b>償債與流動性已屬同業偏強</b>。2026 年前七月累計營收 8.90 億、年增 18.3%；上半年 EPS 0.40 元，獲利年增快於營收。</p>
  <p><b>前景結論（未來五年）：</b>產業面，全球學名藥市場公開預估約由 2025 年 4,263 億美元增至 2030 年 5,882 億美元（CAGR 約 6.7%）；真正對友霖有意義的是「專利懸崖＋複雜劑型」而非大宗學名藥。公司 2026 年 6 月取得美國 Tofacitinib XR 11mg 最終核准（22mg 暫時核准），經 Cipla／INVAGEN 商業化，管理層與通路目標為上市一年內 20–25% 市占——但<b>友霖認列的是供貨、里程碑與分潤，不是美國零售額全數入帳</b>。保守／基準／樂觀三種情境下，2030 年營收區間約 20–40 億元（見第八節），能否站穩取決於美國價格侵蝕速度、22mg 轉最終核准、以及阿茲海默／肺纖維化等管線是否在 2028 年前商業化。</p>
  <p><b>全球競爭力一句話：</b>在全球學名藥巨頭（Teva、Sandoz、Sun、Cipla 等）面前，友霖是「利基技術＋法規路徑」的小型挑戰者，不是規模玩家。相對台灣同業，它與漢達／美時／保瑞同屬「用美國法規紅利切高毛利」的第三條路，規模遠小於保瑞與美時，但 P4 成功案例與三套緩釋平台構成真實進入障礙。</p>
</section>

<section class="page">
  <h2>二、公司定位與商業模式</h2>
  <table>
    <thead><tr><th>項目</th><th style="text-align:left">內容</th></tr></thead>
    <tbody>
      <tr><td>公司</td><td style="text-align:left">友霖生技醫藥股份有限公司（Orient Pharma Co., Ltd.）</td></tr>
      <tr><td>代號／市場</td><td style="text-align:left">4166 / 櫃買中心生技醫療；上櫃日 2025-08-21；承銷價 28 元</td></tr>
      <tr><td>集團</td><td style="text-align:left">友華生技（4120）子公司；董事長蔡正弘；總經理黃春桐</td></tr>
      <tr><td>成立／廠區</td><td style="text-align:left">2008-02-01；雲林虎尾園區製藥廠（2010 完工）</td></tr>
      <tr><td>資本／股數</td><td style="text-align:left">資本額 24.3 億元；發行股約 2.43 億股（面額 10 元）</td></tr>
      <tr><td>人員</td><td style="text-align:left">集團揭露逾 180 人，研發約 45%，七成以上碩博士</td></tr>
      <tr><td>藥證布局</td><td style="text-align:left">管理層稱全球 12 國、約 50 張上市藥證（2025 年報導）</td></tr>
      <tr><td>美國 FDA 學名藥</td><td style="text-align:left">Carisoprodol、Miglitol、Pitavastatin、Glyburide、Vancomycin HCl；2026 年新增 Tofacitinib XR 11mg 最終核准</td></tr>
    </tbody>
  </table>
  <p class="src">來源：友華集團官網、環球生技、櫃買／公開資訊轉述、公司新聞稿與 2025–2026 媒體專訪。</p>
  <h3>2.1 營收怎麼組成</h3>
  <p>2024 年營收 12.23 億元中，<b>產品銷售 10.2 億（83.1%）</b>、<b>授權金與權利金約 1.47 億（12.1%）</b>，其餘為其他收入。這表示本業已不是「只靠授權金的研發公司」，但仍有可觀的授權／里程碑波動。鏡週刊引述總經理：第一支上市 P4 高血脂藥 <b>Pitavastatin（平脂）約貢獻五成營收</b>，台灣年營業額近 5 億；偏頭痛用藥 Trokendi（妥偏停）在台偏頭痛適應症市占近四成、超越同成分原廠。</p>
  <h3>2.2 為什麼毛利能到五成以上</h3>
  <p>一般口服學名藥毛利率常落在 20–40%。友霖 2023 年起毛利率躍升至 50%+，與三件事同時發生：(1) 自有高門檻緩釋產品取代低毛利代工；(2) 批次放大與產線優化；(3) 授權金（高增量利潤）佔比提升。2025 年管理層亦導入 LIMS／MES／APS，宣稱週期時間縮短約 35%、不良率降約 22%（法說轉述，屬公司自評）。</p>
</section>

<section class="page">
  <h2>三、近五年財務分析（2021–2025）</h2>
  <h3>3.1 合併損益摘要</h3>
  <p class="src">單位：新台幣億元。年度數字取自愛玩股合併損益（與公司 2024–2025 對外揭露一致：2024 營收 12.23 億、2025 營收 14.00 億、稅後 2.08 億、EPS 0.90）。毛利／營業利益由「營收−成本」「毛利−營業費用」推得。</p>
  <table>
    <thead>
      <tr><th>年度</th><th>營收</th><th>YoY</th><th>毛利</th><th>毛利率</th><th>營業利益</th><th>營益率</th><th>稅前</th><th>稅後淨利</th><th>淨利率</th><th>EPS</th></tr>
    </thead>
    <tbody>
      <tr><td>2021</td><td>4.63</td><td>+12.4%</td><td>1.42</td><td>30.7%</td><td class="neg">-1.34</td><td class="neg">-28.9%</td><td class="neg">-1.10</td><td class="neg">-1.03</td><td class="neg">-22.2%</td><td class="neg">-0.55</td></tr>
      <tr><td>2022</td><td>5.12</td><td>+10.6%</td><td>1.55</td><td>30.3%</td><td class="neg">-0.42</td><td class="neg">-8.2%</td><td class="neg">-0.41</td><td class="neg">-0.29</td><td class="neg">-5.7%</td><td class="neg">-0.15</td></tr>
      <tr><td>2023</td><td>8.90</td><td>+73.8%</td><td>4.69</td><td>52.7%</td><td>0.25</td><td>2.8%</td><td>0.23</td><td>0.22</td><td>2.5%</td><td>0.10</td></tr>
      <tr><td>2024</td><td>12.23</td><td>+37.4%</td><td>6.52</td><td>53.3%</td><td>1.58</td><td>12.9%</td><td>1.63</td><td>1.07</td><td>8.8%</td><td>0.48</td></tr>
      <tr><td>2025</td><td>14.00</td><td>+14.5%</td><td>7.90</td><td>56.4%</td><td>2.60</td><td>18.6%</td><td>2.45</td><td>2.08</td><td>14.9%</td><td>0.90</td></tr>
    </tbody>
  </table>
  <svg class="chart" viewBox="0 0 720 250" role="img" aria-label="營收與稅後淨利">
    <rect width="720" height="250" fill="#fff"/>
    <text x="12" y="22" font-size="13" fill="#1e3a4c">圖 1　合併營收（柱）與稅後淨利（線，億元）</text>
    <line x1="50" y1="190" x2="600" y2="190" stroke="#d6d3d1"/>
    <rect x="70" y="137" width="42" height="53" fill="#1e3a4c"/><text x="74" y="132" font-size="10" fill="#1e3a4c">4.63</text>
    <rect x="190" y="131" width="42" height="59" fill="#1e3a4c"/><text x="194" y="126" font-size="10" fill="#1e3a4c">5.12</text>
    <rect x="310" y="88" width="42" height="102" fill="#1e3a4c"/><text x="314" y="83" font-size="10" fill="#1e3a4c">8.90</text>
    <rect x="430" y="50" width="42" height="140" fill="#0f6b63"/><text x="430" y="45" font-size="10" fill="#0f6b63">12.23</text>
    <rect x="550" y="30" width="42" height="160" fill="#0f6b63"/><text x="554" y="25" font-size="10" fill="#0f6b63">14.00</text>
    <polyline fill="none" stroke="#b0893e" stroke-width="2.5" points="91,182 211,147 331,123 451,83 571,36"/>
    <circle cx="91" cy="182" r="4" fill="#b0893e"/><circle cx="211" cy="147" r="4" fill="#b0893e"/>
    <circle cx="331" cy="123" r="4" fill="#b0893e"/><circle cx="451" cy="83" r="4" fill="#b0893e"/>
    <circle cx="571" cy="36" r="4" fill="#b0893e"/>
    <text x="78" y="212" font-size="10" fill="#57534e">2021</text>
    <text x="198" y="212" font-size="10" fill="#57534e">2022</text>
    <text x="318" y="212" font-size="10" fill="#57534e">2023</text>
    <text x="438" y="212" font-size="10" fill="#57534e">2024</text>
    <text x="558" y="212" font-size="10" fill="#57534e">2025</text>
    <rect x="620" y="40" width="10" height="10" fill="#1e3a4c"/><text x="634" y="49" font-size="9" fill="#444">營收</text>
    <rect x="620" y="58" width="18" height="3" fill="#b0893e"/><text x="642" y="64" font-size="9" fill="#444">稅後淨利</text>
  </svg>
  <h3>3.2 解讀：兩階段跳躍，不是平滑成長</h3>
  <ol>
    <li><b>2021–2022 奠基虧損期：</b>營收仍在 4.6–5.1 億，毛利率約 30%，營業費用吃掉毛利，EPS −0.55／−0.15。這是雲林廠折舊＋研發＋尚未放量的典型結構。</li>
    <li><b>2023 結構轉折：</b>營收年增 73.8% 至 8.90 億，毛利率跳到 52.7%——產品組合明顯轉向高門檻自有品項。營業利益由負轉正，但營益率僅 2.8%，費用仍重。</li>
    <li><b>2024–2025 獲利收成：</b>營收續增但增速降到 37%→14.5%（高基期）；營業利益率 12.9%→18.6%，淨利率 8.8%→14.9%。2025 稅後 2.08 億、年增 94%，EPS 0.90 創當時新高。營收增速放緩、獲利增速更快，符合「固定成本已被營業額覆蓋」的營運槓桿。</li>
  </ol>
</section>

<section class="page">
  <h3>3.3 2026 年進度（截至 7 月／Q2）</h3>
  <p class="src">季報：Yahoo 股市（單位千元）。月營收：Yahoo／PChome。EPS 與公司累計揭露一致（2026H1 EPS 0.40）。</p>
  <table>
    <thead><tr><th>期間</th><th>營收</th><th>毛利</th><th>毛利率</th><th>營業利益</th><th>營益率</th><th>稅後淨利</th><th>EPS</th></tr></thead>
    <tbody>
      <tr><td>2025Q1</td><td>316,902</td><td>165,222</td><td>52.1%</td><td>61,204</td><td>19.3%</td><td>50,571</td><td>0.23</td></tr>
      <tr><td>2025Q2</td><td>325,546</td><td>183,573</td><td>56.4%</td><td>44,711</td><td>13.7%</td><td>18,774</td><td>0.08</td></tr>
      <tr><td>2025Q3</td><td>316,122</td><td>176,412</td><td>55.8%</td><td>51,331</td><td>16.2%</td><td>47,264</td><td>0.20</td></tr>
      <tr><td>2025Q4</td><td>441,808</td><td>265,514</td><td>60.1%</td><td>103,813</td><td>23.5%</td><td>91,829</td><td>0.40</td></tr>
      <tr><td>2026Q1</td><td>331,219</td><td>184,996</td><td>55.9%</td><td>46,638</td><td>14.1%</td><td>38,713</td><td>0.16</td></tr>
      <tr><td>2026Q2</td><td>427,078</td><td>225,428</td><td>52.8%</td><td>77,964</td><td>18.3%</td><td>57,440</td><td>0.24</td></tr>
      <tr><td><b>2026H1</b></td><td><b>758,297</b></td><td><b>410,424</b></td><td><b>54.1%</b></td><td><b>124,602</b></td><td><b>16.4%</b></td><td><b>96,153</b></td><td><b>0.40</b></td></tr>
    </tbody>
  </table>
  <ul>
    <li>2026H1 營收年增 <b>18.0%</b>（對 2025H1 之 642,448 千元）；稅後年增約 <b>38.7%</b>（對 69,345 千元）——獲利彈性仍在。</li>
    <li>2026 年前七月累計營收 <b>8.90 億、年增 18.33%</b>。6 月單月 1.83 億（創高、外銷佔比法人估破五成），7 月回落至 1.32 億（月減 28%、年增 20%）——外銷出貨具批次性，單月不宜外插全年。</li>
    <li>近四季（2025Q3–2026Q2）稅後合計約 2.35 億，對應 TTM EPS 約 0.97–0.99 元；Yahoo 本益比 25.26 倍（同業平均轉述約 50 倍，樣本異質，不宜直接當「便宜」證據）。</li>
    <li>2026Q2 毛利率 52.8%，低於 2025Q4 的 60.1%，可能反映產品組合／外銷供貨佔比變化，需看下半年 Tofacitinib 供貨毛利是拉升或被價格侵蝕。</li>
  </ul>
  <div class="note">管理層與法人口徑（2026-03 法說轉述；MoneyDJ 2026-07-23）：2026 年有機會 EPS「1 元以上」創新高、下半年優於上半年、年底前 22mg 劑型有望跟進、2026 年彌補累虧、2027 年具備配息條件。以上屬<b>未實現前瞻</b>，本報告不把它當已實現數字。</div>
  <h3>3.4 獲利品質</h3>
  <ul>
    <li><b>本業為主：</b>2025 營業利益約 2.60 億 vs 稅前 2.45 億，業外不是獲利引擎（2025 業外甚至小幅拖累）。</li>
    <li><b>所得稅：</b>2024 有效稅率偏高（愛玩股列約 34%），2025 回落約 15%；轉虧為盈後遞延稅資產／虧損扣抵會讓稅率波動，不宜用單年稅率外推。</li>
    <li><b>股本膨脹：</b>加權股數約 1.87 億（2021–22）→2.23 億（2023–24）→2.32 億（2025）→發行 2.43 億（上櫃後）。EPS 成長已部分被稀釋，但仍能創新高，顯示淨利增速快於股本。</li>
  </ul>
</section>

<section class="page">
  <h2>四、資產負債、現金流與財務體質</h2>
  <h3>4.1 財務結構（上櫃是分水嶺）</h3>
  <p class="src">單位：千元。2024Q4 取 HiStock／Yahoo；2025–2026 取 Yahoo 資產負債表；比率取 PChome 股市。</p>
  <table>
    <thead><tr><th>時點</th><th>總資產</th><th>總負債</th><th>權益</th><th>流動資產</th><th>流動負債</th><th>負債比</th><th>流動比</th><th>BPS</th></tr></thead>
    <tbody>
      <tr><td>2024Q4</td><td>2,520,582</td><td>732,998</td><td>1,787,584</td><td>728,426</td><td>487,250</td><td>29.1%</td><td>150%</td><td>8.01</td></tr>
      <tr><td>2025Q2</td><td>2,550,174</td><td>693,293</td><td>1,856,881</td><td>836,486</td><td>475,057</td><td>27.2%</td><td>176%</td><td>8.33</td></tr>
      <tr><td>2025Q3</td><td>2,887,108</td><td>413,557</td><td>2,473,551</td><td>1,183,848</td><td>222,314</td><td>14.3%</td><td>533%</td><td>10.18</td></tr>
      <tr><td>2025Q4</td><td>2,938,353</td><td>374,879</td><td>2,563,474</td><td>1,259,138</td><td>187,100</td><td>12.8%</td><td>673%</td><td>10.55</td></tr>
      <tr><td>2026Q2</td><td>3,011,929</td><td>353,900</td><td>2,658,029</td><td>1,277,643</td><td>172,799</td><td>11.8%</td><td>739%</td><td>10.94</td></tr>
    </tbody>
  </table>
  <p>2025Q3 融資現金流 <b>+2.98 億</b>、權益跳增約 6.2 億，對應 8 月上櫃現金增資與溢價公積。負債比腰斬、流動比由 1.5 倍升至 7 倍以上——這是「上市櫃補血」的典型圖像，不是本業突然把負債還光。固定資產約 6.4–6.8 億（雲林廠為核心生產資產），長期資金對固定資產比 2026Q2 達 426%，廠房並未過度舉債。</p>
  <h3>4.2 現金流量</h3>
  <table>
    <thead><tr><th>期間</th><th>營業現金流</th><th>投資現金流</th><th>融資現金流</th><th>自由現金流*</th></tr></thead>
    <tbody>
      <tr><td>2025 全年（四季合計）</td><td>359,858</td><td>-73,067</td><td>+218,029</td><td>+286,791</td></tr>
      <tr><td>2026Q1</td><td>74,364</td><td>+4</td><td>-4,026</td><td>+74,368</td></tr>
      <tr><td>2026Q2</td><td>52,806</td><td>-130,235</td><td>-4,049</td><td>-77,429</td></tr>
      <tr><td>2026H1</td><td>127,170</td><td>-130,231</td><td>-8,075</td><td>-3,061</td></tr>
    </tbody>
  </table>
  <p class="src">*Yahoo 定義之自由現金流＝營業＋投資現金流。2025 四季加總與單季列示可能有重分類／四捨五入差。</p>
  <ul>
    <li>2025 年營業現金流約 3.60 億，高於稅後 2.08 億，<b>盈餘有現金含量</b>，不是紙上獲利。</li>
    <li>2026Q2 投資現金流一次流出 1.30 億，拖累 H1 FCF 轉微負——需在年報確認是擴產／設備還是金融資產配置。對成長中的藥廠，這不一定是警訊，但代表「上櫃現金正在被拿去再投資」。</li>
    <li>利息保障倍數 2026H1 累計 79 倍、速動比 505%，<b>短期償債風險低</b>。</li>
  </ul>
  <h3>4.3 報酬率與周轉</h3>
  <p>2025 年 ROE 9.58%、ROA 7.88%（PChome 累計）。這在「剛轉盈＋剛增資」的公司算中等：分子（獲利）在長，分母（權益）因上櫃一次變大，ROE 會被暫時壓低。應收週轉 2025 年約 5.3 次、存貨週轉約 2.0 次——製藥存貨週期偏長符合處方藥特性。2026H1 ROE 累計僅 3.68%，屬半年數字，不可年化後直接當全年。</p>
  <h3>4.4 市場評價（描述、非建議）</h3>
  <p>2026-08-27 收盤 24.70 元，低於承銷價 28 元與 52 週高 29.60，高於 52 週低 18.53。以 2.43 億股計市值約 <b>60.0 億</b>；P/B 2.26（BPS 10.94）；TTM P/E 約 25 倍。週轉率低、日成交常僅數十至數百張，價格發現效率有限，評價波動會放大基本面以外的因素。</p>
</section>

<section class="page">
  <h2>五、產品組合、管線與美國收成期</h2>
  <h3>5.1 已上市主力</h3>
  <table>
    <thead><tr><th>產品／平台</th><th style="text-align:left">定位與公開進度</th></tr></thead>
    <tbody>
      <tr><td>Pitavastatin<br>平脂／同抑脂</td><td style="text-align:left">P4 高血脂；管理層稱約佔營收五成、台灣年營收近 5 億；已取越南、菲律賓藥證。高劑量劑型列 2025–2028 上市組合。</td></tr>
      <tr><td>Methydur 思有得<br>（SMRT）</td><td style="text-align:left">ADHD 505(b)(2) 改良型；2018 台灣藥證、2020 健保 2A；一天一次。2025 年銷 420 萬錠、年增近 30%。東南亞多國 NDA 中；為海外授權標的。</td></tr>
      <tr><td>Trokendi 妥偏停</td><td style="text-align:left">預防性偏頭痛；2018 健保收載；台灣偏頭痛適應症市占近 40%，超越同成分原廠。</td></tr>
      <tr><td>Vancomycin 口服</td><td style="text-align:left">美國市場；公司稱市占曾超越其他同成分；2026 年強調供給稀缺、通路重整後為下一波美國主力。</td></tr>
      <tr><td>糖尿病學名藥<br>（Miglitol／Glyburide）</td><td style="text-align:left">美國 FDA 學名藥證；公司稱曾為台灣首家取得該類美證之廠。</td></tr>
      <tr><td>OOK 長效針劑</td><td style="text-align:left">思覺失調；上市年約 7,000 支，2026 年前三月已銷約 5,000 支（法說）。</td></tr>
      <tr><td>Tofacitinib XR<br>1PL105</td><td style="text-align:left">類風濕等；輝瑞 Xeljanz XR 之 P4。2025-09 輝瑞撤訴；2026-06 11mg 最終核准、22mg 暫時核准；Cipla／INVAGEN 代理。</td></tr>
    </tbody>
  </table>
  <h3>5.2 Tofacitinib：機會與帳務邊界</h3>
  <p>公司揭露：原廠年銷曾約 <b>600 億台幣</b>，藥價政策後仍約 300 億；<b>2026-06 專利到期後學名藥市場估 30–45 億台幣</b>。政府標案市場供應商約 3 家、私人市場約 8 家。Cipla 目標上市一年內 <b>20–25% 市占</b>。合約含簽約金、核准／上市里程碑，銷售另計分潤。</p>
  <div class="warn">若以 20% × 45 億＝9 億直接加到友霖營收，會高估。友霖角色是「研製＋授權供貨」，美國終端銷售多半落在 Cipla／INVAGEN。友霖帳上較可能是：API／製劑供貨（接近製造毛利）＋里程碑（一次性）＋利潤分成（淨額）。在合約未公開前，本報告把美國 RA 線視為「中高機率的增量」而非「9 億確定營收」。</div>
  <p>11mg 已最終核准並於 2026-06 上市，7 月起認列銷貨——這與 6 月營收創高、7 月回落的型態相符（出貨集中）。22mg 仍為暫時核准，需待專利狀態允許才能量產，是 2026–2027 的選擇權而非已入袋。</p>
  <h3>5.3 2025–2028 管線（管理層口徑）</h3>
  <p>上櫃前業績發表：至 2028 年四大藥品上市銷售——<b>已取證高劑量降血脂、類風濕、阿茲海默、肺纖維化</b>。另喊「未來 3–4 年每年至少兩個新產品上市」。這些是執行層目標；阿茲海默與肺纖維化尚未見與 Tofacitinib 同級的核准公告，應列為較高不確定項目。</p>
</section>

<section class="page">
  <h2>六、產業未來五年前景（2026–2030）</h2>
  <h3>6.1 全球學名藥：量穩、結構轉向複雜劑型</h3>
  <p>The Business Research Company 公開摘要：全球學名藥市場 2025 年約 <b>4,263 億美元</b>，預估 2030 年 <b>5,882 億美元</b>，CAGR 約 <b>6.7%</b>。驅動因子是慢性病普及、政府壓藥價、專利懸崖。結構上，成長較快的不是「普通口服學名藥」（價格戰），而是<b>複雜學名藥、長效／緩釋、注射劑、505(b)(2) 改良型</b>。勤業眾信研究（鏡週刊轉述）：2022–2030 約 190 種藥物失去獨占——這是友霖這類公司的外部浪。</p>
  <h3>6.2 與友霖直接相關的治療領域</h3>
  <table>
    <thead><tr><th>領域</th><th style="text-align:left">公開市場描述</th><th style="text-align:left">對友霖的含義</th></tr></thead>
    <tbody>
      <tr><td>Tofacitinib<br>／JAK</td><td style="text-align:left">TBRC：2025 年約 34.2 億美元，2030 年約 65.3 億美元、CAGR 約 14%（含原廠與各種劑型，不是學名藥專指）。公司則稱美國學名藥化後市場縮至 30–45 億台幣。</td><td style="text-align:left">原廠市場縮小、學名藥量增價跌。友霖要的是「前段供應商＋合理分潤」，不是原廠規模。</td></tr>
      <tr><td>ADHD</td><td style="text-align:left">多家研調口徑分歧（治療市場百億美元級、CAGR 高個位數到約 9%）。台灣市場曾被內部評估「一年僅約 2 億」，但 Methydur 上市後把餅做大並貢獻可觀營收。</td><td style="text-align:left">台灣已驗證「劑型差異可擴市場」。海外（東南亞／中國／美歐日）仍是授權與藥證執行問題，不是台灣複製貼上。</td></tr>
      <tr><td>心血管<br>／血脂</td><td style="text-align:left">全球降血脂學名藥成熟、價格競爭激烈；高劑量／特殊鹽基／複方仍有利基。</td><td style="text-align:left">平脂已是現金牛，未來成長靠劑型延伸與東南亞，而非台灣再翻倍。</td></tr>
      <tr><td>中樞神經<br>長效針劑</td><td style="text-align:left">思覺失調長效針劑屬高遵醫囑、高單價利基；進入障礙在無菌／釋放曲線。</td><td style="text-align:left">OOK 仍小（千支級），但是產能與技術的選擇權。</td></tr>
    </tbody>
  </table>
  <h3>6.3 美國法規與政策五年變數</h3>
  <ul>
    <li><b>P4／ANDA：</b>第一家成功挑戰者可獲 180 天獨賣；代價是專利訴訟與 30 個月停留。友霖已走過輝瑞撤訴，11mg 風險大幅下降，22mg 尚未完全解除。</li>
    <li><b>505(b)(2)：</b>開發 2–5 年、成本遠低於 NCE，可能取得 3 年新臨床保護。這是友霖 Methydur 類產品的制度紅利。</li>
    <li><b>美國製藥政策：</b>2025 年媒體報導美國對進口品牌／專利藥關稅構想，以及「在美設廠」優惠。友霖產能在台灣、美國商業靠 Cipla——<b>沒有美國廠是中期結構弱點</b>（保瑞、美時已用併購補這塊）。學名藥是否適用同一套關稅仍需觀察，但不能假設零衝擊。</li>
    <li><b>藥價：</b>美國政府標案與 IRA 議價會壓縮學名藥價格；「20% 市占」若伴隨價格腰斬，分潤金額不會線性。</li>
  </ul>
  <h3>6.4 台灣製藥業五年座標</h3>
  <p>台灣製藥已拆成三條路：(1) 創新藥國際化（藥華等）；(2) CDMO／併購平台（保瑞）；(3) 高門檻學名藥＋美國通路（美時、漢達、友霖）。未來五年，第三條路的勝負手是<b>美國通路、在地製造政策、以及每年能落地幾個 ANDA／505(b)(2)</b>。友霖規模仍小（2025 營收 14 億 vs 保瑞／美時百億級），比較像「單點產品成功可改變公司」，而不是平台型穩態。</p>
</section>

<section class="page">
  <h2>七、全球競爭力評估</h2>
  <h3>7.1 評分卡（質化，非評級機構分數）</h3>
  <table>
    <thead><tr><th>構面</th><th>評等</th><th style="text-align:left">依據</th></tr></thead>
    <tbody>
      <tr><td>劑型／技術壁壘</td><td>中高</td><td style="text-align:left">SMRT／MUPS／OROS 三平台；緩釋與 P4 不是價格導向學名藥廠能快速複製。</td></tr>
      <tr><td>法規與查廠</td><td>高（相對台廠規模）</td><td style="text-align:left">FDA／EMA 路徑 GMP、日本外國製造認定、TGA、MHRA；已有多張美證。</td></tr>
      <tr><td>產品組合深度</td><td>中</td><td style="text-align:left">約 50 張藥證／12 國，但營收仍高度集中於血脂藥；單一產品風險高。</td></tr>
      <tr><td>美國商業化</td><td>中（依賴夥伴）</td><td style="text-align:left">Cipla／INVAGEN 補通路短板；代價是分潤與議價權。自有美國銷售團隊有限。</td></tr>
      <tr><td>製造規模與地理</td><td>中低</td><td style="text-align:left">單一雲林廠；無美國產能。批次放大中，但無法對標全球巨頭多廠網路。</td></tr>
      <tr><td>財務韌性</td><td>中高</td><td style="text-align:left">低負債、正營業現金流、上櫃後現金部位改善；規模小，抗長訟與價格戰的絕對金額仍有限。</td></tr>
      <tr><td>人才與臨床網絡</td><td>中</td><td style="text-align:left">研發佔比高、有醫師選題機制；上櫃目的之一即延攬人才。絕對人數仍少。</td></tr>
      <tr><td>品牌／ cotation</td><td>低</td><td style="text-align:left">全球處方端認知遠低於原廠與第一線學名藥巨頭；靠通路商品名與醫院標案。</td></tr>
    </tbody>
  </table>
  <h3>7.2 對標</h3>
  <table>
    <thead><tr><th>對象</th><th style="text-align:left">關係</th><th style="text-align:left">競爭意涵</th></tr></thead>
    <tbody>
      <tr><td>Cipla／INVAGEN</td><td style="text-align:left">夥伴（也是全球學名藥前段班）</td><td style="text-align:left">借力美國通路；長期需防「夥伴變競爭者」或續約條件轉差。</td></tr>
      <tr><td>輝瑞等原廠</td><td style="text-align:left">P4 對手</td><td style="text-align:left">Xeljanz 專利戰已撤訴，但原廠仍可用授權學名藥、藥價與新一代 JAK 反擊。</td></tr>
      <tr><td>其他 ANDA 廠<br>（私人市場約 8 家）</td><td style="text-align:left">直接價格競爭</td><td style="text-align:left">學名藥上市 12–24 個月常出現價格崩跌。20% 市占若發生，單位利潤可能同步下滑。</td></tr>
      <tr><td>美時（Alvogen）</td><td style="text-align:left">台灣同路人、規模大一階</td><td style="text-align:left">已有美國銷售與製造資產；友霖是產品型、美時是平台型。</td></tr>
      <tr><td>保瑞</td><td style="text-align:left">CDMO＋專科藥</td><td style="text-align:left">可能是代工夥伴也可能搶產能客戶；模式不同，規模不在同一量級。</td></tr>
      <tr><td>Teva／Sandoz／Sun</td><td style="text-align:left">全球量產學名藥</td><td style="text-align:left">友霖應持續避開大宗口服、留在複雜劑型；正面價格戰必敗。</td></tr>
    </tbody>
  </table>
  <h3>7.3 SWOT</h3>
  <table class="swot">
    <thead><tr><th>優勢 Strengths</th><th>劣勢 Weaknesses</th></tr></thead>
    <tbody>
      <tr>
        <td>三套緩釋平台；FDA 規格廠；已驗證 P4（血脂、RA）；台灣數個品項市占能打贏原廠；財務槓桿低；本業現金流轉正。</td>
        <td>營收規模小且集中；美國無自有銷售與工廠；上櫃後流通性低；累虧待 2026 年才規劃補完；研發管線後期能見度不均。</td>
      </tr>
    </tbody>
    <thead><tr><th>機會 Opportunities</th><th>威脅 Threats</th></tr></thead>
    <tbody>
      <tr>
        <td>2022–2030 專利懸崖；Tofacitinib 與 Vancomycin 美國放量；ADHD 出海；每年 2 個新品目標；東南亞／澳／加／中南美藥證。</td>
        <td>學名藥價格侵蝕；22mg／其他 ANDA 延遲；美國關稅與在地製造政策；夥伴分潤惡化；單一工廠營運中斷；匯率。</td>
      </tr>
    </tbody>
  </table>
</section>

<section class="page">
  <h2>八、公司未來五年情境推演（2026–2030）</h2>
  <p>以下為<b>分析情境</b>，不是財測。關鍵假設已寫明；學名藥分潤比例未知，故營收用區間而非單點。</p>
  <h3>8.1 共同前提</h3>
  <ul>
    <li>台灣血脂／ADHD／偏頭痛維持個位數到低雙位數成長，不再出現 2023 那種 70%+ 跳升。</li>
    <li>雲林廠無重大查廠缺失；美國夥伴關係存續。</li>
    <li>不假設再一次大規模現增；股本大致沿用 2.43 億股（實際仍可能因酬勞／可轉債變動）。</li>
    <li>匯率、藥價、關稅取「有干擾但不至於停業」的中性背景；極端政策列風險而非基準。</li>
  </ul>
  <table>
    <thead>
      <tr><th>情境</th><th>2030 營收</th><th>2030 淨利率</th><th>路徑摘要</th></tr>
    </thead>
    <tbody>
      <tr>
        <td>保守</td>
        <td>約 18–22 億</td>
        <td>8–12%</td>
        <td style="text-align:left">Tofacitinib 僅貢獻供貨＋有限分潤（每年約 1–2 億增量），價格快速侵蝕；22mg 延後；阿茲海默／肺纖維化未放量。美國營收比停在 30–40%。EPS 長期在 0.8–1.2 元附近波動。</td>
      </tr>
      <tr>
        <td>基準</td>
        <td>約 26–32 億</td>
        <td>12–16%</td>
        <td style="text-align:left">2026 營收約 16–18 億（對應前七月 +18% 與下半年美國出貨）；2027 年美國比重接近五成（法人口徑）；Tofacitinib＋Vancomycin＋既有品項穩步貢獻；2028 年前再落地 1–2 個高門檻品項。淨利隨營運槓桿溫和上升，2027 年起具備配息條件（管理層目標）。</td>
      </tr>
      <tr>
        <td>樂觀</td>
        <td>約 36–42 億</td>
        <td>16–20%</td>
        <td style="text-align:left">Cipla 達成 20–25% 市占且價格侵蝕慢於預期；22mg 2026 年底至 2027 轉正；Methydur 海外授權金到位；阿茲海默或肺纖維化其中一項在美／發達市場商業化。這需要「管線＋價格＋夥伴」同時偏多，機率低於基準。</td>
      </tr>
    </tbody>
  </table>
  <h3>8.2 基準路徑的年度邏輯（說明用）</h3>
  <ol>
    <li><b>2026：</b>美國收成元年。前七月已 +18%。Tofacitinib 11mg 自 7 月認列，H2 優於 H1 的機率較高，但 7 月已顯示出貨波動。累虧彌補是會計事件，對現金的意義小於對「能否配息」的法律意義。</li>
    <li><b>2027：</b>若配息啟動，投資人結構可能從純成長轉為成長＋殖利率，但配息率須看累虧補完後的可分配餘額。美國比重若真到五成，匯率與 Medicaid／標案價格會變成主要波動源。</li>
    <li><b>2028–2030：</b>勝負改為「第二、第三根支柱」是否出現。若仍靠平脂＋單一美國 P4，營收會在基準下沿鈍化，競爭力評等降為「單品公司」。</li>
  </ol>
  <div class="note">以 2021–2025 營收 CAGR 31.9% 外推到 2030（14×1.319^5≈55 億）<b>不合理</b>：那五年含轉盈與產品組合質變，高基期後應回到產業個位數到高個位數、加上單品放量的階梯，而不是持續 30% 複合成長。</div>
</section>

<section class="page">
  <h2>九、風險矩陣與觀察清單</h2>
  <table>
    <thead><tr><th>風險</th><th>機率*</th><th>衝擊</th><th style="text-align:left">監控點</th></tr></thead>
    <tbody>
      <tr><td>美國學名藥價格崩跌</td><td>高</td><td>高</td><td style="text-align:left">Tofacitinib 季出貨、毛利率、Cipla 通路庫存</td></tr>
      <tr><td>22mg 維持暫時核准／延後</td><td>中</td><td>中</td><td style="text-align:left">FDA／專利狀態重大訊息</td></tr>
      <tr><td>營收過度集中血脂藥</td><td>已存在</td><td>中高</td><td style="text-align:left">產品別營收（年報附註）是否降到 &lt;35%</td></tr>
      <tr><td>單一工廠中斷或查廠</td><td>低</td><td>極高</td><td style="text-align:left">FDA／TFDA 483、召回、產能利用率</td></tr>
      <tr><td>美國關稅／必須在美生產</td><td>中</td><td>中高</td><td style="text-align:left">政策文本是否納入學名藥；夥伴是否要求移地生產</td></tr>
      <tr><td>授權夥伴條件轉差</td><td>中</td><td>中</td><td style="text-align:left">里程碑認列節奏、權利金率（若揭露）</td></tr>
      <tr><td>管線時程跳票</td><td>中高</td><td>中</td><td style="text-align:left">阿茲海默／肺纖維化 IND／ANDA／上市公告</td></tr>
      <tr><td>流動性與評價波動</td><td>高</td><td>對股價高<br>對營運低</td><td style="text-align:left">日成交張數、承銷價 28 元的股東結構</td></tr>
    </tbody>
  </table>
  <p class="src">*機率為分析判斷（self-reported），非精算。</p>
  <h3>9.1 未來 12–24 個月優先觀察</h3>
  <ol>
    <li>2026Q3–Q4 毛利率是否因美國供貨升或降。</li>
    <li>年報／法說是否揭露美國營收占比（2025 約 30% 的管理層口徑能否被財報附註印證）。</li>
    <li>累虧彌補與 2027 配息是否進入董事會提案。</li>
    <li>22mg 最終核准時點。</li>
    <li>2026Q2 那筆 1.30 億投資現金流的內容（產能 vs 金融資產）。</li>
  </ol>
  <h2>十、總結</h2>
  <p>友霖近五年的財務故事清楚：<b>從虧損的研發製造廠，變成高毛利、低負債、本業獲利的小型特殊學名藥公司</b>。2021 到 2025，營收由 4.63 億到 14.00 億，稅後由 −1.03 億到 +2.08 億，毛利率由約 31% 到約 56%。2026 年前七月續增 18%，美國 Tofacitinib 已進入可出貨狀態，財務體質因上櫃而大幅強化。</p>
  <p>未來五年，產業尾風（專利懸崖、複雜學名藥、505(b)(2)）與公司能力是對得上的；全球競爭力則卡在<b>規模、美國在地製造與商業自主權</b>。它有機會在利基上成為「被 Cipla 這類巨頭需要的台灣技術廠」，但很難在 2030 年前長成美時／保瑞那一級的平台。基準情境把 2030 年營收看在約 26–32 億、獲利結構維持雙位數淨利率；要明顯超越，必須看到第二根美國支柱與管線兌現，而不是把單一 P4 的市占口號線性外推。</p>
  <footer class="disc">
    本文件由公開資料彙編，可能有轉述誤差；投資決策請以公司向公開資訊觀測站申報之財報、公開說明書與重大訊息為準。編製者不因本報告承擔任何交易損益責任。
  </footer>
</section>

<section class="page">
  <h2>附錄 A　資料來源</h2>
  <ol>
    <li>Yahoo 股市 4166.TWO：損益表、資產負債表、現金流量表、月營收（精誠資訊；查詢日 2026-08-27）。</li>
    <li>愛玩股 4166 年度損益、獲利能力季報。</li>
    <li>PChome 股市 4166 財務比率、個股概況（本益比、淨值、股本 24.3 億、市值）。</li>
    <li>HiStock 資產／權益表（2024Q4 補齊）。</li>
    <li>科技新報 2025-07-28：上櫃前業績、2024 營收結構、四大藥品、廠區認證。</li>
    <li>鏡週刊 2025-11-08：P4 策略、平脂營收貢獻、Trokendi 市占、每年兩產品、2027 海外營收超國內之管理層展望。</li>
    <li>鉅亨網 2026-03-24、聯合新聞網、工商時報、MoneyDJ 2026-03／07：Tofacitinib 時程、市占目標、累虧／配息口徑、6 月外銷。</li>
    <li>公司重大訊息轉述（BigGo／MarketScreener）：FDA 11mg 最終核准、22mg 暫時核准、INVAGEN 合約架構；先前 CRL 紀錄。</li>
    <li>友華集團官網、Pharmacompass、台灣臨床試驗平台：廠史與 FDA／日本認證時點。</li>
    <li>The Business Research Company 公開摘要：全球學名藥、Tofacitinib 市場規模（2025–2030）。</li>
    <li>櫃買／公開資訊：上櫃日 2025-08-21、承銷價 28 元。</li>
  </ol>
  <h2>附錄 B　關鍵計算</h2>
  <ul>
    <li>營收 CAGR 2021–2025＝(14.00/4.63)^(1/4)−1＝<b>31.9%</b>。</li>
    <li>毛利率＝(營收−營業成本)/營收；營業利益＝毛利−營業費用（愛玩股年度成本／費用）。</li>
    <li>2026H1 營收年增＝758,297/642,448−1＝<b>18.0%</b>；稅後年增＝96,153/69,345−1＝<b>38.7%</b>。</li>
    <li>2026Q2 負債比＝353,900/3,011,929＝<b>11.75%</b>；流動比＝1,277,643/172,799＝<b>7.39</b>。</li>
    <li>市值（2026-08-27）＝24.70×2.43 億股＝<b>60.0 億</b>；P/B＝24.70/10.94＝<b>2.26</b>。</li>
    <li>TTM 稅後（2025Q3–2026Q2）＝47,264+91,829+38,713+57,440＝<b>235,246 千元</b>。</li>
  </ul>
  <h2>附錄 C　版本</h2>
  <p>檔名：<code>augur_4166_orient_pharma_financial_outlook_20260827</code>　·　格式：HTML／PDF　·　語言：繁體中文　·　性質：公開資訊研究筆記，非受監管研究報告。</p>
</section>

</body>
</html>
"""

DOWNLOAD = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>下載｜4166 友霖生技財務與前景報告 PDF</title>
<style>
  body { font-family: "WenQuanYi Micro Hei", "Noto Sans CJK TC", sans-serif; max-width: 720px; margin: 48px auto; padding: 0 20px; color: #1c1917; background: #faf7f2; }
  a.btn { display: inline-block; background: #1e3a4c; color: #fff; text-decoration: none; padding: 14px 22px; font-size: 16px; }
  a.btn:hover { background: #0f6b63; }
  .sub { color: #57534e; }
</style>
</head>
<body>
  <p class="sub">TPEX:4166　·　報告日 2026-08-27</p>
  <h1>友霖生技近五年財務分析<br>與未來五年前景・全球競爭力報告</h1>
  <p>PDF 可直接下載（約十餘頁，A4）。內容含 2021–2025 財報、2026 上半年／前七月營運、產業與情境推演。</p>
  <p><a class="btn" href="augur_4166_orient_pharma_financial_outlook_20260827.pdf" download="4166_友霖生技_財務與前景報告_20260827.pdf">下載 PDF</a></p>
  <p class="sub">若瀏覽器未開始下載，請對連結按右鍵「另存連結」。HTML 版：<a href="augur_4166_orient_pharma_financial_outlook_20260827.html">線上閱讀</a>。</p>
  <p class="sub">本報告為公開資訊整理，非投資建議。</p>
</body>
</html>
"""

def main() -> None:
    OUT.write_text(HTML, encoding="utf-8")
    DL.write_text(DOWNLOAD, encoding="utf-8")
    print(f"wrote {OUT}")
    print(f"wrote {DL}")


if __name__ == "__main__":
    main()
