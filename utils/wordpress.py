import requests

WP_API_BASE = "https://public-api.wordpress.com/rest/v1.1/sites/{site_id}"

def upload_image(access_token, image_path, image_name):
    files = {"file": open(image_path, "rb")}
    headers = {"Authorization": f"Bearer {access_token}"}
    url = f"{WP_API_BASE.format(site_id='me')}/media/new"
    res = requests.post(url, headers=headers, files=files)
    res.raise_for_status()
    return res.json()["ID"]

def post_to_wordpress(access_token, title, content, media_id=None):
    url = f"{WP_API_BASE.format(site_id='me')}/posts/new"
    headers = {"Authorization": f"Bearer {access_token}"}
    data = {"title": title, "content": content, "status": "publish"}
    if media_id:
        data["media[]"] = media_id
    res = requests.post(url, headers=headers, data=data)
    res.raise_for_status()
    return res.json()["URL"]
