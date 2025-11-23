"""
Script to create sample financial documents for testing.
"""

from pathlib import Path
import os

# Create data directory
data_dir = Path("./data")
data_dir.mkdir(exist_ok=True)

# Sample financial documents
documents = {
    "annual_report_2023.txt": """
Annual Report 2023 - Financial Summary

Company Overview:
Our company achieved strong financial performance in 2023, with total revenue reaching $125 million, 
representing a 25% increase compared to 2022. This growth was driven primarily by expansion into new 
markets and increased demand for our core products.

Financial Highlights:
- Total Revenue: $125,000,000 (2023) vs $100,000,000 (2022)
- Net Profit: $18,750,000 (2023) vs $12,000,000 (2022)
- Total Assets: $250,000,000 (2023) vs $200,000,000 (2022)
- Operating Margin: 15% (2023) vs 12% (2022)

Revenue Breakdown:
- Product Sales: $100,000,000 (80%)
- Service Revenue: $25,000,000 (20%)

Key Growth Drivers:
1. Market expansion into Asia-Pacific region
2. New product line launch in Q2 2023
3. Strategic partnerships with key distributors

Risk Factors:
- Economic uncertainty in global markets
- Increased competition in core markets
- Regulatory changes in key jurisdictions
- Currency exchange rate fluctuations

Outlook for 2024:
We project revenue growth of 20-25% for 2024, with continued focus on international expansion 
and product innovation. Operating margins are expected to improve to 16-18% through operational 
efficiency initiatives.
""",

    "financial_statements_q4.txt": """
Quarterly Financial Statements - Q4 2023

Income Statement:
Revenue: $35,000,000
Cost of Goods Sold: $21,000,000
Gross Profit: $14,000,000
Operating Expenses: $8,750,000
Operating Income: $5,250,000
Net Income: $4,200,000

Balance Sheet (as of Dec 31, 2023):
Assets:
- Cash and Cash Equivalents: $45,000,000
- Accounts Receivable: $28,000,000
- Inventory: $15,000,000
- Property, Plant & Equipment: $162,000,000
Total Assets: $250,000,000

Liabilities:
- Accounts Payable: $20,000,000
- Short-term Debt: $15,000,000
- Long-term Debt: $80,000,000
Total Liabilities: $115,000,000

Shareholders' Equity: $135,000,000

Cash Flow Statement:
Operating Activities: $22,000,000
Investing Activities: -$15,000,000
Financing Activities: -$5,000,000
Net Change in Cash: $2,000,000
""",

    "risk_assessment.txt": """
Risk Assessment Report 2023

Executive Summary:
This report identifies and assesses the principal risks facing our organization in 2023 
and outlines mitigation strategies.

Market Risks:
1. Economic Downturn Risk: Medium
   - Potential impact of global economic slowdown on demand
   - Mitigation: Diversified product portfolio and geographic presence

2. Competitive Pressure: High
   - Increased competition from new market entrants
   - Mitigation: Focus on innovation and customer relationships

3. Currency Fluctuation: Medium
   - Exposure to foreign exchange rate changes
   - Mitigation: Hedging strategies and local currency pricing

Operational Risks:
1. Supply Chain Disruption: Medium
   - Dependence on key suppliers
   - Mitigation: Multi-sourcing and inventory buffers

2. Technology Disruption: Low
   - Risk of technological obsolescence
   - Mitigation: Continuous R&D investment

Regulatory Risks:
1. Regulatory Changes: Medium
   - Changes in financial regulations
   - Mitigation: Compliance monitoring and legal review

2. Tax Policy Changes: Low
   - Potential changes in corporate tax rates
   - Mitigation: Tax planning and advisory services

Financial Risks:
1. Credit Risk: Low
   - Customer payment defaults
   - Mitigation: Credit checks and payment terms

2. Liquidity Risk: Low
   - Insufficient cash for operations
   - Mitigation: Cash reserves and credit facilities

Risk Rating Scale:
- Low: Minimal impact, well-controlled
- Medium: Moderate impact, requires monitoring
- High: Significant impact, active management required
""",

    "investment_strategy.txt": """
Investment Strategy and Capital Allocation 2023

Investment Philosophy:
Our investment strategy focuses on long-term value creation through strategic capital allocation 
across three key areas: organic growth, acquisitions, and shareholder returns.

Capital Allocation Framework:
1. Organic Growth (60%): $45 million
   - R&D and product development
   - Market expansion initiatives
   - Technology infrastructure

2. Strategic Acquisitions (25%): $18.75 million
   - Complementary businesses
   - Technology platforms
   - Market access opportunities

3. Shareholder Returns (15%): $11.25 million
   - Dividend payments
   - Share buybacks

Investment Priorities:
- Digital transformation initiatives
- Expansion into high-growth markets
- Sustainability and ESG investments
- Talent acquisition and development

Expected Returns:
- Organic growth investments: 15-20% IRR
- Strategic acquisitions: 12-18% IRR
- Technology investments: 20-25% IRR

Risk-Adjusted Returns:
All investments are evaluated using risk-adjusted return metrics, with minimum 
hurdle rates of 12% for low-risk and 18% for high-risk projects.
""",

    "regulatory_compliance.txt": """
Regulatory Compliance Report 2023

Compliance Overview:
Our organization maintains strict adherence to all applicable financial regulations, 
including SEC reporting requirements, GAAP accounting standards, and industry-specific regulations.

Key Compliance Areas:
1. Financial Reporting
   - Quarterly and annual SEC filings completed on time
   - GAAP-compliant financial statements
   - Independent audit completed with clean opinion

2. Tax Compliance
   - Federal and state tax returns filed timely
   - Transfer pricing documentation maintained
   - International tax compliance verified

3. Industry Regulations
   - Product safety standards compliance
   - Environmental regulations adherence
   - Labor and employment law compliance

4. Data Protection
   - GDPR compliance for EU operations
   - CCPA compliance for California operations
   - Data security measures implemented

Compliance Metrics:
- Regulatory filing timeliness: 100%
- Audit findings: Zero material findings
- Compliance training completion: 98%
- Policy violations: 0

Regulatory Changes Monitored:
- SEC disclosure requirements updates
- Tax law changes
- Industry-specific regulation updates
- International trade regulations
""",

    "market_analysis.txt": """
Market Analysis and Competitive Landscape 2023

Market Overview:
The global market for our products and services is estimated at $5 billion in 2023, 
with projected growth of 8-10% annually over the next five years.

Market Segmentation:
1. Enterprise Segment: $3 billion (60%)
   - Large corporations and institutions
   - High-value contracts
   - Long-term relationships

2. SMB Segment: $1.5 billion (30%)
   - Small and medium businesses
   - Growing market
   - Price-sensitive

3. Consumer Segment: $500 million (10%)
   - Individual consumers
   - Emerging opportunity
   - High growth potential

Competitive Position:
- Market Share: 12% (ranked #3)
- Key Competitors:
  1. Competitor A: 25% market share
  2. Competitor B: 18% market share
  3. Our Company: 12% market share
  4. Others: 45% market share

Competitive Advantages:
- Strong brand recognition
- Innovative product portfolio
- Excellent customer service
- Efficient operations

Market Trends:
- Digital transformation acceleration
- Sustainability focus
- Price competition intensifying
- Consolidation in industry
""",

    "revenue_analysis.txt": """
Revenue Analysis and Forecasting 2023

Revenue Performance:
Total revenue for 2023 reached $125 million, exceeding our target of $120 million. 
This represents a 25% year-over-year growth rate.

Revenue by Product Line:
1. Core Products: $75,000,000 (60%)
   - Growth rate: 20%
   - Market leader position

2. New Products: $30,000,000 (24%)
   - Growth rate: 45%
   - Launched in Q2 2023

3. Services: $20,000,000 (16%)
   - Growth rate: 15%
   - Recurring revenue model

Revenue by Geography:
- North America: $62,500,000 (50%)
- Europe: $37,500,000 (30%)
- Asia-Pacific: $18,750,000 (15%)
- Other: $6,250,000 (5%)

Revenue Trends:
- Q1: $28,000,000
- Q2: $30,000,000
- Q3: $32,000,000
- Q4: $35,000,000

Forecast for 2024:
- Q1: $38,000,000 (projected)
- Full Year: $150,000,000 - $156,000,000
- Growth Rate: 20-25%
""",

    "cost_structure.txt": """
Cost Structure Analysis 2023

Total Operating Costs: $106,250,000

Cost Breakdown:
1. Cost of Goods Sold: $75,000,000 (70.6%)
   - Raw materials: $45,000,000
   - Labor: $20,000,000
   - Manufacturing overhead: $10,000,000

2. Operating Expenses: $31,250,000 (29.4%)
   - Sales & Marketing: $15,000,000 (14.1%)
   - Research & Development: $8,000,000 (7.5%)
   - General & Administrative: $6,250,000 (5.9%)
   - Depreciation: $2,000,000 (1.9%)

Cost Efficiency Metrics:
- Gross Margin: 40%
- Operating Margin: 15%
- EBITDA Margin: 18%

Cost Trends:
- COGS as % of revenue: 60% (stable)
- Operating expenses as % of revenue: 25% (improving)
- R&D as % of revenue: 6.4% (increasing)

Cost Optimization Initiatives:
- Supply chain optimization: $2M savings
- Process automation: $1.5M savings
- Vendor consolidation: $1M savings
- Total savings: $4.5M annually
""",

    "balance_sheet_analysis.txt": """
Balance Sheet Analysis - Year End 2023

Assets: $250,000,000
Current Assets: $88,000,000 (35.2%)
- Cash: $45,000,000
- Accounts Receivable: $28,000,000
- Inventory: $15,000,000

Non-Current Assets: $162,000,000 (64.8%)
- Property, Plant & Equipment: $120,000,000
- Intangible Assets: $35,000,000
- Investments: $7,000,000

Liabilities: $115,000,000
Current Liabilities: $35,000,000 (30.4%)
- Accounts Payable: $20,000,000
- Short-term Debt: $15,000,000

Non-Current Liabilities: $80,000,000 (69.6%)
- Long-term Debt: $80,000,000

Shareholders' Equity: $135,000,000
- Common Stock: $50,000,000
- Retained Earnings: $85,000,000

Financial Ratios:
- Current Ratio: 2.51
- Debt-to-Equity: 0.59
- Asset Turnover: 0.50
- Return on Assets: 7.5%
- Return on Equity: 13.9%
""",

    "cash_flow_statement.txt": """
Cash Flow Statement 2023

Operating Activities: $22,000,000
- Net Income: $18,750,000
- Depreciation: $2,000,000
- Changes in Working Capital: $1,250,000
  - Accounts Receivable: -$3,000,000
  - Inventory: -$2,000,000
  - Accounts Payable: +$2,000,000
  - Other: +$4,250,000

Investing Activities: -$15,000,000
- Capital Expenditures: -$12,000,000
- Acquisitions: -$3,000,000

Financing Activities: -$5,000,000
- Debt Repayment: -$8,000,000
- Dividends Paid: -$3,000,000
- New Debt Issued: +$6,000,000

Net Change in Cash: +$2,000,000
Beginning Cash: $43,000,000
Ending Cash: $45,000,000

Free Cash Flow: $10,000,000
(Operating Cash Flow - Capital Expenditures)

Cash Flow Trends:
- Strong operating cash flow generation
- Positive free cash flow
- Adequate cash reserves for operations
- Capacity for strategic investments
"""
}

# Write documents
print("Creating sample financial documents...")
for filename, content in documents.items():
    filepath = data_dir / filename
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"Created: {filename}")

print(f"\nCreated {len(documents)} sample documents in {data_dir}/")
print("You can now run: python main.py --setup")

