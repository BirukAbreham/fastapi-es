import logging
import uuid

import numpy as np
import pandas as pd
from elasticsearch import AsyncElasticsearch
from elasticsearch.helpers import async_bulk
from fastapi import APIRouter, Depends

from app.core.config import settings
from app.db.elasticsearch import get_es

logger = logging.getLogger(__name__)

router = APIRouter()

index_mappings = {
    "properties": {
        "id": {"type": "integer"},
        "type": {"type": "text", "analyzer": "standard"},
        "sku": {"type": "text", "analyzer": "standard"},
        "name": {"type": "text", "analyzer": "standard"},
        "published": {"type": "boolean"},
        "is_featured": {"type": "boolean"},
        "visibility_in_catalog": {
            "type": "text",
            "analyzer": "standard",
        },
        "short_description": {"type": "text", "analyzer": "standard"},
        "description": {"type": "text", "analyzer": "standard"},
        "in_stock": {"type": "boolean"},
        "stock": {"type": "integer"},
        "backorders_allowed": {"type": "boolean"},
        "sold_individually": {"type": "boolean"},
        "allow_customer_reviews": {"type": "boolean"},
        "regular_price": {"type": "double"},
        "categories": {"type": "text", "analyzer": "standard"},
        "parent": {"type": "text", "analyzer": "standard"},
    }
}

selected_cols = [
    "ID",
    "Type",
    "SKU",
    "Name",
    "Published",
    "Is featured?",
    "Visibility in catalog",
    "Short description",
    "description",
    "In stock?",
    "Stock",
    "Backorders allowed?",
    "Sold individually?",
    "Allow customer reviews?",
    "Regular price",
    "Categories",
    "Parent",
]

rename_cols = [
    "id",
    "type",
    "sku",
    "name",
    "published",
    "is_featured",
    "visibility_in_catalog",
    "short_description",
    "description",
    "in_stock",
    "stock",
    "backorders_allowed",
    "sold_individually",
    "allow_customer_reviews",
    "regular_price",
    "categories",
    "parent",
]


@router.post("/index-data")
async def load_and_index_data(
    es: AsyncElasticsearch = Depends(get_es),
):
    # create the index on the elasticsearch cluster if it does not exist
    list_of_indices = await es.indices.get_alias(index="*")

    if "products" not in list_of_indices:
        logger.info(
            "creating the index for 'products' with the 'index_mappings' provided"
        )
        await es.indices.create(index="products", mappings=index_mappings)
    else:
        logger.info("deleting existing index and creating a new one")
        await es.indices.delete(index="products")
        await es.indices.create(index="products", mappings=index_mappings)

    # load the dataset
    df = pd.read_csv(settings.DATASET_FILE)

    # select, rename, and clean the data
    df = df[selected_cols]
    df.columns = rename_cols
    df["published"] = df["published"].astype(bool)
    df["is_featured"] = df["is_featured"].astype(bool)
    df["in_stock"] = df["in_stock"].astype(bool)
    df["backorders_allowed"] = df["backorders_allowed"].astype(bool)
    df["sold_individually"] = df["sold_individually"].astype(bool)
    df["allow_customer_reviews"] = df["allow_customer_reviews"].astype(bool)
    df = df.replace(np.nan, None)

    # async iterate over the dataframe
    async def df_data():
        for idx, row in df.iterrows():
            yield {
                "_index": "products",
                "_id": str(uuid.uuid4()),
                "_source": {
                    "id": row["id"],
                    "type": row["type"],
                    "sku": row["sku"],
                    "name": row["name"],
                    "published": row["published"],
                    "is_featured": row["is_featured"],
                    "visibility_in_catalog": row["visibility_in_catalog"],
                    "short_description": row["short_description"],
                    "description": row["description"],
                    "in_stock": row["in_stock"],
                    "stock": row["stock"],
                    "backorders_allowed": row["backorders_allowed"],
                    "sold_individually": row["sold_individually"],
                    "allow_customer_reviews": row["allow_customer_reviews"],
                    "regular_price": row["regular_price"],
                    "categories": row["categories"],
                    "parent": row["parent"],
                },
            }

    # bulk indexing
    response = await async_bulk(es, df_data())

    return {
        "status": "success",
        "message": f"indexed {response[0]} number of records",
    }


@router.get("/search")
async def search_from_es(es: AsyncElasticsearch = Depends(get_es)):
    query = {"match_phrase": {"name": "Hoodies"}}

    response = await es.search(index="products", query=query)

    return response
