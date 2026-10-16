# Design: PR log

World: a hand-kept logbook. Blue-black fountain-pen ink on a cool white page, a red margin rule, and red-pen margin notes for things the owner still has to do.
Scene: someone opens the link on a phone or laptop in daylight, reads top to bottom, maybe searches one repo.
Colour strategy: Restrained. Ink, page, one red (the pen), status words carry their own muted hue plus the word itself. Never colour alone.
Type: system stacks only. Charter/Iowan Old Style/Georgia for reading, system-ui for the small gutter text. Tabular numerals for dates and counts. No webfonts, no display face.
Layout: one column, 40rem. A gutter on the left holds the status word, the entry sits to its right. Entries are grouped by the day they last changed, newest first. The red margin rule runs down the gutter edge on wide screens and disappears on phones.
Components: filter links (underlined, aria-pressed), plain search field, ruled entry lists, red margin notes. No cards, no pills, no shadows, no gradients, no icons.
Motion: none, except nothing needs it.
Rules to keep: status is always a word. Contrast at least 4.5:1 in both modes. Every control reachable by keyboard with a visible focus ring. Nothing depends on JavaScript for reading except the data fetch, and a noscript line says so.
Tokens live in :root in style.css. Change colours there only.
