import PyPDF2
pdffiles=["Sample1.pdf", "Sample2.pdf"]
merger=PyPDF2.PdfMerger()
for filename in pdffiles:
    pdfFile=open(filename,"rb")
    pdfReader=PyPDF2.PdfReader(pdfFile)
    merger.append(pdfReader)
pdfFile.close()
merger.write("Merged.pdf")