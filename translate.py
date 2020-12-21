import argparse
import requests
import pprint

def main():

    api_url = "https://script.google.com/macros/s/AKfycbyBsXrekiDfsKh4gZAheHq2wk7_NvtIPWU_EptPZYJOEgAvCJeX/exec"
    headers = {"Authorization": "Bearer ya29.a0AfH6SMAe-iBgD2qzEuciSRTT-ARk8kEI56rK861Em0qrR-nXt1-SazhMkO-CzKG7LIsN3NJlg9mZmJzhq7gwf5Citr98PNZpOnq3O9nqYZXvf-KrLpS3roC0x4KQTk_Q00dByHAmmFr_A1s3eW9iN07YtNZ4xMYh2c2of7G3j7w"}

    parser = argparse.ArgumentParser()
    parser.add_argument("-input", type=str, required=True)
    args = parser.parse_args()

    input = ""
    with open(args.input, 'r',encoding="utf-8") as f:
        for line in f:
            print(line)
            line = line.strip()
            input += line

    params = {
        'text': "\"" + input + "\"",
        'source': 'en',
        'target': 'ja'
    }

    r_post = requests.post(api_url, headers=headers, data=params)
    print(r_post.text)


if __name__ == "__main__":
    main()