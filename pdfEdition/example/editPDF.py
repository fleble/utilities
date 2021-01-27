import sys

from PyPDF2 import PdfFileWriter, PdfFileReader
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.graphics.shapes import Rect
from reportlab.lib.colors import yellow, red, black, white

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

pdfmetrics.registerFont(TTFont('dejavu-sans', 'DejaVuSans.ttf'))
pdfmetrics.registerFont(TTFont('dejavu-sans-bold', 'DejaVuSans-Bold.ttf'))
pdfmetrics.registerFont(TTFont('dejavu-sans-it', 'DejaVuSans-Oblique.ttf'))


def editPDF(inFile, outFile):

    ## Edit the PDF

    packet = io.BytesIO()
    # create a new PDF with Reportlab
    can = canvas.Canvas(packet, pagesize=letter)
    # blank former CMS Prelimiary
    can.setFillColorRGB(1,1,1)
    can.rect(118,390,200,20, stroke=False, fill=True)
    # write new CMS Prelimiary
    can.setFillColorRGB(0,0,0)
    can.setFont("dejavu-sans-bold", 15)
    can.drawString(160, 393.5, "CMS")
    can.setFont("dejavu-sans-it", 13)
    can.drawString(200, 393.5, "Preliminary")
    # add 10**-6 on y axis
    posX = 118
    posY = 392
    can.setFont("dejavu-sans", 12)
    can.drawString(posX, posY, "x10")
    can.setFont("dejavu-sans", 9.5)
    can.drawString(posX+23.5, posY+5, "-6")
    can.setFont("dejavu-sans", 12)
    # blank y label
    can.setFillColorRGB(1,1,1)
    can.rect(70,175,20,80, stroke=False, fill=True)
    # write new y label
    can.setFillColorRGB(0,0,0)
    can.rotate(90)
    can.drawString(200, -87, "Rate")
    # indicate that changes are finished
    can.showPage()
    can.save()


    ## Save the edited PDF

    # move to the beginning of the StringIO buffer
    packet.seek(0)
    new_pdf = PdfFileReader(packet)
    # read your existing PDF
    existing_pdf = PdfFileReader(open(inFile, "rb"))
    output = PdfFileWriter()
    # add the "watermark" (which is the new pdf) on the existing page
    page = existing_pdf.getPage(0)
    page.mergePage(new_pdf.getPage(0))
    output.addPage(page)
    # finally, write "output" to a real file
    outputStream = open(outFile, "wb")
    output.write(outputStream)
    outputStream.close()


if (__name__ == '__main__'):
    editPDF(sys.argv[1], sys.argv[2])
    # to test a single file:
    #editPDF("name.pdf", "test.pdf")
