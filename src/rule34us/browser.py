import asyncio,aiohttp
from bs4 import BeautifulSoup
import logging
from typing import Optional

from .session import *


class Browser():
    def __init__(self, session: Session):
        self.session = session

    async def close(self):
        """
        Close the browser
        """
        await self.session.close()
        self.session = None

    async def get_post_by_id(self, id: str) -> Optional[Post]:
        """
        Get a Post by its id
        """
        if not self.session:
            logging.error("No Session is active")
            return None
        html = await self.session.get_site_by_id(id)
        soup = BeautifulSoup(html, "html.parser")

        # Get image url and hash
        content = soup.find("div", class_="content_push")
        if not content:
            logging.error("No content found. Either Host is down or library is out of date")
            return None

        url = content.img["src"]
        if not url:
            logging.error("Post has no url")
            return None
        last_slash_index = max([i for i, ltr in enumerate(url) if ltr == "/"])
        last_point_index = max([i for i, ltr in enumerate(url) if ltr == "."])
        hash = url[last_slash_index+1:last_point_index]

        # Get Tags
        taglist = soup.find(id="tag-list ") # Yes the website has a typo so it ends with a space
        artist = taglist.find_all("li", class_="artist-tag")
        character = taglist.find_all("li", class_="character-tag")
        copyright = taglist.find_all("li", class_="copyright-tag")
        metadata = taglist.find_all("li", class_="metadata-tag")
        tags = taglist.find_all("li", class_="general-tag")

        all_tags = []

        for e in artist:
            if not e.a:
                continue
            all_tags.append(Tag(TagType.ARTIST, e.a.string))
        for e in character:
            if not e.a:
                continue
            all_tags.append(Tag(TagType.CHARACTER, e.a.string))
        for e in copyright:
            if not e.a:
                continue
            all_tags.append(Tag(TagType.COPYRIGHT, e.a.string))
        for e in metadata:
            if not e.a:
                continue
            all_tags.append(Tag(TagType.METADATA, e.a.string))
        for e in tags:
            if not e.a:
                continue
            all_tags.append(Tag(TagType.TAG, e.a.string))

        return Post(
            id,
            hash,
            url,
            all_tags,
        )

    async def get_latest_post_id(self) -> Optional[str]:
        """
        Get the id of the newest available post.
        """
        if not self.session:
            logging.error("No Session is active")
            return None
        html = await self.session.get_page_by_query()
        soup = BeautifulSoup(html, "html.parser")
        content = soup.find("div", class_="thumbail-container") # Yes the website has a typo so the n is missing
        return content.div.a.get('id')

    async def get_latest_post_ids(self, *, max=100) -> Optional[list[str]]:
        """
        Get the ids of the newest available post.
        """
        if not self.session:
            logging.error("No Session is active")
            return None

        result = []
        p = 0
        while len(result) < max:
            html = await self.session.get_page_by_query(page=p)
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find("div", class_="thumbail-container") # Yes the website has a typo so the n is missing
            for e in content.children:
                if len(result) >= max:
                    break
                elif not e.a:
                    break
                else:
                    result.append(e.a.get('id'))
            p += 1

        return result

    async def get_search_results(self, query: str, *, max=100) -> Optional[list[str]]:
        if not self.session:
            logging.error("No Session is active")
            return None

        result = []
        p = 0
        while len(result) < max:
            act = False
            html = await self.session.get_page_by_query(query=query, page=p)
            soup = BeautifulSoup(html, "html.parser")
            content = soup.find("div", class_="thumbail-container") # Yes the website has a typo so the n is missing
            for e in content.children:
                if len(result) >= max:
                    break
                elif not e.a:
                    break
                else:
                    result.append(e.a.get('id'))
                    act = True
            p += 1
            if not act:
                break

        return result


    async def get_img_id_from_query(self, query: list[str], start_page=0, end_page=-1) -> Optional[list[str]]:
        """
        Get all imgs associated with the query.
        """
        result = []
        page = start_page
        while True:
            async with self.session.get(f"https://rule34.us/index.php?r=posts/index&q={'+'.join(query)}&page={page}") as response:
                if not response.status == 200:
                    break
                html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            container = soup.find("div", class_="thumbail-container")
            for e in container.find_all("a"):
                result.append(e["id"])
            print(page)
            page += 1
            if end_page > -1 and page >= end_page:
                break

        return result
