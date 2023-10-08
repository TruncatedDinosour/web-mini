#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""minify css"""

import re

from . import clrs, const, recache

css_fns: recache.ReCache = recache.ReCache()


@css_fns.recache(r"/\*.*?\*/", re.S)
def css_remove_comments(pat: re.Pattern[str], css: str) -> str:
    """remove all useless comments"""
    return pat.sub("", css)


@css_fns.recache(r'([a-zA-Z]+)="([a-zA-Z0-9-_\.]+)"]')
def css_unquote_selectors(pat: re.Pattern[str], css: str) -> str:
    """remove quotes from selectors where theyre not needed"""
    return pat.sub(r"\1=\2]", css)


@css_fns.recache(r'url\((["\'])([^)]*)\1\)')
def css_remove_url_quotes(pat: re.Pattern[str], css: str) -> str:
    """remove useless quotes from url()"""
    return pat.sub(r"url(\2)", css)


@css_fns.recache(r"\s*({|}|:|;|,)\s*")
def css_remove_whitespace(pat: re.Pattern[str], css: str) -> str:
    """remove useless whitespace"""
    return pat.sub(r"\1", css).replace("and (", "and(").replace(") and", ")and").strip()


@css_fns.recache(r";;+")
def css_remove_semicolons(pat: re.Pattern[str], css: str) -> str:
    """remove useless semicolons"""
    return pat.sub("", css.replace(";}", "}"))


@css_fns.recache(r"(border|opacity):none")
def css_none_to_zero(pat: re.Pattern[str], css: str) -> str:
    """prop: none to prop: 0"""
    return pat.sub(r"\1:0", css)


@css_fns.recache(
    r"([\s:])(0)("
    r"em|ex|cap|ch|ic|rem|lh|rlh|vw|vh"
    r"|vi|vb|vmin|vmax|cqw|cqh|cqi|cqb|cqmin|cqmax"
    r"|cm|mm|Q|in|pc|pt|px|deg|grad|rad|turn"
    r"|s|ms|Hz|kHz|dpi|dpcm|dppx|x|fr|%"
    r")"
)
def css_sub_zero_units(pat: re.Pattern[str], css: str) -> str:
    """replace zero units with just zero"""
    return pat.sub(r"\1\2", css)


@css_fns.recache(r"(:|\s)0+\.(\d+)")
def css_shorten_floats(pat: re.Pattern[str], css: str) -> str:
    """shorten 0.x to .x"""
    return pat.sub(r"\1.\2", css)


@css_fns.recache(r"rgb\((\d+),\s*(\d+),\s*(\d+)\)")
def css_rgb2hex(pat: re.Pattern[str], css: str) -> str:
    """convert css rgb to hex"""
    return pat.sub(
        clrs.rgb_to_hex,
        css,
    )


@css_fns.recache(r"hsl\((\d+),\s*([\d.]+)%?,\s*([\d.]+)%?\)")
def css_hsl2hex(pat: re.Pattern[str], css: str) -> str:
    """convert css hsl to hex"""
    return pat.sub(
        clrs.hsl_to_hex,
        css,
    )


def css_sub_clrs(css: str) -> str:
    """replace built-in clrs w shorter hex colours"""

    for builtin, hexclr in const.REPLACABLE_CLRS.items():
        css = css.replace(f":{builtin}", hexclr)

    return css


@css_fns.recache(r"#([0-9a-fA-F]{6})")
def css_shorten_hex(pat: re.Pattern[str], css: str) -> str:
    """shorten hex like #xxyyzzaa to #xyza"""

    def shorten_clr(match: re.Match[str]) -> str:
        clr: str = match.group(1)

        if all(clr[idx] == clr[idx + 1] for idx in range(0, 5, 2)):
            return f"#{clr[0]}{clr[2]}{clr[4]}"

        return f"#{clr}"

    return pat.sub(shorten_clr, css)


@css_fns.recache(r"rgba\((\d+),\s*(\d+),\s*(\d+),\s*([\d.]+)\)")
def css_rgba2hex(pat: re.Pattern[str], css: str) -> str:
    """convert css rgba to hex"""
    return pat.sub(
        clrs.rgba_to_hex,
        css,
    )


@css_fns.recache(r"hsla\((\d+),\s*([\d.]+)%?,\s*([\d.]+)%?,\s*([\d.]+)\)")
def css_hsla2hex(pat: re.Pattern[str], css: str) -> str:
    """convert css hsla to hex"""
    return pat.sub(
        clrs.hsla_to_hex,
        css,
    )


@css_fns.recache(r"[^\}\{]+\{\}")
def css_remove_empty_rules(pat: re.Pattern[str], css: str) -> str:
    """remove empty rules"""
    return pat.sub("", css)


def css_font_weights(css: str) -> str:
    """shrink font weights"""

    return css.replace(
        "font-weight:normal",
        "font-weight:400",
    ).replace(
        "font-weight:bold",
        "font-weight:700",
    )


def minify_css(css: str) -> str:
    """run all css stages"""

    css_fns.compileall()

    css = css_remove_comments(css)
    css = css_remove_whitespace(css)
    css = css_unquote_selectors(css)
    css = css_remove_url_quotes(css)
    css = css_remove_semicolons(css)
    css = css_none_to_zero(css)
    css = css_sub_zero_units(css)
    css = css_shorten_floats(css)
    css = css_rgb2hex(css)
    css = css_hsl2hex(css)
    css = css_sub_clrs(css)
    css = css_shorten_hex(css)
    css = css_rgba2hex(css)
    css = css_hsla2hex(css)
    css = css_remove_empty_rules(css)
    css = css_font_weights(css)

    return css