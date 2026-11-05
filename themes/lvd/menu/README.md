# Light vs Dark menu art

- `background.png`: actual Light vs Dark game render, seed 2026, four bundled base bots, 90 simulated seconds, spectator visibility, camera distance 90, 1672×941. Captured before HUD rendering with floating name/health bars disabled. No synthetic scene replacement.
- `logo.png`: existing `../lvd_logo.png`, aspect-preserved in a transparent 3:2 canvas to match the shared home-menu layout.
- `button-*.png`: adaptations of the existing GotA menu buttons. Original beveled silhouette and alpha retained; secondary buttons shifted toward amethyst and primary gold slightly softened to match LvD's logo.

The renderer and menu geometry are shared in `polyworld/src/polyworld/homes.nim`; these images remain game-specific.
