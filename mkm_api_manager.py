from mkmsdk.mkm import Mkm
from mkmsdk.api_map import _API_MAP
from util import response_code_valid, pretty


mkm = Mkm(_API_MAP["2.0"]["api"], _API_MAP["2.0"]["api_root"])

standard_languages = ("English", "Italian", "Japanese", "Korean", "Russian", "S-Chinese")

condition_to_num = {
    "MT": 6,
    "NM": 5,
    "EX": 4,
    "GD": 3,
    "LP": 2,
    "PL": 1,
    "PO": 0
}


def get_products_from_user_in_range(user, min_limit, max_limit):
    return mkm.market_place.user_articles(
        user=user,
        params={
            "start": min_limit,
            "maxResults": max_limit
        }
    )


def get_products_from_user(user):

    is_last_response_valid = True
    min_limit = 0
    step = 1000

    articles = []

    while is_last_response_valid:
        response = get_products_from_user_in_range(user, min_limit, step)
        if response_code_valid(response.status_code) and len(response.json()["article"]) != 0:
            min_limit += step
            articles += response.json()["article"]
        else:
            is_last_response_valid = False

    return articles


def get_user_info(user):
    return mkm.market_place.user(user=user)


# Retrieve filtered articles based upon passed criteria
def filter_deals(articles, condition_min, threshold, min_price, max_price, languages):
    deals = {}

    articles_worth = list(filter(
        lambda article_listed:
            "condition" in article_listed and
            condition_to_num[article_listed["condition"]] >= condition_to_num[condition_min] and
            min_price <= article_listed["price"] < max_price and
            "language" in article_listed and
            article_listed["language"]["languageName"] in languages,
        articles)
    )

    print("Total articles: ", len(articles), " | Articles filtered: ", len(articles_worth))

    for article in articles_worth:
        product_info = get_article_info(article["idProduct"])

        if "isFoil" in article and article["isFoil"] is True:
            if is_foil_price_deal(article["price"], product_info["priceGuide"], threshold):

                print("{name}[{edition}](FOIL): {price} | LOWFOIL: {min_price}".format(
                    name=product_info["enName"],
                    edition=product_info["expansion"]["enName"],
                    price=article["price"],
                    min_price=product_info["priceGuide"]["LOWFOIL"]))

                deals[product_info["enName"]] = (article["price"], product_info["image"])

        elif is_price_deal(article["price"], product_info["priceGuide"], threshold):

                print("{name}[{edition}]: {price} | LOWEX: {min_price}".format(
                    name=product_info["enName"],
                    edition=product_info["expansion"]["enName"],
                    price=article["price"],
                    min_price=product_info["priceGuide"]["LOWEX"]))

                deals[product_info["enName"]] = (article["price"], product_info["image"])


def get_article_info(article_id):
    response = mkm.market_place.product(product=article_id)
    if response_code_valid(response.status_code):
        return response.json()["product"]


def is_price_deal(price, price_table, threshold):
    return True if price < (price_table["LOWEX"] + price_table["LOWEX"]*threshold) else False


def is_foil_price_deal(price, price_table, threshold):
    return True if price < (price_table["LOWFOIL"] + price_table["LOWFOIL"]*threshold) else False


def get_deals(user, condition_min="EX", threshold=0.15, min_price=3, max_price=11, languages=standard_languages):
    articles = get_products_from_user(user)
    return filter_deals(articles, condition_min, threshold, min_price, max_price, languages)


def get_wantlist_ids():
    return list(wantlist["idWantslist"] for wantlist in mkm.wants_list.get_all_wants_list().json()["wantslist"])


# Get each article in authenticated user wantlists in map form.
# Key -> idProduct/idMetaproduct | Value -> product/metaproduct
def get_all_articles_in_wantlists_as_map():
    for wantlist_id in get_wantlist_ids():
        wantlist_items = mkm.wants_list.get_wants_list(wants=wantlist_id).json()["wantslist"]["item"]
