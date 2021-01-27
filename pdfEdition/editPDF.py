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

    # edit the PDF here, see example in example/
    # ...

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

