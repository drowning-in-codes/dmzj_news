import requests

llm_api = "http://proanimer.com:9321"

# res = requests.get(llm_api + "/supports")
# print(res)
# print(res.text)
# print(res.json())
# if res.status_code == 200:
#     print(res.json())
#     res = res.json()
#     print(res[0])
#     site = res[0].get("site")
#     print(site)
#
# data = {
#     "prompt": "give me some fantastic anime",
#     "model": "gpt-3.5-turbo",
#     "site": "better",
# }
# res = requests.get(
#     llm_api + "/ask/stream",
#     params=data,
#     headers={
#         "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
#         "Chrome/117.0.0.0 Safari/537.36 Edg/117.0.2045.36"
#     },
#     stream=True,
# )
#
# for i in res.iter_content(chunk_size=1024):
#     print(i)
