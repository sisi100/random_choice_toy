import json
import os
import random

import boto3
import requests

S3_CLIENT = boto3.client("s3")
BUCKET_NAME = os.getenv("BUCKET")
SLACK_URL = os.getenv("SLACK_URL")

GENERATE_PRESIGNED_URL_EXPIRES_IN = 12 * 60 * 60  # 12時間

items = [
    ["手作りのうさぎ", "img1.jpg"],
    ["手作りのほし", "img2.jpg"],
    ["手作りのぞう", "img3.jpg"],
]


def get_item():
    name, key = random.choice(items)
    presigned_url = S3_CLIENT.generate_presigned_url(
        ClientMethod="get_object",
        ExpiresIn=GENERATE_PRESIGNED_URL_EXPIRES_IN,
        Params={"Bucket": BUCKET_NAME, "Key": key},
        HttpMethod="GET",
    )
    return name, presigned_url


def random_choice(event, context):
    name, img_url = get_item()

    payload = {"text": f"今日の玩具は【{name}】です。<{img_url}|🌟>"}  # 直接URLを表示するとスマホでみたときに長過ぎたのでリンクを貼ってごまかす
    headers = {"content-type": "application/json"}

    r = requests.post(SLACK_URL, data=json.dumps(payload), headers=headers)
    return {"text": r.text}
