from typing import List, Dict, Any, Optional
import re

# ============================================================================
# SQL Query Mapping
# ============================================================================

class SQLQueryMapper:
    """Maps user intents to SQL queries based on inventory schema"""
    
    def __init__(self):
        self.query_patterns = self._build_query_patterns()
    
    def _build_query_patterns(self) -> List[Dict[str, Any]]:
        """Define all supported query patterns with their SQL mappings"""
        return [
            {
                "patterns": [
                    r"how many assets",
                    r"total assets",
                    r"count.*assets",
                    r"number of assets"
                ],
                "sql": "SELECT COUNT(*) AS AssetCount FROM Assets WHERE Status <> 'Disposed';",
                "answer_template": "You have {AssetCount} assets in your inventory.",
                "intent": "asset_count_total"
            },
            {
                "patterns": [
                    r"how many assets.*by site",
                    r"assets.*per site",
                    r"asset count.*site",
                    r"breakdown.*site",
                    r"show.*assets.*by site",
                    r"show.*assets.*site",
                    r"list.*assets.*by site",
                    r"assets.*by site"
                ],
                "sql": """SELECT s.SiteName, COUNT(*) AS AssetCount 
FROM Assets a 
JOIN Sites s ON s.SiteId = a.SiteId 
WHERE a.Status <> 'Disposed' 
GROUP BY s.SiteName 
ORDER BY AssetCount DESC;""",
                "answer_template": "Here's the asset count by site: {results}",
                "intent": "asset_count_by_site"
            },
            {
                "patterns": [
                    r"total value.*assets.*site",
                    r"asset value.*site",
                    r"value.*assets.*per site"
                ],
                "sql": """SELECT s.SiteName, SUM(ISNULL(a.Cost, 0)) AS TotalValue
FROM Assets a
JOIN Sites s ON s.SiteId = a.SiteId
WHERE a.Status <> 'Disposed'
GROUP BY s.SiteName
ORDER BY TotalValue DESC;""",
                "answer_template": "Here's the total asset value by site: {results}",
                "intent": "asset_value_by_site"
            },
            {
                "patterns": [
                    r"assets purchased.*this year",
                    r"assets.*bought.*year",
                    r"how many.*purchased.*current year"
                ],
                "sql": """SELECT COUNT(*) AS AssetCount
FROM Assets
WHERE YEAR(PurchaseDate) = YEAR(GETDATE())
AND Status <> 'Disposed';""",
                "answer_template": "You purchased {AssetCount} assets this year.",
                "intent": "assets_purchased_this_year"
            },
            {
                "patterns": [
                    r"which vendor.*most assets",
                    r"vendor.*supplied.*most",
                    r"top vendor.*assets"
                ],
                "sql": """SELECT TOP 1 v.VendorName, COUNT(*) AS AssetCount
FROM Assets a
JOIN Vendors v ON v.VendorId = a.VendorId
WHERE a.Status <> 'Disposed'
GROUP BY v.VendorName
ORDER BY AssetCount DESC;""",
                "answer_template": "The vendor that supplied the most assets is {VendorName} with {AssetCount} assets.",
                "intent": "top_vendor_by_assets"
            },
            {
                "patterns": [
                    r"total billed.*last quarter",
                    r"bills.*last quarter",
                    r"amount billed.*quarter"
                ],
                "sql": """SELECT SUM(TotalAmount) AS TotalBilled
FROM Bills
WHERE BillDate >= DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()) - 1, 0)
AND BillDate < DATEADD(QUARTER, DATEDIFF(QUARTER, 0, GETDATE()), 0);""",
                "answer_template": "The total billed amount for the last quarter is ${TotalBilled:,.2f}.",
                "intent": "total_billed_last_quarter"
            },
            {
                "patterns": [
                    r"how many.*open.*purchase orders",
                    r"pending.*purchase orders",
                    r"open.*po"
                ],
                "sql": """SELECT COUNT(*) AS OpenPOCount
FROM PurchaseOrders
WHERE Status = 'Open';""",
                "answer_template": "There are {OpenPOCount} open purchase orders currently pending.",
                "intent": "open_purchase_orders"
            },
            {
                "patterns": [
                    r"assets.*by category",
                    r"breakdown.*category",
                    r"assets.*per category",
                    r"show.*assets.*category",
                    r"list.*assets.*category"
                ],
                "sql": """SELECT Category, COUNT(*) AS AssetCount
FROM Assets
WHERE Status <> 'Disposed'
GROUP BY Category
ORDER BY AssetCount DESC;""",
                "answer_template": "Here's the breakdown of assets by category: {results}",
                "intent": "assets_by_category"
            },
            {
                "patterns": [
                    r"sales orders.*customer.*last month",
                    r"how many.*sales orders.*month",
                    r"so.*created.*customer"
                ],
                "sql": """SELECT c.CustomerName, COUNT(*) AS SOCount
FROM SalesOrders so
JOIN Customers c ON c.CustomerId = so.CustomerId
WHERE so.SODate >= DATEADD(MONTH, -1, GETDATE())
GROUP BY c.CustomerName
ORDER BY SOCount DESC;""",
                "answer_template": "Here are the sales orders created for customers last month: {results}",
                "intent": "sales_orders_by_customer_last_month"
            },
            {
                "patterns": [
                    r"list.*vendors",
                    r"show.*vendors",
                    r"all vendors"
                ],
                "sql": """SELECT VendorCode, VendorName, Email, Phone
FROM Vendors
WHERE IsActive = 1
ORDER BY VendorName;""",
                "answer_template": "Here are all active vendors: {results}",
                "intent": "list_vendors"
            },
            {
                "patterns": [
                    r"list.*customers",
                    r"show.*customers",
                    r"all customers"
                ],
                "sql": """SELECT CustomerCode, CustomerName, Email, Phone
FROM Customers
WHERE IsActive = 1
ORDER BY CustomerName;""",
                "answer_template": "Here are all active customers: {results}",
                "intent": "list_customers"
            },
            {
                "patterns": [
                    r"list.*sites",
                    r"show.*sites",
                    r"all sites"
                ],
                "sql": """SELECT SiteCode, SiteName, City, Country
FROM Sites
WHERE IsActive = 1
ORDER BY SiteName;""",
                "answer_template": "Here are all active sites: {results}",
                "intent": "list_sites"
            }
        ]
    
    def match_intent(self, message: str) -> Optional[Dict[str, Any]]:
        """Match user message to a query pattern"""
        message_lower = message.lower().strip()
        
        for pattern_def in self.query_patterns:
            for pattern in pattern_def["patterns"]:
                if re.search(pattern, message_lower):
                    return {
                        "sql": pattern_def["sql"],
                        "answer_template": pattern_def["answer_template"],
                        "intent": pattern_def["intent"]
                    }
        
        return None
