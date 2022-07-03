from .session import *

class Account():
    def __init__(self, session: Session):
        self.session = session

    async def login(self, username, password):
        if not self.session:
            logging.error("No Session is active")
            return None
        payload = {
            "user": username,
            "pass": password,
        }
        async with await self.session.session.post("/index.php?r=account/login", data=payload) as response:
            if response.status == 200:
                logging.info("Logged in successfully")
            else:
                logging.warning(f"Login failed: received {response.status}")

    async def logout(self):
        if not self.session:
            logging.error("No Session is active")
            return None
        async with await self.session.session.get("/index.php?r=account/logout") as response:
            if response.status == 200:
                logging.info("Logged out successfully")
            else:
                logging.warning(f"Logout failed: received {response.status}")

    async def get_account_id(self) -> str:
        if not self.session:
            logging.error("No Session is active")
            return None
        cookies = self.session.session.cookie_jar
        for cookie in self.session.session.cookie_jar:
            if cookie.key == "user_id":
                return cookie.value
        return None

    async def add_favourite(self, id: str) -> str:
        async with await self.session.session.get(f"/index.php?r=favorites/create&id={id}") as response:
            code = await response.text()
        if code == "1":
            logging.warning("Post already in favorites")
        elif code == "2":
            logging.warning("Not logged in")
        else:
            logging.info("Post added to favorites")

    async def remove_favourite(self, id: str):
        async with await self.session.session.get(f"/index.php?r=favorites/delete&id={id}") as response:
            code = response.status

    async def get_favourites(self, id, *, max=100) -> Optional[list[str]]:
        if not self.session:
            logging.error("No Session is active")
            return None

        result = []
        p = 0
        while len(result) < max:
            act = False
            async with await self.session.session.get(f"/index.php?r=favorites/view&id={id}&page={p}") as response:
                html = await response.text()
            soup = BeautifulSoup(html, "html.parser")
            for e in soup.find_all("div", class_="thumbnail-preview"):
                a_s = e.find_all("a")
                if len(result) >= max:
                    break
                elif not a_s:
                    break
                else:
                    result.append(a_s[1].get('id').replace("p", ""))
                    act = True
            p += 1
            if not act:
                break

        return result
