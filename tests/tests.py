import unittest,asyncio
from PIL import Image
import src.rule34us as r34

class TestBrowse(unittest.IsolatedAsyncioTestCase):
    async def test_post(self):
        session = await r34.Session().init()
        state = r34.Browser(session)
        post = await state.get_post_by_id("2")
        await state.close()
        self.assertEqual(post.image_url, "https://img2.rule34.us/images/7a/c2/7ac2ece6da2d181d866b22d25a8800d3.jpeg")
        self.assertTrue("akizora" in post.tags_raw())

    async def test_image_fetching(self):
        session = await r34.Session().init()
        state = r34.Browser(session)
        post = await state.get_post_by_id(await state.get_latest_post_id())
        await state.close()
        thumbnail = Image.open(await post.get_thumbnail())
        self.assertTrue(thumbnail)

    async def test_account(self):
        session = await r34.Session().init()
        account = r34.Account(session)
        await account.login("None3065", "Weird14")
        id = await account.get_account_id()
        self.assertEqual(id, "30249")
        await account.add_favourite("1")
        favs = await account.get_favourites(id, max=10)
        self.assertTrue("1" in favs)
        await account.remove_favourite("1")
        await account.logout()
        await session.close()

if __name__ == "__main__":
    unittest.main()
