import PyPDF2

pdffiles = ["Sample1.pdf", "Sample2.pdf"]
merger = PyPDF2.PdfMerger()

for filename in pdffiles:
    merger.append(filename)  # You can directly pass filename

# Write merged file
with open("Merged.pdf", "wb") as f:
    merger.write(f)

merger.close()
