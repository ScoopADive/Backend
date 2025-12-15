# utils/wordpress.py
import requests
import json

WP_API_BASE = "https://public-api.wordpress.com/rest/v1.1/sites/{site_id}"


def upload_image(access_token, image_path, image_name):
    """
    WordPress 미디어 라이브러리에 이미지 업로드
    """
    url = f"{WP_API_BASE.format(site_id='me')}/media/new"
    headers = {"Authorization": f"Bearer {access_token}"}

    with open(image_path, "rb") as img_file:
        files = {"file": (image_name, img_file)}
        res = requests.post(url, headers=headers, files=files)

    res.raise_for_status()
    return res.json()["ID"]


def post_to_wordpress(access_token, title, content, media_id=None):
    """
    WordPress 글 작성 (UTF-8 안전)
    """
    url = f"{WP_API_BASE.format(site_id='me')}/posts/new"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json; charset=utf-8",
    }
    data = {
        "title": title,
        "content": content,
        "status": "publish",
    }
    if media_id:
        data["media[]"] = media_id

    # JSON 문자열 UTF-8로 안전하게 변환
    res = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))
    res.raise_for_status()
    return res.json()["URL"]
