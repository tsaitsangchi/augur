# authority_tier 71 active 源逐源提案表(AI 草案;逐源人核後才落 DDL)

> **性質**:[I] 提案材料(G3 評估之後續;`AUTHORITY-TIER-go` 拍板前之人核清單)。
> **紀律**:tier=信任判斷=**決策層**——本表每列僅為建議;你逐源核/改後,我出 migration 把核定值
> 落 `knowledge_source.authority_tier`(一欄+backfill,零其他 schema 變動)。
> 級別語意(rdai 憲章 §3.3 移植):T0 標準/法規|T1 同儕審查/國家機構|T2 產業權威數據|
> T3 廠商宣稱|T4 媒體/社群|internal 內部 ground truth|NA_philosophy 素養層不適用。

| source_key | adapter | domain | license | **建議 tier** | 理由(一句) |
|---|---|---|---|---|---|
| `arxiv_search` | arxiv | general | cc_whitelist | **T1** | 預印本索引——T1 但**未同儕審查**,引用宜註記 preprint |
| `chembl_molecules` | generic_json | chemistry | cc_whitelist | **T2** | 機構數據庫／官方倉儲(數據權威,非逐篇同儕審查) |
| `cod_crystals` | generic_json | chemistry | cc_whitelist | **T2** | 機構數據庫／官方倉儲(數據權威,非逐篇同儕審查) |
| `crossref_works` | crossref | general | metadata_only | **T1** | 同儕審查文獻／OA 學術索引 |
| `ctext_books` | generic_json | philosophy | public_domain | **NA_philosophy** | 公版原典(哲學素養層) |
| `curation_accounting_mgmt` | manual_file | accounting_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_biology` | manual_file | biology | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_business_mgmt` | manual_file | business_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_chemistry` | manual_file | chemistry | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_electronics` | manual_file | electronics | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_energy_materials` | manual_file | energy_materials | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_finance_mgmt` | manual_file | finance_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_investment_mgmt` | manual_file | investment_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_mgmt_philosophy` | manual_file | mgmt_philosophy | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_organization_mgmt` | manual_file | organization_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_physics` | manual_file | physics | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_production_mgmt` | manual_file | production_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_rd_mgmt` | manual_file | rd_mgmt | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `curation_solar_materials` | manual_file | solar_materials | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `datacite_dois` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `dblp_cs` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `dbpedia_accounting_mgmt` | dbpedia_sparql | accounting_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_abel_prize` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_copley_medal` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_fields_medal` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_kyoto_prize` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_lasker_award` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_millennium_technology_prize` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_nobel_in_literature` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_nobel_peace_prize` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_pritzker_architecture_prize` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_turing_award` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_wolf_prize_in_chemistry` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_award_wolf_prize_in_physics` | dbpedia_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_biology` | dbpedia_sparql | biology | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_business_mgmt` | dbpedia_sparql | business_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_chemistry` | dbpedia_sparql | chemistry | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_electronics` | dbpedia_sparql | electronics | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_energy_materials` | dbpedia_sparql | energy_materials | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_finance_mgmt` | dbpedia_sparql | finance_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_investment_mgmt` | dbpedia_sparql | investment_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_mgmt_philosophy` | dbpedia_sparql | mgmt_philosophy | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_organization_mgmt` | dbpedia_sparql | organization_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_philosophers` | dbpedia_sparql | philosophy | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_physics` | dbpedia_sparql | physics | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_production_mgmt` | dbpedia_sparql | production_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `dbpedia_rd_mgmt` | dbpedia_sparql | rd_mgmt | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `doaj_articles` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `eric_education` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `europepmc` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `gbif_species` | generic_json | biology | cc_whitelist | **T2** | 機構數據庫／官方倉儲(數據權威,非逐篇同儕審查) |
| `gutendex_search` | gutendex | philosophy | public_domain | **NA_philosophy** | 公版原典(哲學素養層) |
| `hal_france` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `inspire_hep` | generic_json | physics | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `internet_archive` | internet_archive | general | public_domain | **NA_philosophy** | 公版書目/原典總集(素養層;零量化價值,tier 判準不適用) |
| `manual_curation` | manual_file | management | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `openalex_authors` | openalex | general | metadata_only | **T1** | 同儕審查文獻／OA 學術索引 |
| `openalex_works` | openalex | general | metadata_only | **T1** | 同儕審查文獻／OA 學術索引 |
| `openlibrary_books` | openlibrary | general | public_domain | **NA_philosophy** | 公版書目/原典總集(素養層;零量化價值,tier 判準不適用) |
| `osti_energy` | osti | energy_materials | public_domain | **T2** | 機構數據庫／官方倉儲(數據權威,非逐篇同儕審查) |
| `plos_search` | generic_json | general | cc_whitelist | **T1** | 同儕審查文獻／OA 學術索引 |
| `pubchem_compounds` | generic_json | chemistry | public_domain | **T2** | NIH PubChem 機構數據庫 |
| `rdai_knowhow_docs` | local_files | solar_rd | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `semantic_scholar` | semantic_scholar | general | metadata_only | **T1** | 同儕審查文獻／OA 學術索引 |
| `ttai_erp_pilot` | manual_file | erp_tiptop | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `ttai_knowhow_docs` | local_files | erp_semantics | owned_local | **internal** | 內部 ground truth／人工策展(T0-internal 類比,不塞 T0) |
| `uniprot_proteins` | generic_json | biology | cc_whitelist | **T2** | UniProt 機構數據庫(EBI/SIB/PIR) |
| `unpaywall_doi` | unpaywall | general | metadata_only | **T1** | OA 定位服務(隨所解析文獻之 T1 屬性) |
| `wikidata_api` | generic_json | general | cc_whitelist | **T4** | 社群編纂(同 wikidata_sparql) |
| `wikidata_people` | wikidata_sparql | general | metadata_only | **T4** | 社群編纂(DBpedia/Wikidata)——線索與人物索引用,不得單獨作定量依據 |
| `zenodo_records` | generic_json | general | cc_whitelist | **T2** | 機構數據庫／官方倉儲(數據權威,非逐篇同儕審查) |

**建議分佈**:NA_philosophy 4 · T1 14 · T2 7 · T4 28 · internal 18(=71;四筆原未入規則者已逐一手核填入)。

**T3/T4 前置閘提醒**:現役近乎零 T3——閘先立(「T3 只支撐宣稱、T4 不得單獨定量」),未來接
廠商/媒體源時判準已在。**核定方式**:直接在本檔改 tier 欄後說一聲,或列出你的逐源裁定;
`AUTHORITY-TIER-go` 拍板後我出 migration(一欄+核定值 backfill)。
