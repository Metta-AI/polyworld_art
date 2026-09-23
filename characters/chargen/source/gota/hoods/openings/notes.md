# Hood opening review

The Crossbowman has a pointed brown opening with broad cheek corners and a
lower cloth point. The Lich has an ivory V beneath a matching crown band.
The Warlock has a small central peak, stepped gold shoulders and angular
lower corners. All three openings sit lower over the forehead. Their rounded
rear shells and loose lower hems remain fitted to the shared head.

The comparison sheets contain actual exported GLB renders and original
concept crops. The Ranger is an unchanged control. Front, side, back, walk
and crouch captures use the runtime rig and materials. The review renderer
now uses a hidden window with an offscreen multisample framebuffer, so
capturing these images does not display a native window.

Validation completed:

- The runtime library audit passed for all ten Gota heroes, including finite
  geometry, canonical rig joints, normalized skin weights and asset budgets.
- Headgear counts are 1,060 triangles for Crossbowman, 1,330 for Lich and
  1,554 for Warlock including both horns.
- The chargen tests and Nim check for the review renderer passed.
- Hidden screenshots were checked for rendered image content.
- Source authoring files and individual hero review sheets were refreshed.

The independent hood judge passed the forehead coverage and opening shapes
after inspecting the concept comparison, full front/back renders and each
crouch capture. Eyes remain readable and the distinctive cuts survive the
pose changes. No further revision was requested within this scope.
