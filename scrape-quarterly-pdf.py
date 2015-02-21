import pdfquery

# load the pdf from file path
pdf = pdfquery.PDFQuery('data/test.pdf')
pdf.load()
# find the anchor point of the "# Apts" label
label = pdf.pq('LTTextLineHorizontal:contains("# Apts")')
left_corner = float(label.attr('x0'))
bottom_corner = float(label.attr('y0'))
# grab the unit count below the # Apts label
apt_count = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (left_corner, bottom_corner-20, left_corner+100, bottom_corner+10)).text()

print apt_count

