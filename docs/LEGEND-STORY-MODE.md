# DIDIK Legenda — top-down Story Mode

## User journey

Parents and teachers write a quiz once (minimum **10** questions), then choose **Legenda: Story Mode** from the existing `Main bersama` mode picker. The room/QR-code flow, solo participation and multiplayer already use DIDIK Live's real-time infrastructure. There are no additional questions, boss editors or environment settings for the parent to configure.

The five chapters are Tasik Chini, Batang Lupar, Hutan Larut, Rimba Bayangan, Gunung Ledang. Each world has five question-driven obstacles, grants five selectable elemental weapons, and ends with a five-heart legendary boss. All worlds reuse the parent quiz if fewer than 50 questions are supplied. In party play, children have their own progress and hearts, while the current world's boss HP is shared.

## Code

- `live/server/didik_live/game/modes/story.py`: authoritative game state, movement, questions, checkpoint recovery, boss hearts and elemental scoring.
- `live/web/src/lib/games/story/art.js`: an original, **top-down** 2D art renderer: hand-authored pixel shapes, regional terrain, lake, shrines, bridges, foliage, characters and bosses. This is **not Three.js or the generated concept image**. The illustration is rendered by the same code used in live gameplay.
- `StoryScene.svelte`: responsive canvas and camera presentation.
- `StoryPlayer.svelte`: mobile joystick, keyboard, parent-provided questions, six-heart meter, elemental weapon bar, visual combat feedback, five-chapter progress.
- `StoryHost.svelte`: party display.
- `live/web/src/lib/home/StorySpotlight.svelte`: displays the live renderer for all five worlds.

## Controls

- **Keyboard:** WASD / arrow keys; Space or Enter to engage when close enough.
- **Touch:** thumbstick, then tap the engage button when close to an obstacle/boss.
- **Weapons:** after answering the five obstacle questions, pick any of Api / Angin / Petir / Tanah / Air.
- **Health:** 6 hearts, wrong answer −1.5 hearts, correct answer +0.5 hearts (capped at 6), defeat restarts at the current-world checkpoint.
- **Boss:** five successful quiz-driven strikes. Incorrect answers trigger damage rather than a strike. Failed boss questions rotate through available questions so the encounter can still be won.
- **Party:** question checking and HP changes occur only on the FastAPI server, preventing the client from authoring correct answers or altering health.

## Tests / screenshots

`live/server/tests/test_story.py` covers constraints, solo progression, checkpoint retry, boss hits and shared party HP. GitHub Actions workflow `didik-live.yml` runs the Python suite, Svelte check/build and Chromium screenshot capture.

Screenshots in workflow artifact **didik-story-world-screenshots** are genuine browser captures of the `StoryScene` renderer on the homepage, not an imported mockup. Run `npm run dev --prefix live/web -- --host 127.0.0.1 --port 5173` and visit `/#legenda` to inspect the visuals. The server is required to actually answer questions or progress between worlds.

## Current scope and limitations

This branch is a development **vertical slice**, not a final production-grade Zelda-like game. The top-down stage and camera are integrated with the existing authoritative room/game system, while the map is still a guided corridor with regional scenery. Trees and decorative ruins are not yet collision obstacles, boss attacks are quiz-triggered rather than free-form real-time combat, and there are no dedicated animation sprite sheets, cinematics or custom audio tracks. Completing a fully explorable RPG matching a high-detail concept painting would require carefully authored tilemaps, directional sprites, richer encounter phases and art iteration, rather than substituting the reference concept image as a static background.

Keep the pull request as **draft** until actual user gameplay is reviewed on mobile and desktop.
