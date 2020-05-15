from bs4 import BeautifulSoup
import pandas as pd
import re
from urllib.request import urlopen

url = "https://infinitediscs.com"
output_file = "discs.csv"


def flatten_li(arr):
    flat_arr = []
    for li in arr:
        if li.find("li") == None:
            flat_arr.append(li.find("a"))
        else:
            [flat_arr.append(sub_li.find("a")) for sub_li in li.findAll("li")]
    return flat_arr


def get_disc_refs(category):
    try:
        return [
            itm.findAll("button")[-1]["onclick"].split("=")[1].strip("'")
            for itm in category.findAll("div", {"class": "thumbnail"})
        ]
    except Exception:
        return []


disc_attrs = {
    "name": {
        "id": "ContentPlaceHolder1_lblDiscName",
        "type": "h1",
        "f": lambda x: x.text.strip()
    },
    "diameter": {
        "id": "ContentPlaceHolder1_lblDiameter",
        "type": "li",
        "f": lambda x: x.text.replace("Diameter:", "").strip()
    },
    "height": {
        "id": "ContentPlaceHolder1_lblHeight",
        "type": "li",
        "f": lambda x: x.text.replace("Height:", "").strip()
    },
    "rim_depth": {
        "id": "ContentPlaceHolder1_lblRimDepth",
        "type": "li",
        "f": lambda x: x.text.replace("Rim Depth:", "").strip()
    },
    "rim_width": {
        "id": "ContentPlaceHolder1_lblRimWidth",
        "type": "li",
        "f": lambda x: x.text.replace("Rim Width:", "").strip()
    },
    "speed": {
        "id": "ContentPlaceHolder1_lblSpeed",
        "type": "li",
        "f": lambda x: float(x.text.replace("Speed:", "").strip())
    },
    "glide": {
        "id": "ContentPlaceHolder1_lblGlide",
        "type": "li",
        "f": lambda x: float(x.text.replace("Glide:", "").strip())
    },
    "turn": {
        "id": "ContentPlaceHolder1_lblTurn",
        "type": "li",
        "f": lambda x: float(x.text.replace("Turn:", "").strip())
    },
    "fade": {
        "id": "ContentPlaceHolder1_lblFade",
        "type": "li",
        "f": lambda x: float(x.text.replace("Fade:", "").strip())
    },
    "stability": {
        "id": "ContentPlaceHolder1_lblStability",
        "type": "li",
        "f": lambda x: x.text.replace("Stability:", "").strip()
    },
    "bead": {
        "id": "ContentPlaceHolder1_lblBeadless",
        "type": "li",
        "f": lambda x: x.text.strip()
    }
}

html = urlopen(url).read()
soup = BeautifulSoup(html, features="html.parser")

menu = soup.find("div", {"id": "main-menu"})
menu_items = [li for li in flatten_li(menu.findAll("li")) if li != None]
mfgs = [itm for itm in menu_items if "/category/" in itm["href"]][:-1]

discs = []

mfg_counter = 0
for mfg in mfgs:
    mfg_counter += 1
    print("Researching manufacturer: {} - ({}/{})".format(
        mfg.text, str(mfg_counter), str(len(mfgs))
    ))
    html = urlopen(url + mfg["href"]).read()
    soup = BeautifulSoup(html, features="html.parser")

    disc_refs = []
    for id in ["DD", "CD", "MR", "PT"]:
        disc_refs += get_disc_refs(
            soup.find("div", {"id": "ContentPlaceHolder1_pnl" + id})
        )

    disc_counter = 0
    for disc_ref in disc_refs:
        disc_counter += 1
        html = urlopen(url + disc_ref).read()
        soup = BeautifulSoup(html, features="html.parser")

        disc = {
            "manufacturer": mfg.text,
            "link": url + disc_ref
        }
        for key in disc_attrs:
            attr = disc_attrs[key]
            try:
                disc[key] = attr["f"](
                    soup.find(attr["type"], {"id": attr["id"]}))
            except Exception:
                disc[key] = None

        discs.append(disc)
        print("\t({}/{}) {} - {}".format(
            str(disc_counter).zfill(len(str(len(disc_refs)))),
            str(len(disc_refs)),
            mfg.text,
            disc["name"]
        ))

# write disc info to csv file
df = pd.DataFrame.from_dict(discs)
df = df[[
    "manufacturer",
    "name",
    "speed",
    "glide",
    "turn",
    "fade",
    "diameter",
    "height",
    "rim_depth",
    "rim_width",
    "bead",
    "stability",
    "link"
]]

df.to_csv(output_file, index=False)

input("\nData load complete\n")
