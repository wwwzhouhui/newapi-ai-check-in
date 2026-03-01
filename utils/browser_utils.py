#!/usr/bin/env python3
"""
浏览器自动化相关的公共工具函数
"""

import os
import random
from datetime import datetime
from urllib.parse import urlparse


def parse_cookies(cookies_data) -> dict:
    """解析 cookies 数据

    支持字典格式和字符串格式的 cookies

    Args:
        cookies_data: cookies 数据，可以是字典或分号分隔的字符串

    Returns:
        解析后的 cookies 字典
    """
    if isinstance(cookies_data, dict):
        return cookies_data

    if isinstance(cookies_data, str):
        cookies_dict = {}
        for cookie in cookies_data.split(";"):
            if "=" in cookie:
                key, value = cookie.strip().split("=", 1)
                cookies_dict[key] = value
        return cookies_dict
    return {}


def filter_cookies(cookies: list[dict], origin: str) -> dict:
    """根据 origin 过滤 cookies，只保留匹配域名的 cookies

    Args:
        cookies: Camoufox cookies 列表，每个元素是包含 name, value, domain 等的字典
        origin: Provider 的 origin URL (例如: https://api.example.com)

    Returns:
        过滤后的 cookies 字典 {name: value}
    """
    # 提取 provider origin 的域名
    provider_domain = urlparse(origin).netloc

    # 过滤 cookies，只保留与 provider domain 匹配的
    user_cookies = {}
    matched_items = []  # 存储 "name(domain)" 格式
    filtered_items = []  # 存储 "name(domain)" 格式

    for cookie in cookies:
        cookie_name = cookie.get("name")
        cookie_value = cookie.get("value")
        cookie_domain = cookie.get("domain", "")

        if cookie_name and cookie_value:
            # 检查 cookie domain 是否匹配 provider domain
            # cookie domain 可能以 . 开头 (如 .example.com)，需要处理
            normalized_cookie_domain = cookie_domain.lstrip(".")
            normalized_provider_domain = provider_domain.lstrip(".")

            # 匹配逻辑：cookie domain 应该是 provider domain 的后缀
            if (
                normalized_provider_domain == normalized_cookie_domain
                or normalized_provider_domain.endswith("." + normalized_cookie_domain)
                or normalized_cookie_domain.endswith("." + normalized_provider_domain)
            ):
                user_cookies[cookie_name] = cookie_value
                matched_items.append(f"{cookie_name}({cookie_domain})")
            else:
                filtered_items.append(f"{cookie_name}({cookie_domain})")

    if matched_items:
        print(f"  🔵 Matched: {', '.join(matched_items)}")
    if filtered_items:
        print(f"  🔴 Filtered: {', '.join(filtered_items)}")

    print(
        f"🔍 Cookie filtering result ({provider_domain}): "
        f"{len(matched_items)} matched, {len(filtered_items)} filtered"
    )

    return user_cookies


def get_random_user_agent() -> str:
    """获取随机的现代浏览器 User Agent 字符串

    Returns:
        随机选择的 User Agent 字符串
    """
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 " "(KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:134.0) " "Gecko/20100101 Firefox/134.0",
    ]
    return random.choice(user_agents)


async def take_screenshot(
    page,
    reason: str,
    account_name: str,
    screenshots_dir: str = "screenshots",
) -> None:
    """截取当前页面的屏幕截图

    Args:
        page: Camoufox/Playwright 页面对象
        reason: 截图原因描述
        account_name: 账号名称（用于日志输出和文件名）
        screenshots_dir: 截图保存目录，默认为 "screenshots"

    Note:
        通过环境变量 DEBUG=true 启用截图功能，默认为 false
    """
    # 检查 DEBUG 环境变量
    debug_enabled = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    if not debug_enabled:
        print(f"🔍 {account_name}: Screenshot skipped (DEBUG=false), reason: {reason}")
        return

    try:
        os.makedirs(screenshots_dir, exist_ok=True)

        # 自动生成安全的账号名称
        safe_account_name = "".join(c if c.isalnum() else "_" for c in account_name)

        # 生成文件名: 账号名_时间戳_原因.png
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_reason = "".join(c if c.isalnum() else "_" for c in reason)
        filename = f"{safe_account_name}_{timestamp}_{safe_reason}.png"
        filepath = os.path.join(screenshots_dir, filename)

        await page.screenshot(path=filepath, full_page=True)
        print(f"📸 {account_name}: Screenshot saved to {filepath}")
    except Exception as e:
        print(f"⚠️ {account_name}: Failed to take screenshot: {e}")


async def save_page_content_to_file(
    page,
    reason: str,
    account_name: str,
    prefix: str = "",
    logs_dir: str = "logs",
) -> None:
    """保存页面 HTML 到日志文件

    Args:
        page: Camoufox/Playwright 页面对象
        reason: 日志原因描述
        account_name: 账号名称（用于日志输出和文件名）
        prefix: 文件名前缀（如 "github_", "linuxdo_" 等）
        logs_dir: 日志保存目录，默认为 "logs"

    Note:
        通过环境变量 DEBUG=true 启用保存 HTML 功能，默认为 false
    """
    # 检查 DEBUG 环境变量
    debug_enabled = os.getenv("DEBUG", "false").lower() in ("true", "1", "yes")

    if not debug_enabled:
        print(f"🔍 {account_name}: Save HTML skipped (DEBUG=false), reason: {reason}")
        return

    try:
        os.makedirs(logs_dir, exist_ok=True)

        # 自动生成安全的账号名称
        safe_account_name = "".join(c if c.isalnum() else "_" for c in account_name)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_reason = "".join(c if c.isalnum() else "_" for c in reason)

        # 构建文件名
        if prefix:
            filename = f"{safe_account_name}_{timestamp}_{prefix}_{safe_reason}.html"
        else:
            filename = f"{safe_account_name}_{timestamp}_{safe_reason}.html"
        filepath = os.path.join(logs_dir, filename)

        html_content = await page.content()
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        print(f"📄 {account_name}: Page HTML saved to {filepath}")
    except Exception as e:
        print(f"⚠️ {account_name}: Failed to save HTML: {e}")


async def aliyun_captcha_check(page, account_name: str) -> bool:
    """阿里云验证码检查和处理

    检查页面是否有阿里云验证码（通过 waf meta / traceid / renderData 检测），
    如果有则尝试自动滑动验证。

    Args:
        page: Camoufox/Playwright 页面对象
        account_name: 账号名称（用于日志输出）

    Returns:
        bool: 验证码处理是否成功（无验证码或验证通过返回 True，验证失败返回 False）
    """

    async def _detect_waf_state() -> dict:
        """检测当前页面是否为阿里云 WAF 验证页，并提取 traceid。"""
        return await page.evaluate(
            """() => {
            const result = {
                has_waf_meta: !!document.querySelector('meta[name="aliyun_waf_aa"], meta[name="aliyun_waf_bb"]'),
                has_captcha_container: !!document.querySelector('#nocaptcha, #captcha-element, #h5_captcha-element, .nc-container'),
                traceid: null,
            };

            const extractTraceId = (text) => {
                if (!text) return null;
                const m = text.match(/TraceID:\\s*([a-f0-9]+)/i);
                return m ? m[1] : null;
            };

            // 1) 传统 traceid 容器
            const traceElement = document.getElementById('traceid');
            if (traceElement) {
                result.traceid = extractTraceId(traceElement.innerText || traceElement.textContent);
            }

            // 2) 新版页面用 newTraceid
            if (!result.traceid) {
                const newTraceElement = document.getElementById('newTraceid');
                if (newTraceElement) {
                    result.traceid = extractTraceId(newTraceElement.innerText || newTraceElement.textContent);
                }
            }

            // 3) 从 renderData 中提取 requestInfo.traceid
            if (!result.traceid) {
                const renderData = document.getElementById('renderData');
                if (renderData && renderData.value) {
                    const marker = 'var requestInfo = ';
                    const raw = renderData.value;
                    const idx = raw.indexOf(marker);
                    if (idx !== -1) {
                        const jsonText = raw.slice(idx + marker.length).trim().replace(/;\\s*$/, '');
                        try {
                            const info = JSON.parse(jsonText);
                            if (info && info.traceid) {
                                result.traceid = info.traceid;
                            }
                        } catch (e) {
                            // ignore parse error
                        }
                    }
                }
            }

            return result;
        }"""
        )

    try:
        state = await _detect_waf_state()
        traceid = state.get("traceid")
        has_waf_meta = state.get("has_waf_meta", False)
        has_captcha_container = state.get("has_captcha_container", False)

        # 非验证页，直接通过
        if not has_waf_meta and not traceid and not has_captcha_container:
            print(f"ℹ️ {account_name}: No aliyun captcha detected")
            await take_screenshot(page, "aliyun_captcha_not_detected", account_name)
            return True

        print(
            f"⚠️ {account_name}: Aliyun captcha detected"
            f" (traceid: {traceid if traceid else 'N/A'})"
        )
        await take_screenshot(page, "aliyun_captcha_detected", account_name)

        try:
            await page.wait_for_selector(
                "#nocaptcha, #captcha-element, #h5_captcha-element, .nc-container",
                timeout=20000,
            )
        except Exception:
            # 页面异步渲染，稍作等待
            await page.wait_for_timeout(3000)

        slider_selectors = [
            "#nocaptcha .nc_scale",
            "#aliyunCaptcha-sliding-slider",
            ".nc_scale",
            "[id*='sliding-slider']",
        ]

        handle_selectors = [
            "#nocaptcha .btn_slide",
            ".btn_slide",
            ".nc_iconfont.btn_slide",
            "[class*='btn_slide']",
            "span.btn_slide",
            "div[role='button'][class*='slide']",
            "#aliyunCaptcha-sliding-slider + *",
        ]

        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            slider = None
            slider_selector = None
            for selector in slider_selectors:
                element = await page.query_selector(selector)
                if element:
                    box = await element.bounding_box()
                    if box:
                        slider = box
                        slider_selector = selector
                        break

            handle = None
            handle_selector = None
            for selector in handle_selectors:
                element = await page.query_selector(selector)
                if element:
                    box = await element.bounding_box()
                    if box:
                        handle = box
                        handle_selector = selector
                        break

            if slider and handle:
                # 规范化：handle 应该是较窄的滑块，slider 应该是较宽的轨道
                # 某些页面选择器会反过来命中（例如 #aliyunCaptcha-sliding-slider + *）
                slider_width = slider.get("width", 0)
                handle_width = handle.get("width", 0)
                if handle_width > slider_width:
                    slider, handle = handle, slider
                    slider_selector, handle_selector = handle_selector, slider_selector

                print(f"ℹ️ {account_name}: [attempt {attempt}/{max_attempts}] Slider selector: {slider_selector}, box: {slider}")
                print(f"ℹ️ {account_name}: [attempt {attempt}/{max_attempts}] Handle selector: {handle_selector}, box: {handle}")
                await take_screenshot(page, "aliyun_captcha_slider_start", account_name)

                start_x = handle.get("x") + handle.get("width") / 2
                start_y = handle.get("y") + handle.get("height") / 2
                # 目标点设为轨道右端减去滑块半宽，避免拖过头
                target_x = slider.get("x") + slider.get("width") - handle.get("width") / 2 - 2

                await page.mouse.move(start_x, start_y)
                await page.mouse.down()
                await page.mouse.move(target_x, start_y, steps=40)
                await page.wait_for_timeout(500)
                await page.mouse.up()

                await take_screenshot(page, "aliyun_captcha_slider_completed", account_name)
                await page.wait_for_timeout(10000)
                await take_screenshot(page, "aliyun_captcha_slider_result", account_name)
            else:
                # 新版阿里云验证码通常不暴露可拖拽 DOM，尝试直接等待/点击触发一次交互后再检测
                print(f"⚠️ {account_name}: [attempt {attempt}/{max_attempts}] Slider or handle not found, trying soft interaction fallback")
                try:
                    await page.mouse.move(360, 420)
                    await page.mouse.click(360, 420)
                    await page.wait_for_timeout(8000)
                except Exception as e:
                    print(f"⚠️ {account_name}: Soft interaction fallback failed: {e}")
                await take_screenshot(page, "aliyun_captcha_error", account_name)

            post_state = await _detect_waf_state()
            post_has_waf_meta = post_state.get("has_waf_meta", False)
            post_traceid = post_state.get("traceid")
            post_has_captcha_container = post_state.get("has_captcha_container", False)
            print(
                f"ℹ️ {account_name}: [attempt {attempt}/{max_attempts}] Post-check "
                f"has_waf_meta={post_has_waf_meta}, traceid={post_traceid if post_traceid else 'N/A'}, "
                f"has_captcha_container={post_has_captcha_container}"
            )

            if not post_has_waf_meta and not post_traceid and not post_has_captcha_container:
                print(f"✅ {account_name}: Aliyun captcha verification passed")
                return True

        # 重试后仍失败
        final_state = await _detect_waf_state()
        final_traceid = final_state.get("traceid")
        print(
            f"❌ {account_name}: Aliyun captcha still present after {max_attempts} attempts"
            f" (traceid: {final_traceid if final_traceid else 'N/A'})"
        )
        return False

    except Exception as e:
        print(f"❌ {account_name}: Error occurred while processing aliyun captcha, {e}")
        await take_screenshot(page, "aliyun_captcha_error", account_name)
        return False
