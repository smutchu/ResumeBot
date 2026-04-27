
import fitz



def readpdf():
    arrpage=[]
    with fitz.open("/Users/hravs/Python_projects/ResumeBot/data/Test_Resume_Sample-merged.pdf") as file:
        for page in file:
            tabs = page.get_text()
            arrpage.append(tabs)
        return "\n\n".join(arrpage).strip()

combined=readpdf()
print(combined)