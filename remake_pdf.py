from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTChar, LTFigure
from pdfminer.layout import LAParams
import codecs

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
# from reportlab.lib.units import cm

from reportlab.platypus import BaseDocTemplate, PageTemplate, NextPageTemplate
from reportlab.platypus import Paragraph, PageBreak, FrameBreak
from reportlab.platypus.flowables import Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4, mm
# from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase import cidfonts
from reportlab.platypus.frames import Frame

from reportlab.pdfbase.pdfmetrics import registerFont
from reportlab.pdfbase.ttfonts import TTFont

import pprint
import requests


def extract_elements(path):
    laparams = LAParams()
    #上手く動かなかったpdfがあったため変更、要検証
    laparams.char_margin = 3.0
    
    page_layouts = []
    
    for page_layout in extract_pages(path, laparams=laparams):
        
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
                            letter = character.get_text()
                            font = character.fontname
                            fonts.append((letter, font))

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

def show_id(page_layouts, output_path):
    pdfFile = canvas.Canvas(output_path)
    pdfFile.saveState()

    for page_layout in page_layouts:
        page_width = page_layout['width']
        page_height = page_layout['height']
        pdfFile.setPageSize((page_width, page_height))
        i = 0
        for element in page_layout['texts']:
            x0 = element['x0']
            x1 = element['x1']
            y0 = element['y0']
            y1 = element['y1']
            width = element['width']
            height = element['height']
            pdfFile.rect(x0, y0, width, height, stroke=1, fill=0)
            pdfFile.drawString(x0, y0, str(i))
            i += 1

        pdfFile.showPage()

    # pdfFile.restoreState()
    pdfFile.save()

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

    # pdfmetrics.registerFont(cidfonts.UnicodeCIDFont("HeiseiMin-W3"))
    GEN_SHIN_GOTHIC_MEDIUM_TTF = "./fonts/GenShinGothic-Monospace-Medium.ttf"
    pdfmetrics.registerFont(TTFont('GenShinGoshic', GEN_SHIN_GOTHIC_MEDIUM_TTF))

    show = 1 # 1:Frameの枠を表示, 0:表示しない

    
    doc = canvas.Canvas(output_path,  
        pagesize=(page_width, page_height),
        )

    page_num = 0
    for page_layout in page_layouts:
        frame_id = 0
        frames = []
        for element in page_layout['texts']:
            x0 = element['x0']
            x1 = element['x1']
            y0 = element['y0']
            y1 = element['y1']
            width = element['width']
            height = element['height']

            text = element['text']

            replace_strs = [b'\x00']

            # byte文字列に変換
            line_utf8 = text.encode('utf-8')
            #print(text.encode(encoding="utf-8", errors="strict"))
            #print(line_utf8)
            #print(line_utf8.isascii())

            # ASCIIで以外が含まれているものを除外
            if line_utf8.isascii() == False:
                continue

            # 余分な文字を除去する
            for replace_str in replace_strs:
                line_utf8 = line_utf8.replace(replace_str, b'')

            # strに戻す
            text = line_utf8.decode()

            text = translate(text)
            text = text.removeprefix("「")
            text = text.removesuffix("」")
            
            frame = Frame(x0, y0, width, height, 
                        showBoundary=show, 
                        leftPadding=0, 
                        bottomPadding=0, 
                        rightPadding=0, 
                        topPadding=0, 
                        id=str(frame_id) )

            # フォントの大きさなど調整
            style_dict ={
                    "name":"normal",
                    "fontName":"GenShinGoshic",
                    "fontSize":15,
                    "leading":10
                    }
            style = ParagraphStyle(**style_dict)
            
            # style_dict ={
            #         "name":"normal",
            #         "fontName":"HeiseiMin-W3",
            #         "fontSize":15,
            #         "leading":10,
            #         }
            # style = ParagraphStyle(**style_dict)

            # para = Paragraph(text)
            para = Paragraph(text, style)
            
            # 文字が領域内に入るかの判定
            # とりあえず、収まりきらなかったらページ番号とidを出力
            w, h = para.wrap(width, height) # find required space
            if w <= width and h <= height:
                frame.addFromList([para], doc)
            else:
                doc.rect(x0, y0, width, height, stroke=1, fill=0)
                print("Not enough space at p.", page_num, ", id:", frame_id)
            
            frame_id += 1

        doc.showPage()
        page_num += 1

    doc.save()

def main():
    input_path = input("Please input pdf path : ")
    output_id,ext = input_path.split(".")
    output_id += "_id.pdf"
    output_path,ext = input_path.split(".")
    output_path += "_remake.pdf"

    #input_path = 'test.pdf' # 入力ファイル
    #output_id = 'test_id.pdf' # テキストボックスとid確認用ファイル
    #output_path = 'test_remake.pdf' # 出力ファイル
    
    page_layouts = extract_elements(input_path)
    show_id(page_layouts, output_id)
    # pprint.pprint(page_layouts)
    remake_pdf(page_layouts, output_path)

if __name__ == '__main__':
    main()
