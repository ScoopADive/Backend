import requests
import json
import unicodedata

WP_API_BASE = "https://public-api.wordpress.com/rest/v1.1/sites/{site_id}"


def sanitize_filename(filename: str) -> str:
    """
    이미지 파일 이름을 ASCII-safe로 변환
    """
    safe_name = unicodedata.normalize('NFKD', filename).encode('ascii', 'ignore').decode('ascii')
    if not safe_name:
        safe_name = "image.jpg"
    return safe_name


def upload_image(access_token, image_path, image_name):
    """
    WordPress 미디어 라이브러리에 이미지 업로드 (UTF-8/ASCII 안전)
    """
    safe_name = sanitize_filename(image_name)
    url = f"{WP_API_BASE.format(site_id='me')}/media/new"
    files = {"file": (safe_name, open(image_path, "rb"))}
    headers = {"Authorization": f"Bearer {access_token}"}

    res = requests.post(url, headers=headers, files=files)
    res.raise_for_status()
    return res.json()["ID"]


def post_to_wordpress(access_token, title, content, media_id=None):
    """
    WordPress 글 작성 (UTF-8 안전, JSON 전송)
    """
    url = f"{WP_API_BASE.format(site_id='me')}/posts/new"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {
        "title": title,
        "content": content,
        "status": "publish",
    }
    if media_id:
        data["media[]"] = media_id

    res = requests.post(url, headers=headers, json=data)
    res.raise_for_status()
    return res.json()["URL"]
