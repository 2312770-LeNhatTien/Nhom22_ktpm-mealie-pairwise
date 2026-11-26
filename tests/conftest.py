import pytest

from chung import Api
from loi_da_bao import LOI_DA_BAO


@pytest.fixture(scope="session")
def api():
    return Api()


def tim_hoac_tao(api, path_list, path_create, ten):
    s, d = api("GET", path_list, params={"perPage": 200})
    for it in d["items"]:
        if it.get("name") == ten:
            return it
    s, d = api("POST", path_create, json={"name": ten})
    assert s in (200, 201), (path_create, s, d)
    return d


@pytest.fixture(scope="session")
def nen(api):
    n = {}
    s, d = api("GET", "/api/organizers/categories", params={"perPage": 50})
    cats = {c["name"]: c for c in d["items"]}
    s, d = api("GET", "/api/organizers/tags", params={"perPage": 50})
    tags = {t["name"]: t for t in d["items"]}
    n["cats"] = [cats["Món chính"], cats["Tráng miệng"]]
    n["tags"] = [tags["Chay"], tags["Nhanh"]]
    n["unit"] = tim_hoac_tao(api, "/api/units", "/api/units", "PW-gram")
    n["food"] = tim_hoac_tao(api, "/api/foods", "/api/foods", "PW-ca chua")
    s, d = api("GET", "/api/groups/labels", params={"perPage": 200})
    lab = next((x for x in d["items"] if x["name"] == "PW-rau cu"), None)
    if lab is None:
        s, lab = api("POST", "/api/groups/labels", json={"name": "PW-rau cu", "color": "#4caf50"})
    n["label"] = lab
    s, d = api("GET", "/api/recipes", params={"search": "Phở bò", "perPage": 1})
    n["recipe_id"] = d["items"][0]["id"]
    return n


def pytest_collection_modifyitems(items):
    for it in items:
        if it.name in LOI_DA_BAO:
            it.add_marker(pytest.mark.xfail(reason=LOI_DA_BAO[it.name], strict=False))
