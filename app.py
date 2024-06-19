from flask import Flask, render_template, request, redirect
from datetime import date, datetime
import random
import json
import os

app = Flask(__name__)

markers = ["t>", "s>", "i>", "l>", "p>"]


def getname_fixlen(n: str, ln: int):
    if len(n) <= ln:
        return n
    n = n.split()
    s, ps = '', ''
    for i in n:
        ps += i
        if len(ps) <= ln:
            s += i
        else:
            return s


@app.route('/')
def main():
    nl, nt, ns, pt, ph = os.listdir("static/news"), [], [], [], []
    for i in range(len(nl)):
        with open(f"static/news/{nl[i]}/news.txt", "r", encoding="utf-8") as fl:
            st = "t>"
            while st[:2] in markers:
                st = fl.readline()
            nt.append(st[:175]+("..." if len(st) > 175 else ""))
        with open(f"static/news/{nl[i]}/info.json", "r") as fl:
            lst = json.load(fl)
            ns.append({"index": i, "date": lst["date"]})
    ns = sorted(ns, key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)
    ns = [i["index"] for i in ns[:6]]
    np = [getname_fixlen(i, 48) for i in nl]
    if len(nl) < 6:
        for i in range(len(nl), 6):
            nl.append("none"), ns.append(i), np.append(""), nt.append("")
    pl = os.listdir('static/photos')
    for i in range(3):
        rand = random.randint(0, len(pl)-1)
        pt.append(pl[rand])
        pl.pop(rand)
    for i in pt:
        with open(f"static/photos/{i}/info.json", "r", encoding="utf-8") as fl:
            lst = json.load(fl)
            ph.append({"index": i, "ntype": lst["ntype"], "image": lst['image'], "text": lst['text']})
    bigphotos = [["Следите за ходом космических миссий", "в новостном разделе", "mars_rover.png",
                  "/news?title=&ntype=space_missions"],
                 ["Впечатляющие фотографии планет", "в разделе фотографии солнечной системы", "jupiter.png",
                  "/photos?title=&ntype=solar"],
                 ["Красоты далёких миров", "фотографии дальнего космоса", "andromeda.jpg",
                  "/photos?title=&ntype=farspace"]]
    indexes = [i for i in range(len(bigphotos))]
    rand = random.randint(0, len(indexes) - 1)
    bp = [indexes[rand]]
    indexes.pop(rand)
    bp.append(indexes[random.randint(0, len(indexes) - 1)])
    bp = [bigphotos[bp[i]] for i in range(len(bp))]
    return render_template('main.html', nl=nl, np=np, nt=nt, ns=ns, ph=ph, bp=bp)


@app.route('/news')
def news():
    nl, nt, ns = os.listdir("static/news"), [], []
    for i in range(len(nl)):
        with open(f"static/news/{nl[i]}/news.txt", "r", encoding="utf-8") as fl:
            st = "t>"
            while st[:2] in markers:
                st = fl.readline()
            nt.append(st)
        with open(f"static/news/{nl[i]}/info.json", "r", encoding="utf-8") as fl:
            lst = json.load(fl)
            ns.append({"index": i, "date": lst["date"], "ntype": lst["ntype"],  "image": f"news/{nl[i]}/{lst['mimg']}",
                       "kwords": {i for i in lst["kwords"].split()}})
    ns = sorted(ns, key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)
    try:
        title = request.args['title']
        data = request.args['ntype']
        checks = ["checked" if data == "all" else "", "checked" if data == "earth" else "",
                  "checked" if data == "nearspace" else "", "checked" if data == "space_missions" else "",
                  "checked" if data == "farspace" else ""]
        if data != "all":
            ns = [i for i in ns if i["ntype"] == data]
        ctg = "все категории" if data == "all" else "земные" if data == "earth" else "ближний космос" if (
                data == "nearspace") else "космические миссии" if data == "space_missions" else "дальний космос"
        if title == '':
            return render_template('news.html', nl=nl, nt=nt, ns=ns, checks=checks, ctg=ctg,
                                   poisk="Последние новости" if ns != [] else "По запросу ничего не найдено")
        else:
            nn = [i for i in ns if title == nl[i['index']]]
            add = sorted([[{u for u in title.split()} & ns[i]["kwords"], i] for i in range(len(ns))],
                         key=lambda x: len(x[0]), reverse=True)
            add = [i for i in add if i[0] != set()]
            nn += [ns[i[1]] for i in add if ns[i[1]] not in nn]
            add = sorted([[{u for u in title.split()} & set(nl[ns[i]['index']].split()), i] for i in range(len(ns))],
                         key=lambda x: len(x[0]), reverse=True)
            add = [i for i in add if i[0] != set()]
            nn += [ns[i[1]] for i in add if ns[i[1]] not in nn]
            return render_template('news.html', nl=nl, nt=nt, ns=nn, checks=checks, ctg=ctg,
                                   poisk="Последние новости" if nn != [] else "По запросу ничего не найдено")
    except:
        return render_template('news.html', nl=nl, nt=nt, ns=ns, ctg="все категории",
                               checks=["checked", "", "", "", ""], poisk="Последние новости")


@app.route('/news/<title>')
def article(title):
    if title in os.listdir("static/news"):
        with open(f"static/news/{title}/news.txt", "r", encoding="utf-8") as fl:
            info = fl.read().split(sep="\n")
        return render_template('article.html', notfound=False, info=info, nl=title)
    else:
        return render_template('article.html', notfound=True)


@app.route('/feedback', methods=["GET", "POST"])
def feedback():
    if request.method == 'POST':
        count = len(os.listdir("reports")) + 1
        with open(f"reports/report{count}.json", "w", encoding="utf-8") as fl:
            txt = {"причина": request.form['option'], "текст": request.form['text'], "проверено": False}
            fl.write(json.dumps(txt, ensure_ascii=False))
    return render_template('feedback.html')


@app.route('/photos')
def photos():
    nl, ns = os.listdir("static/photos"), []
    for i in range(len(nl)):
        with open(f"static/photos/{nl[i]}/info.json", "r", encoding="utf-8") as fl:
            lst = json.load(fl)
            ns.append({"index": i, "date": lst["date"], "ntype": lst["ntype"], "text": lst['text'],
                       "image": lst['image'], "kwords": {i for i in lst["kwords"].split()}})
    ns = sorted(ns, key=lambda x: datetime.strptime(x['date'], '%d.%m.%Y'), reverse=True)
    try:
        title = request.args['title']
        data = request.args['ntype']
        checks = ["checked" if data == "all" else "", "checked" if data == "space" else "",
                  "checked" if data == "solar" else "", "checked" if data == "farspace" else ""]
        if data != "all":
            ns = [i for i in ns if i["ntype"] == data]
        ctg = "все категории" if data == "all" else "космическое пространство" if (
                data == "space") else "солнечная система" if data == "solar" else "дальний космос"
        if title == '':
            return render_template('photos.html', nl=nl, ns=ns, checks=checks, ctg=ctg,
                                   poisk="Последние фото" if ns != [] else "По запросу ничего не найдено")
        else:
            nn = [i for i in ns if title == nl[i['index']]]
            add = sorted([[{u for u in title.split()} & ns[i]["kwords"], i] for i in range(len(ns))],
                         key=lambda x: len(x[0]), reverse=True)
            add = [i for i in add if i[0] != set()]
            nn += [ns[i[1]] for i in add if ns[i[1]] not in nn]
            add = sorted([[{u for u in title.split()} & set(nl[ns[i]['index']].split()), i] for i in range(len(ns))],
                         key=lambda x: len(x[0]), reverse=True)
            add = [i for i in add if i[0] != set()]
            nn += [ns[i[1]] for i in add if ns[i[1]] not in nn]
            return render_template('photos.html', nl=nl, ns=nn, checks=checks, ctg=ctg,
                                   poisk="Последние фото" if ns != [] else "По запросу ничего не найдено")
    except:
        return render_template('photos.html', nl=nl, ns=ns, ctg="все категории",
                               checks=["checked", "", "", ""], poisk="Последние фото")


@app.route('/photos/<title>')
def photo(title):
    if title in os.listdir("static/photos"):
        with open(f"static/photos/{title}/info.json", "r", encoding="utf-8") as fl:
            info = json.load(fl)
        return render_template('photo.html', notfound=False, nl=title, text=info["text"],
                               image=info["image"], date=info["date"])
    else:
        return render_template('photo.html', notfound=True)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
