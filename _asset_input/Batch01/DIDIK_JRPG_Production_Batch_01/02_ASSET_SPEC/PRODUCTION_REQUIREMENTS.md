# Production asset specifications — DIDIK Story Mode

**Do not let the generated reference boards overwrite gameplay data.** They frequently show incorrect element typing (e.g. Shadow instead of Tanah), inconsistent boss anatomy, false class labels, and erroneous text. The authoritative names are in the shared master spec: Api, Angin, Petir, Tanah and Air. The image packs are visual reference inputs.

## Standard export profile

| Kind | Preferred size | Alpha | Delivery |
|---|---|---|---|
| Chapter / battle background | 1920×1080 master, responsive 16:9 crop | No | WebP/PNG, clean of characters, HUD and text |
| Boss isolated art/rig | 2048 px longest axis, optional 4K source | Yes | Clean transparent PNG layers / packed sprites + animation metadata |
| Character portrait | 1024×1024 | Yes preferred | PNG/WebP portrait no baked label |
| Hero full-body sprites | 256–512 px height on consistent shared scale | Yes | Directional frames + contact sheet, 2D anchor |
| 5 elemental buttons | 256×256 each | Yes | Separate SVG/PNG or icon atlas + state metadata |
| HUD panels and hearts | Vector if possible; 2x @ target DPI | Yes | SVG/PNG nine-slice; full/half/empty states |
| Particles and attack FX | 256–1024 px | Yes | Atlas or frame sequence, offsets documented |
| Boss cinematic keyframe | 1920×1080 | No | Composite reference, not active sprite |
| Trailer/storyboard still | 1920×1080 | No | PNG/JPG, shot number and intended motion |
| Mobile promo | 1080×1920 | No | Reference/promo only |

Note: exact sizes can adapt to measured gameplay canvas; consistency, masking, transparent edges and anchor points matter more than arbitrarily huge files. Keep master image files and export optimized runtime derivatives.

## Must label every asset
`id / world / subject / usage / available source file / dimensions / alpha / status(reference_only|prototype|production_ready) / source/licence / action_needed / animation_state`.

## FIRST BATCH prioritization
1. Design system / story mode key art and consistent **character silhouettes**.
2. World 1 **battle background with NO boss or text** and World 1 **Naga Chini isolated separate 2D subject**.
3. Hang Tuah and Mahsuri selection portraits and 2D battle rig, then Hang Jebat.
4. Five elemental icons, full/half/empty hearts and five-boss-bar HUD.
5. Enemy, question overlay, correct/wrong feedback, automatic story pan, boss reveal/defeat.

The images included here are reference boards. They are not in those production formats, and not all have alpha/transparency or clean separable character layers. This is a **deliberate gap that Codex/Claude Code must respect**.
