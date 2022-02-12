from imgurpython.helpers.error import ImgurClientError
from imgurpython import ImgurClient
import requests
import pathlib
import random
import json
import sys
import re
import os

root = pathlib.Path(__file__).parent.resolve()

def update_programmer_humor_img(name):
  try:
    client = ImgurClient(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])
    items = client.subreddit_gallery(name, sort='top', window='week', page=0)
    for item in items:
      if item.link.endswith(".mp4") or item.link.endswith(".gif"):
        continue
      else:
        return '<a href="https://imgur.com/r/ProgrammerHumor/{}"><img max-height="400" width="350" src="{}"></a>'.format(item.id, item.link)
    return '<a href="https://imgur.com/r/ProgrammerHumor/{}"><img max-height="400" width="350" src="https://i.imgur.com/{}"></a>'.format("SV767tT", "SV767tT")
  except ImgurClientError as e:
    print(e.error_message)

def replace_chunk(content, marker, chunk, inline=False):
  # build the regular expression pattern, DOTALL will match any character, including a newline
  r = re.compile(
    r"<!-- {} starts -->.*<!-- {} ends -->".format(marker, marker),
    re.DOTALL,
  )
  # add newline before and after
  if not inline:
    chunk = "\n{}\n".format(chunk)
  # build the final chunk by adding comments before and after the chunk
  chunk = "<!-- {} starts -->{}<!-- {} ends -->".format(marker, chunk, marker)
  # replace matched string using pattern provided with the chunk
  return r.sub(chunk, content)


def yearProgress():
  txt_yearProgress = root / "yearProgress.txt"
  
  txt_pro = txt_yearProgress.open(encoding='utf-8').read()
  
  return txt_pro

if __name__ == "__main__":
  readme = root / "README.md"

  readme_contents = readme.open(encoding='utf-8').read()
  rewritten = readme_contents
  rewritten = replace_chunk(rewritten, "programmer_humor_img", update_programmer_humor_img("ProgrammerHumor"))

  rewritten = replace_chunk(rewritten, "yearProgress", yearProgress())
  

  readme.open("w", encoding='utf-8').write(rewritten)