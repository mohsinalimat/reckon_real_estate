# Manual template contract

Reference: C:/Users/User/.codex/plugins/cache/openai-curated-remote/openai-templates/0.1.1/skills/artifact-template-system-design/assets/reference.docx

Evidence: template_render/reference.pdf and seven page PNGs; template_style.json; section audit output. Canonical renderer attempted but LibreOffice is absent. Microsoft Word background export works with desktop access and is the render authority for this task.

Page system: one portrait Letter section, 8.5 by 11 inches; margins left/right/top 0.7 inches and bottom 0.6201389 inches; different first page enabled. Preserve section XML unchanged.

Typography and components: clone exact pPr/rPr from reference Title paragraphs 8 and 9, body paragraph 22, Heading 1 paragraph 21, Heading 3 paragraph 35, and caption paragraph 33. Preserve source styles, fonts, blue heading colors, paragraph rhythm and title positioning. Cover metadata tables retain original grid and cell formatting. Body tables clone source table 5, with source row shading, header, padding and cell typography; repeat header rows. Preserve footer formatting, replacing its subject text only and adding an unobtrusive page field.

Slot map: word/document.xml body content before first Heading 1 is cover. Replace two title slots, metadata labels and values. Replace proposal-specific body content with manual chapters, cloning heading, prose, caption and table patterns. Chapters may repeat and start on new pages for user-reference navigation. Screenshot positions are caption paragraphs, to be replaced later with inline screenshots. Remove unused architecture drawing and sample footnote references from body; retain their unused package parts unchanged. All placeholders from the original template must be removed from visible content. Cover author/reviewer slots become audience and verification scope, without invented sign-offs.

Preserve-only: every package part except word/document.xml, footer text parts and docProps/core.xml. Preserve numbering, styles, theme, settings, relationships, media, footnotes, endnotes, headers and opaque parts byte-for-byte. The authoring script records SHA256 and part inventory in template_inventory.json and validates final output against it. Use a zip/XML patch to avoid rewriting preserve-only parts.

Content: source-verified module reference as of 5 September 2026. Procedures are not a live-site test. Native accounting entries are distinguished from operational records. UI labels derive from form JSON and JavaScript. No unsupported planned features presented as implemented.

Fidelity gates: unchanged reference hash and section geometry; all retained parts identical; every final page visually checked after Word export; no table splits, clipped text, accidental blank pages or leftover sample text. Expected content-driven differences include chapter count, manual headings, screenshot captions and cover wording.
