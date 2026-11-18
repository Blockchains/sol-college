"""Shared helpers for public curriculum copy (limits, prerequisites, inventory labels)."""
from __future__ import annotations
import ast
import re


def format_limit_text(lim):
  """Public copy must not leak raw Python list/dict syntax."""
  if lim is None or lim == '':
    return ''
  if isinstance(lim, (list, tuple)):
    parts = [str(p).strip() for p in lim if str(p).strip()]
    return '; '.join(parts)
  if isinstance(lim, dict):
    parts = [f'{k}: {v}' for k, v in lim.items() if str(v).strip()]
    return '; '.join(parts)
  text = str(lim).strip()
  if text.startswith('[') and text.endswith(']'):
    try:
      val = ast.literal_eval(text)
      if isinstance(val, (list, tuple)):
        return '; '.join(str(p).strip() for p in val if str(p).strip())
    except Exception:
      pass
  return text


def format_prereq(p, resolve_slug):
  """Resolve lesson-slug prerequisites via resolve_slug(slug) -> markdown link or None."""
  if p is None or p == '':
    return ''
  if not isinstance(p, str):
    return str(p)
  slug = p.strip()
  if re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug):
    linked = resolve_slug(slug)
    if linked:
      return linked
  return p
