import asyncio,aiohttp,logging
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from typing import Optional
from enum import Enum
from io import BytesIO


class Session():
    """
    The Session that is connected to the website
    """
    def __init__(self):
        self.session = None

    async def init(
        self,
        *,
        headers={
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:98.0) Gecko/20100101 Firefox/99.0"
        },
        cookies=None,
        cookie_jar=None,
    ):
        """
        Initialize the Session with given headers and cookies (optional)
        """
        logging.debug("Initializing Session...")
        self.session = aiohttp.ClientSession(
            base_url="https://rule34.us/",
            headers=headers,
            cookies=cookies,
            cookie_jar=cookie_jar,
        )
        return self

    async def close(self):
        """
        Close the Session
        """
        logging.debug("Closing Session...")
        await self.session.close()

    async def is_closed(self) -> bool:
        """
        Check if the Session is closed
        """
        return self.session.closed

    async def get_site_by_id(self, id) -> str:
        """
        Get a Site by it's id
        """
        async with self.session.get(f"/index.php?r=posts/view&id={id}") as response:
            html = await response.text()
        return html

    async def get_page_by_query(self, *, query="", page=0) -> None:
        """
        Get a Page containing multiple posts by a query
        """
        async with self.session.get(f"/index.php?r=posts/index&q={query}&page={page}") as response:
            html = await response.text()
        return html

class TagType(Enum):
    TAG = 1
    ARTIST = 2
    CHARACTER = 3
    COPYRIGHT = 4
    METADATA = 5

class Tag():
    def __init__(self, type: TagType, value: str):
        self.type = type
        self.value = value

    def __str__(self):
        return f"{self.type}: {self.value}"
    def __repr__(self):
        return f"{self.type}: {self.value}"

class Post():
    def __init__(self, id: str, hash: str, image_url: str, tags=[]):
        self.id = id
        self.hash = hash
        self.image_url = image_url
        self.tags = tags

    def __str__(self):
        return f"ID: {self.id} | HASH: {self.hash} -> IMG: {self.image_url} | tags: {self.tags}"

    def thumbnail_url(self) -> str:
        """
        Get a thumbnail url from the specified Post
        """
        url = self.image_url.replace("images", "thumbnails")
        last_slash_index = max([i for i, ltr in enumerate(url) if ltr == "/"])
        url = url[:last_slash_index] + "/thumbnail_" + url[last_slash_index+1:]
        last_point_index = max([i for i, ltr in enumerate(url) if ltr == "."])
        url = url[:last_point_index] + ".jpg"

        return url

    async def get_thumbnail(self) -> Optional[BytesIO]:
        """
        Get the thumbail image of a Post
        """
        logging.warning("Getting Images via this Library is currently not recommended as it is not very efficient implemented.")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.thumbnail_url()) as response:
                img = BytesIO(await response.read())
        return img

    async def get_image(self) -> Optional[BytesIO]:
        """
        Get the image of a Post
        """
        logging.warning("Getting Images via this Library is currently not recommended as it is not very efficient implemented.")
        async with aiohttp.ClientSession() as session:
            async with session.get(self.image_url) as response:
                img = BytesIO(await response.read())
        return img

    def tags_raw(self) -> list[str]:
        """
        Get all Tags as an array of strings
        """
        r = []

        for e in self.tags:
            r.append(e.value)
        return r

    def tags_obj(self):
        """
        Get all Tags as a dict of lists containing all tags
        """
        r = {
            "Tag": [],
            "Artist": [],
            "Character": [],
            "Copyright": [],
            "Metadata": [],
        }

        for e in self.tags:
            if TagType.METADATA == e.type:
                r["Metadata"].append(e)
            elif TagType.COPYRIGHT == e.type:
                r["Copyright"].append(e)
            elif TagType.CHARACTER == e.type:
                r["Character"].append(e)
            elif TagType.ARTIST == e.type:
                r["Artist"].append(e)
            else:
                r["Tag"].append(e)

        return r
