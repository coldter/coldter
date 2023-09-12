import requests
import pathlib
import re
import os

root = pathlib.Path(__file__).parent.resolve()


def update_programmer_humor_img(name):
    try:
        items = requests.get(
            "https://api.imgur.com/3/gallery/t/{tagName}/{sort}".format(
                tagName=name, sort="viral"
            ),
            headers={"Authorization": f"Client-ID {os.getenv('CLIENT_ID')}"},
        ).json()["data"]["items"]

        for item in items:
            if item["images"][0]["link"].endswith(".mp4") or item["images"][0][
                "link"
            ].endswith(".gif"):
                continue
            else:
                return '<a href="https://imgur.com/t/ProgrammerHumor/{}"><img max-height="400" width="350" src="{}"></a>'.format(
                    item["id"], item["images"][0]["link"]
                )

        return '<a href="https://imgur.com/r/ProgrammerHumor/{}"><img max-height="400" width="350" src="https://i.imgur.com/{}"></a>'.format(
            "SV767tT", "SV767tT.jpeg"
        )
    except Exception as e:
        print(e)


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

    txt_pro = txt_yearProgress.open(encoding="utf-8").read()

    return txt_pro


if __name__ == "__main__":
    readme = root / "README.md"

    readme_contents = readme.open(encoding="utf-8").read()
    rewritten = readme_contents
    rewritten = replace_chunk(
        rewritten,
        "programmer_humor_img",
        update_programmer_humor_img("programmerhumor"),
    )

    rewritten = replace_chunk(rewritten, "yearProgress", yearProgress())

    readme.open("w", encoding="utf-8").write(rewritten)
