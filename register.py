"""
register.py — регистрация на featherless.ai через Playwright.
"""
import os
import re
import time

from playwright.sync_api import sync_playwright

from capzy_solver import solve_turnstile

REGISTER_URL = "https://featherless.ai/register"
KEYS_URL = "https://featherless.ai/account/api-keys"
TURNSTILE_SITEKEY = "0x4AAAAAADwBXIixBQUgukBi"

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/149.0 Safari/537.36")

KEY_RE = re.compile(r'rc_[A-Za-z0-9]{20,}')


MOCK_TURNSTILE_JS = """
window.turnstile = {
    render: function(container, params) {
        window.__turnstileCB = params.callback;
        return 'mock-widget';
    },
    getResponse: function() { return ''; },
    reset: function() {},
    remove: function() {},
    ready: function(cb) { if (cb) setTimeout(cb, 0); }
};
"""


def _inject_turnstile_token(page, token):
    return page.evaluate("""(token) => {
        if (window.__turnstileCB) {
            window.__turnstileCB(token);
            return 'callback';
        }
        const ta = document.querySelector('textarea[name="cf-turnstile-response"]');
        if (ta) {
            const nativeSetter = Object.getOwnPropertyDescriptor(HTMLTextAreaElement.prototype, 'value').set;
            nativeSetter.call(ta, token);
            ta.dispatchEvent(new Event('input', { bubbles: true }));
            ta.dispatchEvent(new Event('change', { bubbles: true }));
            return 'textarea';
        }
        return 'noop';
    }""", token)


def _register_account(page, email, password):
    page.route("**/turnstile/v0/api.js**", lambda route: route.fulfill(
        content_type="application/javascript",
        body=MOCK_TURNSTILE_JS,
    ))
    page.goto(REGISTER_URL, wait_until="domcontentloaded")
    try:
        page.get_by_role("button", name="Allow all").click(timeout=3000)
    except Exception:
        pass
    page.wait_for_function("() => window.__turnstileCB !== null", timeout=15000)
    print("    [captcha] Turnstile render перехвачен (мок)")
    page.get_by_role("textbox", name="Email address").fill(email)
    page.get_by_role("textbox", name="Password").fill(password)
    page.wait_for_timeout(500)

    print("    [captcha] решаю Turnstile через Capzy...")
    token = solve_turnstile(TURNSTILE_SITEKEY, REGISTER_URL)
    print(f"    [captcha] Turnstile решён, токен: {token[:40]}...")
    _inject_turnstile_token(page, token)
    print("    [captcha] токен инжектнут")
    page.wait_for_timeout(1000)
    page.get_by_role("button", name="Create Account").click()
    page.wait_for_timeout(3000)
    print(f"    [register] отправлено для {email}")


def _verify_and_get_key(page, browser, link):
    page.goto(link, wait_until="domcontentloaded")
    page.wait_for_timeout(5000)
    print("    [verify] почта подтверждена")
    page.goto(KEYS_URL, wait_until="domcontentloaded")
    page.wait_for_timeout(3000)
    return get_key(page)


def run_registration(email, password, mail_ctx, provider, headless=True):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(
            user_agent=UA,
            permissions=["clipboard-read", "clipboard-write"],
        )
        page = context.new_page()

        # Phase 1: register
        try:
            _register_account(page, email, password)
        except Exception:
            browser.close()
            raise

        # Phase 2: wait for email (browser stays open, session preserved)
        print("    [verify] жду письмо (до 3 мин)...")
        link = provider.wait_for_link(mail_ctx, timeout=180, interval=10)
        if not link:
            print("    [verify] письмо не пришло за 3 мин")
            browser.close()
            return None
        print("    [verify] ссылка получена")

        # Phase 3: verify + get key (same browser, same session)
        api_key = _verify_and_get_key(page, browser, link)
        browser.close()
        return api_key


def _scan_for_key(page):
    try:
        js = """() => {
            let out = [];
            for (const el of document.querySelectorAll('input, textarea')) {
                if (el.value) out.push(el.value);
            }
            out.push(document.body ? document.body.innerText : '');
            return out.join('\\n');
        }"""
        blob = page.evaluate(js) or ""
        m = KEY_RE.search(blob)
        if m:
            return m.group(0)
    except Exception:
        pass

    try:
        for inp in page.query_selector_all("input, textarea"):
            try:
                val = (inp.input_value() or "").strip()
            except Exception:
                val = (inp.get_attribute("value") or "").strip()
            if val.startswith("rc_") and len(val) > 20:
                return val
    except Exception:
        pass

    try:
        m = KEY_RE.search(page.content())
        if m:
            return m.group(0)
    except Exception:
        pass
    return None


def _dump_debug(page):
    try:
        with open("debug_keys_page.html", "w", encoding="utf-8") as f:
            f.write(page.content())
        page.screenshot(path="debug_keys_page.png")
        print("    [keys] сохранил debug_keys_page.html и .png — пришли их мне")
    except Exception as e:
        print(f"    [keys] не смог сохранить дамп: {e}")


def get_key(page):
    api_key = None
    try:
        # Кнопка New API Key может быть disabled — кликаем через JS dispatchEvent
        print("    [keys] жду кнопку New API Key (до 60 сек)...")
        page.wait_for_function("() => document.querySelector('button[title=\"New API Key\"]') !== null", timeout=60000)
        page.evaluate("""() => {
            const btn = document.querySelector("button[title='New API Key']");
            if (btn) {
                btn.removeAttribute('disabled');
                btn.style.pointerEvents = 'auto';
                btn.style.opacity = '1';
                setTimeout(() => btn.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true})), 100);
            }
        }""")
        page.wait_for_timeout(3000)
        print("    [keys] клик по New API Key отправлен через JS")

        # Ждём появления диалога и кнопки Create
        clicked = False
        for name in ("Create", "Create key", "Create API Key", "Generate", "Confirm"):
            try:
                cbtn = page.locator(f"button:has-text('{name}')").first
                cbtn.wait_for(state="visible", timeout=5000)
                cbtn.click(timeout=5000)
                clicked = True
                print(f"    [keys] нажал подтверждение: {name}")
                break
            except Exception:
                continue
        if not clicked:
            print("    [keys] не нашёл кнопку Create/Generate — пробую через JS")
            for txt in ("Create", "Create key", "Create API Key", "Generate", "Confirm"):
                found = page.evaluate(f"""(txt) => {{
                    const btns = document.querySelectorAll('button');
                    for (const b of btns) {{
                        if (b.textContent.includes(txt)) {{
                            b.click();
                            return txt;
                        }}
                    }}
                    return null;
                }}""", txt)
                if found:
                    clicked = True
                    print(f"    [keys] нажал через JS: {found}")
                    break
        if not clicked:
            print("    [keys] не нашёл кнопку Create — сохраняю дамп")
            _dump_debug(page)

        page.wait_for_timeout(1500)
        print("    [keys] жду появления rc_ (до 30 сек)...")

        for _ in range(60):
            api_key = _scan_for_key(page)
            if api_key:
                break
            page.wait_for_timeout(500)

        if not api_key:
            try:
                copy_btn = page.locator("button:has-text('copy')").first
                copy_btn.wait_for(state="visible", timeout=3000)
                copy_btn.click(timeout=3000)
                page.wait_for_timeout(500)
                clip = page.evaluate("() => navigator.clipboard.readText()") or ""
                m = KEY_RE.search(clip)
                if m:
                    api_key = m.group(0)
                    print("    [keys] ключ взят из буфера")
            except Exception:
                pass

        if api_key:
            print(f"    [keys] КЛЮЧ НАЙДЕН: {api_key}")
        else:
            print("    [keys] rc_ не найден — сохраняю дамп")
            _dump_debug(page)

        try:
            done_btn = page.locator("button:has-text('Done')").first
            done_btn.click(timeout=3000)
            print("    [keys] нажал Done")
        except Exception:
            pass
    except Exception as e:
        print(f"    [keys] ошибка: {e}")
    return api_key
