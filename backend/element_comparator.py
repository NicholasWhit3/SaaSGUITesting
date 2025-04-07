import json
from backend.logger import logger

def compare_elements(figma_elements, website_elements):
    differences = []
    matched_elements = []

    for figma_element in figma_elements:
        selector = figma_element.get("selector") or figma_element.get("name")
        if not selector:
            logger.warning("Figma element without a selector or name, skipping.")
            continue

        expected_styles = {
            "width": figma_element.get("width"),
            "height": figma_element.get("height"),
            "color": figma_element.get("color"),
            "background-color": figma_element.get("background-color"),
            "font-family": figma_element.get("font-family"),
            "font-size": figma_element.get("font-size"),
            "margin": figma_element.get("margin"),
            "padding": figma_element.get("padding"),
            "border": figma_element.get("border"),
        }

        actual_element = next((e for e in website_elements if e.get("selector") == selector or e.get("tag") == selector), None)

        if actual_element:
            mismatches = []
            for style, expected_value in expected_styles.items():
                actual_value = actual_element.get(style)
                if expected_value and actual_value and expected_value != actual_value:
                    mismatches.append({
                        "property": style,
                        "expected": expected_value,
                        "actual": actual_value
                    })

            if mismatches:
                differences.append({
                    "element": selector,
                    "issue": "Style mismatch",
                    "details": mismatches
                })
                logger.warning(f"Mismatch in {selector}: {mismatches}")
            else:
                matched_elements.append({"element": selector})
        else:
            differences.append({
                "element": selector,
                "issue": "Element not found on the website"
            })
            logger.error(f"Element {selector} not found on the website")

    return {"differences": differences, "matched": matched_elements}
