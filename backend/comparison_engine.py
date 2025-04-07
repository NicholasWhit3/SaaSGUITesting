import os
import sys
import time
import asyncio
import requests
from fastapi import APIRouter, Body
from fastapi.responses import JSONResponse
from playwright.sync_api import sync_playwright

from backend.logger import logger
from backend.element_comparator import compare_elements

# === Initializing ===
router = APIRouter()


# Windows-specific asyncio fix
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


# === Auxiliary functions ===

def handle_popups(page):
    """Closes the most typical pop-ups on the site."""
    popup_selectors = [
        '[id*="cookie"] button', '[class*="cookie"] button', '[aria-label*="cookie"]',
        '[id*="consent"] button', '[class*="consent"] button', '[aria-label*="consent"]',
        '[id*="close"]', '[class*="close"]', '[aria-label*="close"]'
    ]
    for selector in popup_selectors:
        try:
            element = page.query_selector(selector)
            if element:
                element.click()
                logger.info(f"Closed pop-up: {selector}")
        except Exception as e:
            logger.warning(f"Failed to close the pop-up {selector}: {e}")


def capture_website_data(url, selectors=None):
    """Loads the site and collects CSS styles of elements."""
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url, timeout=30000)
            logger.info(f"Page {url} loaded.")
        except Exception as e:
            logger.error(f"Error when opening the site {url}: {e}")
            return []

        handle_popups(page)

        elements = []
        targets = (
            [page.query_selector(s.strip()) for s in selectors.split(",")]
            if selectors else page.query_selector_all("*")
        )

        for element in filter(None, targets):
            try:
                style = page.evaluate("el => window.getComputedStyle(el)", element)
                tag = page.evaluate("el => el.tagName", element)
                elements.append({
                    "tag": tag,
                    "selector": page.evaluate("el => el.outerHTML", element)[:100],
                    "color": style.get("color", "N/A"),
                    "background": style.get("backgroundColor", "N/A"),
                    "fontSize": style.get("fontSize", "N/A"),
                    "fontFamily": style.get("fontFamily", "N/A"),
                    "margin": style.get("margin", "N/A"),
                    "padding": style.get("padding", "N/A"),
                })
            except Exception as e:
                logger.warning(f"Element could not be processed: {e}")
                continue

        browser.close()
        return elements


def get_figma_data(figma_url):
    """Failed to process element:Retrieves styles from the Figma API from the link."""
    if not figma_url:
        logger.error("❌ Figma URL absent.")
        return []

    try:
        file_key = figma_url.split("/file/")[1].split("/")[0]
    except IndexError:
        logger.error("❌ Not valid Figma URL format.")
        return []

    headers = {"X-Figma-Token": os.getenv("FIGMA_ACCESS_TOKEN")}
    api_url = f"https://api.figma.com/v1/files/{file_key}"

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()
        figma_data = response.json()
        logger.info("✅ Data from the Figma API was obtained successfully.")

        if "document" not in figma_data:
            logger.error("❌ The Figma API response does not contain a 'document' field.")
            return []

        elements = []

        def extract_elements(node, depth=0):
            name = node.get("name", "Unnamed")
            indent = "  " * depth

            if "absoluteBoundingBox" in node:
                # Protection against missing fills
                fills = node.get("fills")
                if isinstance(fills, list) and len(fills) > 0 and isinstance(fills[0], dict):
                    color = fills[0].get("color", "N/A")
                else:
                    color = "N/A"

                element_data = {
                    "name": name,
                    "width": node["absoluteBoundingBox"].get("width"),
                    "height": node["absoluteBoundingBox"].get("height"),
                    "color": color,
                    "font-size": node.get("style", {}).get("fontSize", "N/A"),
                    "font-family": node.get("style", {}).get("fontFamily", "N/A")
                }
                logger.debug(f"{indent}🎯 Element: {name}, style: {element_data}")
                elements.append(element_data)
            else:
                logger.debug(f"{indent}⏩ Missed: {name} (no absolute coordinates)")

            for child in node.get("children", []):
                extract_elements(child, depth + 1)

        extract_elements(figma_data["document"])
        logger.info(f"📦 Total {len(elements)} elements from figma.")
        return elements

    except requests.RequestException as e:
        logger.error(f"❌ Figma API Error: {e}")
        return []


# === API endpoint ===

@router.post("/run-test")
def check_gui(
    website_url: str = Body(...),
    figma_url: str = Body(None),
    selectors: str = Body(None)
):
    logger.info(f"🔍 Run test: {website_url} | Selectors: {selectors or 'all'}")
    start_time = time.time()

    try:
        website_data = capture_website_data(website_url, selectors)
        figma_data = get_figma_data(figma_url) if figma_url else []

        if not figma_data:
            logger.warning("⚠️ Data from Figma is empty or not received.")

        comparison = compare_elements(figma_data, website_data)
        duration = round(time.time() - start_time, 2)
        logger.info(f"✅ Test completed for {duration} s")

        return {
            "status": "success",
            "differences": comparison["differences"],
            "matched": comparison["matched"],
            "elements": website_data,
            "execution_time": duration,
        }

    except Exception as e:
        logger.exception("❌ Error during testing")
        return JSONResponse(status_code=500, content={
            "status": "error",
            "message": str(e),
        })

@router.get("/ping")
def ping():
    return {"message": "Service is alive!"}
