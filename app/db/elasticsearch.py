import logging

from elasticsearch import AsyncElasticsearch

from app.core.config import settings

logger = logging.getLogger(__name__)

es_client: AsyncElasticsearch = None


def get_es() -> AsyncElasticsearch:
    return es_client


async def connect_to_es() -> None:
    global es_client

    es_client = AsyncElasticsearch(hosts=settings.ES_URL)

    try:
        logger.info(f"Connecting to ElasticSearch on connection {settings.ES_URL}")

        es_info = await es_client.info()

        if not es_info:
            raise Exception("Elastic search connection is not valid")
        else:
            logger.info(f"Connection information: {es_info}")

    except Exception:
        logger.error("Could not connect to ElasticSearch", exc_info=True)


async def close_es_connection() -> None:
    global es_client

    if es_client is None:
        logger.warning("ElasticSearch client is None, nothing to close")
        return

    await es_client.close()

    es_client = None

    logger.info("ElasticSearch client connection closed")
