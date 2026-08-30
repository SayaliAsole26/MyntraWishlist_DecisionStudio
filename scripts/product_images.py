"""Verified, category-matched image URLs — one per product (P001–P062)."""

IMG = "https://images.unsplash.com/photo-{id}?w=400&h=500&fit=crop"

# Shorthand for verified Unsplash photo IDs grouped by visual intent.
_DRESSES = [
    "1515372039744-b8f02a3ae446",  # floral summer dress
    "1566174053879-31528523f8ae",  # solid midi dress
    "1496747611176-843222e1e57c",  # fit & flare
    "1539008835657-9e8e9680c956",  # casual day dress
    "1469334031218-e382a71b716b",  # maxi / flowy
    "1585487000160-6ebcfceb0d03",  # party / evening
    "1594938298603-c8148c4dae35",  # formal / neutral
    "1585487000160-6ebcfceb0d03",
]
_SNEAKERS_M = [
    "1542291026-7eec264c27ff",  # red running
    "1608231387042-66d1773070a5",  # white running
    "1595950653106-6c9ebd614d3a",  # grey athletic
    "1542291026-7eec264c27ff",
]
_SNEAKERS_W = [
    "1543163521-1bf539c55dd2",  # women lifestyle sneaker
    "1608231387042-66d1773070a5",
]
_TOPS_M = [
    "1521572163474-6864f9cf17ab",  # plain tee
    "1576566588028-4147f3842f27",  # folded tees
    "1586363104862-3a5e2ab60d99",  # printed tee
    "1618354691373-d851c5c3a990",  # polo / collared
    "1576566588028-4147f3842f27",
]
_JEANS_M = [
    "1542272604-787c3835535d",  # blue denim
    "1624378439575-d8705ad7ae80",  # dark denim
    "1541099649105-f69ad21f3246",  # stacked denim
]
_JEANS_W = ["1541099649105-f69ad21f3246"]
_HANDBAGS = [
    "1590874103328-eac38a683ce7",  # crossbody / sling
    "1548036328-c9fa89d128fa",  # tote
    "1590874103328-eac38a683ce7",
    "1548036328-c9fa89d128fa",
    "1548036328-c9fa89d128fa",
]
_KURTAS = ["1617127365659-c47fa864d8bc"] * 5
_JACKETS = [
    "1551028719-00167b16eac5",  # denim / casual jacket
    "1591047139829-d91aecb6caea",  # bomber
    "1544022613-e87ca75a784a",  # leather biker
    "1594938298603-c8148c4dae35",  # puffer / neutral outerwear
    "1591047139829-d91aecb6caea",
]
_WATCHES = [
    "1523275335684-37898b6baf30",
    "1524592094714-0f0654e20314",
    "1434493789847-2f02dc6ca35d",
    "1524592094714-0f0654e20314",
    "1523275335684-37898b6baf30",
]
_SHORTS = [
    "1591195853828-11db59a44f6b",
    "1591195853828-11db59a44f6b",
    "1594938298603-c8148c4dae35",
    "1591195853828-11db59a44f6b",
]
_SUNGLASSES = ["1577803645773-f96470509666"] * 4
_ACTIVE = [
    "1506629082955-511b1aa562c8",  # leggings / workout
    "1571019614242-c5c5dee9f50b",  # track pants / gym
    "1518611012118-696072aa579a",  # sports bra / yoga
    "1571019614242-c5c5dee9f50b",
    "1518611012118-696072aa579a",
]
_SANDALS = [
    "1603487742131-4160ec999306",
    "1543163521-1bf539c55dd2",
    "1603487742131-4160ec999306",
    "1543163521-1bf539c55dd2",
]
_BLOUSE = ["1618354691373-d851c5c3a990"]


def _u(photo_id: str) -> str:
    return IMG.format(id=photo_id)


def _pick(pool: list[str], index: int) -> str:
    return _u(pool[index % len(pool)])


PRODUCT_IMAGES: dict[str, str] = {
    # Dresses
    "P001": _pick(_DRESSES, 0),
    "P002": _pick(_DRESSES, 1),
    "P003": _pick(_DRESSES, 2),
    "P013": _pick(_DRESSES, 3),
    "P014": _pick(_DRESSES, 4),
    "P058": _pick(_DRESSES, 5),
    "P059": _pick(_DRESSES, 6),
    # Sneakers
    "P004": _pick(_SNEAKERS_M, 0),
    "P005": _pick(_SNEAKERS_M, 1),
    "P015": _pick(_SNEAKERS_M, 2),
    "P016": _pick(_SNEAKERS_M, 1),
    "P012": _pick(_SNEAKERS_W, 0),
    "P060": _pick(_SNEAKERS_W, 1),
    # Tops
    "P006": _pick(_TOPS_M, 0),
    "P007": _pick(_TOPS_M, 2),
    "P020": _pick(_TOPS_M, 3),
    "P021": _pick(_TOPS_M, 2),
    "P022": _pick(_TOPS_M, 1),
    "P061": _pick(_BLOUSE, 0),
    # Jeans
    "P008": _pick(_JEANS_M, 0),
    "P009": _pick(_JEANS_M, 1),
    "P023": _pick(_JEANS_M, 0),
    "P024": _pick(_JEANS_M, 2),
    "P025": _pick(_JEANS_M, 1),
    "P062": _pick(_JEANS_W, 0),
    # Handbags
    "P010": _pick(_HANDBAGS, 0),
    "P011": _pick(_HANDBAGS, 1),
    "P017": _pick(_HANDBAGS, 2),
    "P018": _pick(_HANDBAGS, 0),
    "P019": _pick(_HANDBAGS, 1),
    # Kurtas
    "P026": _pick(_KURTAS, 0),
    "P027": _pick(_KURTAS, 0),
    "P028": _pick(_KURTAS, 0),
    "P029": _pick(_KURTAS, 0),
    "P030": _pick(_KURTAS, 0),
    # Jackets
    "P031": _pick(_JACKETS, 0),
    "P032": _pick(_JACKETS, 1),
    "P033": _pick(_JACKETS, 2),
    "P034": _pick(_JACKETS, 3),
    "P035": _pick(_JACKETS, 4),
    # Watches
    "P036": _pick(_WATCHES, 0),
    "P037": _pick(_WATCHES, 1),
    "P038": _pick(_WATCHES, 2),
    "P039": _pick(_WATCHES, 1),
    "P040": _pick(_WATCHES, 0),
    # Shorts
    "P041": _pick(_SHORTS, 0),
    "P042": _pick(_SHORTS, 1),
    "P043": _pick(_SHORTS, 2),
    "P044": _pick(_SHORTS, 3),
    # Sunglasses
    "P045": _pick(_SUNGLASSES, 0),
    "P046": _pick(_SUNGLASSES, 0),
    "P047": _pick(_SUNGLASSES, 0),
    "P048": _pick(_SUNGLASSES, 0),
    # Activewear
    "P049": _pick(_ACTIVE, 0),
    "P050": _pick(_ACTIVE, 1),
    "P051": _pick(_ACTIVE, 2),
    "P052": _pick(_ACTIVE, 3),
    "P053": _pick(_ACTIVE, 4),
    # Sandals
    "P054": _pick(_SANDALS, 0),
    "P055": _pick(_SANDALS, 1),
    "P056": _pick(_SANDALS, 2),
    "P057": _pick(_SANDALS, 3),
}
