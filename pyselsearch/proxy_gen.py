import os
import json


def create_proxy_auth_extension(
    proxy_host,
    proxy_port,
    proxy_user,
    proxy_pass,
    extension_dir="proxy_extension"
):
    os.makedirs(extension_dir, exist_ok=True)

    # manifest.json
    manifest_json = {
        "name": "Proxy Auth Extension",
        "version": "1.0.0",
        "manifest_version": 3,
        "permissions": [
            "proxy",
            "storage",
            "tabs",
            "scripting",
            "webRequest",
            "webRequestAuthProvider"
        ],
        "host_permissions": ["<all_urls>"],
        "background": {
            "service_worker": "background.js"
        },
        "action": {
            "default_title": "Proxy Auth Extension"
        }
    }

    background_js = f"""
chrome.proxy.settings.set(
    {{
        value: {{
            mode: "fixed_servers",
            rules: {{
                singleProxy: {{
                    scheme: "http",
                    host: "{proxy_host}",
                    port: parseInt({proxy_port})
                }},
                bypassList: ["localhost"]
            }}
        }},
        scope: "regular"
    }},
    function() {{}}
);

chrome.webRequest.onAuthRequired.addListener(
    function(details) {{
        return {{
            authCredentials: {{
                username: "{proxy_user}",
                password: "{proxy_pass}"
            }}
        }};
    }},
    {{ urls: ["<all_urls>"] }},
    ["blocking"]
);
"""

    # Write files
    with open(os.path.join(extension_dir, "manifest.json"), "w") as f:
        json.dump(manifest_json, f, indent=2)

    with open(os.path.join(extension_dir, "background.js"), "w") as f:
        f.write(background_js)

    return os.path.abspath(extension_dir)
