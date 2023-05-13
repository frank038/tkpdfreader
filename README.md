# tkpdfreader
by frank038
v. 0.5.6

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY. Anyone can use and modified it for any purpose.

A pdf reader in Python3/tkinter based on PyMuPDF by Ruikai Liu and Jorj X. McKie. Required: PyMuPDF (included, no need to download it; Notice: in the fitz folder there is a compiled library file). This program uses custom file and folder dialogs instead of the default tkinter dialogs. They are a slightly modified version of the project by Juliette Monsel (j_4321).
Update: if a package with the name python3-fitz exists in your distro, just install it and move over the fitz folder of this program.

How to start this program: pdfViewer.py FILE_TO_OPEN [FONT_SIZE]

Implemented: Toc, page selection/next/previous, zoom, page rotation, printing, metadata reading, opening of encrypted pdf files (with password), annotations reading and insertion (Text, Highlight, Rectangle and Freetext), saving of the file attached or embedded, links, searching for text. And: the size of the program is saved when it change; standard keyboard navigation; visualization of the metadata, saving.
The document is instantly saved in case of deletion or insertion of annotations.

The paper colour can be changed in the config file: first set USE_ALPHA=1 then set the colour.

A couple of minor issues are still present, but it can also be used daily. 

Feature: Ctrl+LMB: selection to clipboard; the "Text" annotation is inserted by clicking in the main area as soon as the mouse pointer change; the "Rectangle" and the "Freetext" annotations are inserted by choosing two point in the main area of the document; the "Highlight" annotation is inserted by selecting the area with Ctrl+LMB; RMB to reset all choises about the annotations. The annotations support custom data. RMB to choose to delete each annotations, even those not inserted by the user, and save the attached files in form of annotation. If the file include embedded files a new button appears in the top: click it to know some info about them or to save them (a dialog appears). Go to page link: just click it. Go to web link: click it to copy to clipboard the link. The RMB should reset everything.

In the doc folder there are two sample files: the password for the file pdf-password.pdf is password.

Issue: this program was developped using Python version 3.7. With Python version 3.11, this program cannot be launched. To solve this issue go into the fitz directory and change the name of the following file 
from
_fitz.cpython-37m-x86_64-linux-gnu.so
to
_fitz.cpython-311-x86_64-linux-gnu.so

![My image](https://github.com/frank038/tkpdfreader/blob/master/img1.png)
