import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
output_path = os.path.join(PROJECT_ROOT, "data", "raw", "sample_statement.pdf")

doc = SimpleDocTemplate(output_path, pagesize=letter)
styles = getSampleStyleSheet()
elements = []

elements.append(Paragraph("Sample Bank Statement", styles["Title"]))
elements.append(Paragraph("Account Holder: Presley Oluoch | Account: XXXX-4521", styles["Normal"]))
elements.append(Spacer(1, 0.3 * inch))

# Realistic transaction table - deliberately includes messy real-world quirks:
# mixed date formats, a currency symbol, and one blank description
data = [
    ["Date", "Description", "Amount", "Type"],
    ["2024-01-05", "Salary Deposit", "85,000", "Credit"],
    ["01/08/2024", "Grocery Store - Naivas", "-3,450", "Debit"],
    ["Jan 12 2024", "Electricity Bill KPLC", "-2,100", "Debit"],
    ["2024-01-15", "", "-500", "Debit"],
    ["01/20/2024", "Rent Payment", "-25,000", "Debit"],
    ["Jan 25 2024", "Netflix Subscription", "$15.99", "Debit"],
    ["2024-01-28", "Transfer from Savings", "10,000", "Credit"],
]

table = Table(data, colWidths=[1.3 * inch, 2.5 * inch, 1.2 * inch, 1 * inch])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1F4E79")),
    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
    ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ("FONTSIZE", (0, 0), (-1, -1), 9),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F2F2F2")]),
]))

elements.append(table)
doc.build(elements)

print("Sample PDF statement created at:", output_path)