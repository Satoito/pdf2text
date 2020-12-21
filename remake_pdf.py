from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTFigure
import codecs

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
# from reportlab.lib.units import cm

from reportlab.platypus import BaseDocTemplate, PageTemplate
from reportlab.platypus import Paragraph, PageBreak, FrameBreak
from reportlab.platypus.flowables import Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, mm
# from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import cidfonts
from reportlab.platypus.frames import Frame

from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

import requests

# import pprint

def extract_elements(path):
    
    page_layouts = []
    
    for page_layout in extract_pages(path):
        
        page_width = page_layout.width
        page_height = page_layout.height
        
        texts = []
        images = []
        others = []

        for element in page_layout:
            
            if isinstance(element, LTTextContainer): #text
                typ = 0
                text = element.get_text().replace('\n','')
                fonts = []
                for text_line in element:
                    for character in text_line:
                        if isinstance(character, LTChar):
                            fonts.append(character.__dict__)

            elif isinstance(element, LTFigure): #image
                typ = 1
            else: #other
                typ = 2

            if typ == 0 or typ == 1:
                x0 = element.x0
                x1 = element.x1
                y0 = element.y0
                y1 = element.y1
                width =  element.width
                height =  element.height

            if typ == 0:
                temp_dict = {'x0':x0, 'x1':x1, 'y0':y0, 'y1':y1, 
                             'width':width, 'height':height, 
                             'text':text, 'fonts':fonts}
                texts.append(temp_dict)
            elif typ == 1:
                temp_dict = {'x0':x0, 'x1':x1, 'y0':y0, 'y1':y1, 
                             'width':width, 'height':height}
                images.append(temp_dict)
            else:
                temp_dict = {'element':element}
                others.append(temp_dict)

        layout_dict = {'texts':texts, 'images':images, 'others':others, 
                       'width':page_width, 'height':page_height}
        page_layouts.append(layout_dict)
    
    return page_layouts

def translate(input):
    api_url = "https://script.google.com/macros/s/AKfycbyBsXrekiDfsKh4gZAheHq2wk7_NvtIPWU_EptPZYJOEgAvCJeX/exec"
    headers = {"Authorization": "Bearer ya29.a0AfH6SMAe-iBgD2qzEuciSRTT-ARk8kEI56rK861Em0qrR-nXt1-SazhMkO-CzKG7LIsN3NJlg9mZmJzhq7gwf5Citr98PNZpOnq3O9nqYZXvf-KrLpS3roC0x4KQTk_Q00dByHAmmFr_A1s3eW9iN07YtNZ4xMYh2c2of7G3j7w"}
    
    params = {
            'text': "\"" + input + "\"",
            'source': 'en',
            'target': 'ja'
        }
    
    r_post = requests.post(api_url, headers=headers, data=params)
    return r_post.json()["text"]


def remake_pdf(page_layouts, output_path):
    page_width = page_layouts[0]['width']
    page_height = page_layouts[0]['height']
    
    GEN_SHIN_GOTHIC_MEDIUM_TTF = "./fonts/GenShinGothic-Monospace-Medium.ttf"
    pdfmetrics.registerFont(TTFont('GenShinGoshic', GEN_SHIN_GOTHIC_MEDIUM_TTF))
    #ppdfmetrics.registerFont(cidfonts.UnicodeCIDFont("HeiseiMin-W3"))
    
    doc = BaseDocTemplate(output_path, 
        title="test", 
        pagesize=(page_width, page_height),
        )

    show = 1 # 1:Frameの枠を表示, 0:表示しない
    frames = []
    for page_layout in page_layouts:
        for element in page_layout['texts']:
            x0 = element['x0']
            x1 = element['x1']
            y0 = element['y0']
            y1 = element['y1']
            width = element['width']
            height = element['height']
            frames.append( Frame(x0, y0, width, height, showBoundary=show) )

    page_template = PageTemplate("frames", frames=frames)
    doc.addPageTemplates(page_template)

    #style_dict ={
    #         "name":"normal",
    #         "fontName":"HeiseiMin-W3",
    #         "fontSize":15,
    #         "leading":10,
    #         }
    #style = ParagraphStyle(**style_dict)

    style = ParagraphStyle(name='normal', fontName='GenShinGoshic')

    flowables = []

    for page_layout in page_layouts:
        for element in page_layout['texts']:
            #text = element['text']
            text = translate(element['text'])
            text = text.replace("「","")
            text = text.replace("」","")
            print(text)
            para = Paragraph(text, style)
            flowables.append(para)
            flowables.append(FrameBreak())
    doc.multiBuild(flowables)


def main():
    input_path = input("Please input pdf path : ")
    output_path,ext = input_path.split(".")
    output_path += "_remake.pdf"

    page_layouts = extract_elements(input_path)
    #print(takeout_text(page_layouts))
    #print(translate(page_layouts[0]['texts'][1]['text']))
    remake_pdf(page_layouts, output_path)

if __name__ == '__main__':
    main()