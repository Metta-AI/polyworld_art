# How to model for Polyworld with Blender - practical guide for AI

Install Blender from https://www.blender.org/download/ if you don't have it already.

To start modeling you should have a reference image of the thing you are modeling. Generate one and have a human review it if you did not start with one.

Use the imagegen skill to create a 2×2 modeling reference sheet with front, right, back, and top views on a neutral background. Make sure the camera angles are set to make the upright views more useful for modeling with orthographic projection.

Use the imagegen skill to create hand-painted trim sheets. Generate a trim sheet, usually a 4x4 tileable grid of textures.

Start with a blender file using the blender API.

Lay out the modeling references in the 3d for the front, right, back, and top views. Layout any mirroring or symmetry in the 3d space for your object.

Polyworld models are very low-poly. Each quad does something: it uses texture from the trim sheet. Polyworld style is low-poly but with hand-painted detail textures. No need for specular, normal, or bump maps, just color and texture.

Use mirroring. Many of the things use 2-way (people, monsters, swords, tools, etc.), 4-way (buildings, etc.) symmetry, and even 6-way (towers, poles, etc.) symmetry.

Start out with simple extrusion and shape. Think about poly flow, stay away from just overlapping boxes. It's better to start with a box shape and extrude out to make it more complex.

Use a judge subagent. The job of the judge is to review the modeling from many directions and give you suggestions on how to improve the model. Iterate until the judge is satisfied.
