from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import time
import argparse
import requests
import pprint


input_path = input("Please input pdf path : ")
output_path,ext = input_path.split(".")
output_path += ".txt"
output_convert_path,ext = input_path.split(".")
output_convert_path += "_convert.txt"
output_translate_path,ext = input_path.split(".")
output_translate_path += "_translate.txt"

manager = PDFResourceManager()


def is_float(n):
    try:
        float(n)
    except ValueError:
        return False
    else:
        return True

def get_text():
    with open(output_path, "wb") as output:
        with open(input_path, 'rb') as input:
            with TextConverter(manager, output, codec='utf-8', laparams=LAParams()) as conv:
                interpreter = PDFPageInterpreter(manager, conv)
                for page in PDFPage.get_pages(input):
                    interpreter.process_page(page)

def convert_text():
    emp = " "
    with open(output_path, "r", encoding="utf-8") as output:
        with open(output_convert_path, "w", encoding="utf-8") as convert:
            # 除去するutf8文字
            replace_strs = [b'\x00']

            #is_blank_line = False

            for line in output:
                # byte文字列に変換
                line_utf8 = line.encode('utf-8')

                # 余分な文字を除去する
                for replace_str in replace_strs:
                    line_utf8 = line_utf8.replace(replace_str, b'')

                # strに戻す
                line = line_utf8.decode()

                if is_float(line):
                    continue
                
                output = line.replace("\n", "")
                output = output.replace("fig.", "fig").replace("Fig.", "Fig")
                output = output.replace(".", ".\n\n")
                output = output.replace("෍", "")
               
                for i in range(1, 7):
                    output = output.replace(emp * i, " ")
                convert.write(output)


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


def main():
    input = ""

    get_text()
    convert_text()

    with open(output_translate_path, 'w', encoding="utf-8") as f_translate:
        with open(output_convert_path, 'r',encoding="utf-8") as f:
            for line in f:
                #print(line)
                line = line.strip()
                input += line

        f_translate.write(translate(input))


if __name__ == "__main__":
    main()