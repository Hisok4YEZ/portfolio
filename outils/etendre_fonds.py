#!/usr/bin/env python3
"""Prolonge le fond des vignettes autour du logo, sans flou ni recadrage du logo.

Pour chaque image, crée « <nom>-etendu.jpg » à côté de l'original (l'original n'est jamais modifié) :
l'image d'origine est placée au centre d'une toile K fois plus grande, et tout autour on répète les
pixels de ses bords, adoucis en s'éloignant de l'image. Un fond uni reste uni, un dégradé se prolonge
dans le même sens.
La toile garde le format de l'original : le site l'affiche en « contain » dans une boîte K fois plus
grande que la vignette (variable CSS --k), donc le logo garde exactement sa taille et sa place.

    python3 outils/etendre_fonds.py        (depuis le dossier test1)
"""
from pathlib import Path
from PIL import Image, ImageChops, ImageFilter

RACINE = Path(__file__).resolve().parent.parent / "Vignettes 2"

# K : taille de la toile par rapport à l'image. Il faut K ≥ (format le plus large de la vignette) / (format de
# l'image), et inversement. 2,4 couvre les cartes, la mini-carte et la fiche ; 1,2 suffit pour les affiches 2:3.
K_CARTES, K_AFFICHES = 2.4, 1.2

# chemin, K, rognage (gauche, haut, droite, bas) des lignes parasites sur les bords, mode
#   mode 'bords' : répète les pixels des bords ; 'uni' : couleur de fond la plus fréquente sur les bords
#   (pour Oppizi, dont le motif blanc et la ligne rose touchent les bords et feraient des traînées)
IMAGES = [
    ("Principales - Pour Vous/marathon logo.jpeg", K_CARTES, (1, 1, 2, 1), "bords"),
    ("Principales - Pour Vous/Banijay group.png", K_CARTES, (1, 1, 1, 1), "bords"),
    ("Principales - Pour Vous/TF1.jpeg", K_CARTES, (1, 2, 1, 4), "bords"),
    ("Horizontales - Des pépites pour vous/Alptis.png", K_CARTES, (1, 1, 1, 1), "bords"),
    ("Horizontales - Des pépites pour vous/Equancy.png", K_CARTES, (1, 1, 1, 1), "bords"),
    ("Horizontales - Des pépites pour vous/Oppizi.png", K_CARTES, (1, 1, 1, 1), "uni"),
    ("Verticlaes - Jobs étudiants/Action.png", K_AFFICHES, (1, 1, 1, 1), "bords"),
    ("Verticlaes - Jobs étudiants/Confluence.png", K_AFFICHES, (1, 1, 1, 1), "bords"),
    ("Verticlaes - Jobs étudiants/Haagen-Dazs.jpg", K_AFFICHES, (1, 1, 1, 1), "bords"),
    ("Verticlaes - Jobs étudiants/Primark.png", K_AFFICHES, (1, 1, 1, 1), "bords"),
    ("Verticlaes - Jobs étudiants/eurofins.png", K_AFFICHES, (1, 1, 1, 1), "bords"),
    ("Verticlaes - Jobs étudiants/zara.png", K_AFFICHES, (1, 1, 1, 1), "bords"),
]


def couleur_des_bords(im):
    w, h = im.size
    px = [im.getpixel((x, y)) for x in range(w) for y in (0, h - 1)]
    px += [im.getpixel((x, y)) for y in range(h) for x in (0, w - 1)]
    return max(set(px), key=px.count)


def etendre(im, k, mode):
    w, h = im.size
    px, py = round(w * (k - 1) / 2), round(h * (k - 1) / 2)
    W, H = w + 2 * px, h + 2 * py
    if mode == "uni":
        out = Image.new("RGB", (W, H), couleur_des_bords(im))
        out.paste(im, (px, py))
        return out
    rep = Image.NEAREST  # étirer une ligne d'un pixel = la répéter, sans mélange

    def repeter(lisse):
        # répète les bords de l'image ; lisse > 0 : chaque bord est d'abord adouci sur sa longueur
        # (le grain et la compression du bord feraient sinon des traînées en étant répétés)
        bord = lambda b: b.filter(ImageFilter.GaussianBlur(lisse)) if lisse else b
        c = Image.new("RGB", (W, H))
        c.paste(im, (px, py))
        c.paste(bord(im.crop((0, 0, 1, h))).resize((px, h), rep), (0, py))
        c.paste(bord(im.crop((w - 1, 0, w, h))).resize((px, h), rep), (px + w, py))
        c.paste(bord(c.crop((0, py, W, py + 1))).resize((W, py), rep), (0, 0))
        c.paste(bord(c.crop((0, py + h - 1, W, py + h))).resize((W, py), rep), (0, py + h))
        return c

    def masque(debut, fin):
        # 0 à moins de `debut` pixels de l'image, 255 au-delà de `fin`, en fondu entre les deux
        rampe = lambda n, p, m: [min(255, max(0, round((max(p - i, i - (p + m - 1), 0) - debut) / (fin - debut) * 255))) for i in range(n)]
        mx = Image.new("L", (W, 1)); mx.putdata(rampe(W, px, w))
        my = Image.new("L", (1, H)); my.putdata(rampe(H, py, h))
        return ImageChops.lighter(mx.resize((W, H), rep), my.resize((W, H), rep))

    # collé à l'image : le pixel exact du bord (aucune cassure), puis en quelques pixels le bord adouci
    lisse = max(3, max(w, h) / 120)
    out = Image.composite(repeter(lisse), repeter(0), masque(0, 1.5 * lisse))
    # La répétition laisse aussi des angles nets dans les coins : on adoucit le prolongement de plus en plus
    # en s'éloignant de l'image. Le lissage de rayon s ne s'applique qu'à plus de 3,5 s de l'image : il ne
    # puise jamais dans l'image, donc jamais dans le logo.
    base, s = out, 2.0
    while 3.5 * s < max(px, py):
        out = Image.composite(base.filter(ImageFilter.GaussianBlur(s)), out, masque(3.5 * s, 7 * s))
        s *= 1.6
    out.paste(im, (px, py))
    return out


for chemin, k, (g, t, d, b), mode in IMAGES:
    src = RACINE / chemin
    im = Image.open(src).convert("RGB")
    im = im.crop((g, t, im.width - d, im.height - b))
    dst = src.with_name(src.stem + "-etendu.jpg")
    etendre(im, k, mode).save(dst, quality=90, subsampling=0, optimize=True, progressive=True)
    print(f"{dst.relative_to(RACINE)}  {dst.stat().st_size // 1024} Ko")
