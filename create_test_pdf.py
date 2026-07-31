from reportlab.pdfgen import canvas

def create_test_pdf():
    c = canvas.Canvas("test_rag.pdf")
    c.setFont("Helvetica", 12)
    c.drawString(100, 750, "The secret password to access the mainframe is 'ORION-77'.")
    c.drawString(100, 730, "The facility is located at 123 Alpha Base on Mars.")
    c.drawString(100, 710, "Only personnel with Level 5 clearance may enter.")
    c.save()
    print("Created test_rag.pdf")

if __name__ == "__main__":
    create_test_pdf()
