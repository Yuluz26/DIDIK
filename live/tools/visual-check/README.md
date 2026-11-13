# Visual check for the subject games

Headless Chrome, driven over the DevTools protocol (no dependencies), against the dev gallery
`/gaya/subjek?g=<game>&state=right|wrong|host`.

- `node shots.mjs <outdir> play,right,wrong,host <game...>`: a phone-size screenshot of each game in each
  state; reports pages wider than the phone, broken pictures and page errors. `WIDTH=360` for a small phone,
  `PORT=` for another dev server.
- `node playall.mjs <game...>`: plays each game by tapping its controls and sends the answer; reports any
  game that could not be answered and any page error.

Needs Chrome at `C:/Program Files/Google/Chrome/Application/chrome.exe` (edit `cdp.mjs` elsewhere) and the
web dev server running.
