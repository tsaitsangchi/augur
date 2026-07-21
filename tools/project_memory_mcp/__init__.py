"""project-memory-mcp：全 repo「非治理輔助語料」之唯讀語意記憶層。

設計見 reports/PROJECT-MEMORY-MCP-PLAN.md。純 stdlib、stdio JSON-RPC 2.0。

範圍界線（硬邊界）：僅索引非治理輔助語料；治理權威語料（constitution/、
生效 specs/*-SPECIFICATION.md、RULING-*、AMENDMENT-LOG.md）一律排除，其查詢
改走 constitution-mcp。讀寫分離：server 僅匯入唯讀模組；寫入隔離於 index.py。
"""

__version__ = "0.1.0"
