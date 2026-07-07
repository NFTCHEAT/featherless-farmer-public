import html
import os
import random
import re
import time

import requests
from temp_gmail import GMail

DUSTMAIL_KEY = os.environ.get("DUSTMAIL_KEY", "dm_live_LsFGRHrqSkf86BCCu6qJOgdZRsygKzgf")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0 Safari/537.36"

LINK_RE = re.compile(r'https?://[^\s"\'<>)]+', re.IGNORECASE)
VERIFY_HINTS = ("verify", "confirm", "activate", "token", "email", "auth")


def _pick_verify_link(text):
    if not text:
        return None
    candidates = LINK_RE.findall(text)
    for url in candidates:
        low = url.lower()
        if "featherless.ai" in low and any(h in low for h in VERIFY_HINTS):
            return _clean(url)
    for url in candidates:
        if "featherless.ai" in url.lower():
            return _clean(url)
    for url in candidates:
        if any(h in url.lower() for h in ("verify", "confirm", "activate")):
            return _clean(url)
    return None


def _clean(url):
    return html.unescape(url).rstrip('".,)')


class TempGMail:
    name = "tempgmail"

    def create(self):
        g = GMail()
        email = g.create_email()
        return email, {"client": g}

    def wait_for_link(self, ctx, timeout=360, interval=5):
        g = ctx["client"]
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                msgs = g.load_list()
                for msg in msgs.get("messageData", []):
                    body = g.load_item(msg["messageID"])
                    link = _pick_verify_link(body)
                    if link:
                        return link
            except Exception:
                pass
            time.sleep(interval)
        return None


class MailTM:
    name = "mailtm"
    base = "https://api.mail.tm"

    def create(self):
        domains = requests.get(f"{self.base}/domains", timeout=15).json()
        domain = domains["hydra:member"][0]["domain"]
        addr = f"{self._random_name()}@{domain}"
        pw = "TempPass123!"
        r = requests.post(f"{self.base}/accounts", json={
            "address": addr, "password": pw,
        }, timeout=15)
        r.raise_for_status()
        acc = r.json()
        tok = requests.post(f"{self.base}/token", json={
            "address": addr, "password": pw,
        }, timeout=15).json()
        return addr, {"id": acc["id"], "token": tok["token"]}

    def wait_for_link(self, ctx, timeout=360, interval=5):
        h = {"Authorization": f"Bearer {ctx['token']}"}
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                r = requests.get(f"{self.base}/messages", headers=h, timeout=15)
                msgs = r.json().get("hydra:member", [])
                if msgs:
                    mid = msgs[0]["id"]
                    rr = requests.get(f"{self.base}/messages/{mid}", headers=h, timeout=15)
                    data = rr.json()
                    body = data.get("html") or data.get("text") or ""
                    link = _pick_verify_link(body)
                    if link:
                        return link
            except Exception:
                pass
            time.sleep(interval)
        return None

    @staticmethod
    def _random_name():
        import string
        return "".join(random.choices(string.ascii_lowercase + string.digits, k=12))


class DustMail:
    name = "dustmail"
    base = "https://dustmail.net"

    def create(self):
        h = {"User-Agent": UA, "Authorization": f"Bearer {DUSTMAIL_KEY}"}
        r = requests.post(self.base + "/api/v1/inbox", headers=h, timeout=15)
        r.raise_for_status()
        data = r.json()["data"]
        return data["email"], {"inbox_id": data["id"]}

    def wait_for_link(self, ctx, timeout=360, interval=5):
        inbox_id = ctx["inbox_id"]
        h = {"User-Agent": UA, "Authorization": f"Bearer {DUSTMAIL_KEY}"}
        deadline = time.time() + timeout
        while time.time() < deadline:
            try:
                r = requests.get(f"{self.base}/api/v1/inbox/{inbox_id}", headers=h, timeout=15)
                if r.status_code == 200:
                    emails = r.json().get("data", {}).get("emails", []) or []
                    for m in emails:
                        body = m.get("html") or m.get("text") or ""
                        link = _pick_verify_link(body)
                        if link:
                            return link
            except Exception:
                pass
            time.sleep(interval)
        return None


PROVIDERS = [TempGMail, MailTM, DustMail]


def pick_provider():
    return TempGMail()


if __name__ == "__main__":
    p = pick_provider()
    try:
        email, ctx = p.create()
        print(f"[OK]  {p.name} -> {email}")
    except Exception as e:
        print(f"[ERR] {p.name} -> {type(e).__name__}: {e}")
