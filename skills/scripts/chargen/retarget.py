"""Shared sampling and target-pose helpers for supported glTF animations."""

import bisect
import json
import math
import struct

from mathutils import Matrix, Quaternion, Vector

ToBlender = Matrix.Rotation(math.pi / 2, 4, "X")
FrameRate = 30


def quaternion(values):
  """Convert a glTF XYZW quaternion to Blender's WXYZ ordering."""
  x, y, z, w = values
  return Quaternion((w, x, y, z)).normalized()


def readGlb(path):
  """Read JSON and binary GLB chunks without importing source geometry."""
  data = path.read_bytes()
  size = struct.unpack_from("<I", data, 12)[0]
  document = json.loads(data[20:20 + size])
  start = 20 + size
  length, kind = struct.unpack_from("<II", data, start)
  assert kind == 0x004E4942
  return document, data[start + 8:start + 8 + length]


def accessor(document, binary, index):
  """Decode packed or strided floating-point animation keys."""
  entry = document["accessors"][index]
  assert entry["componentType"] == 5126
  width = {"SCALAR": 1, "VEC3": 3, "VEC4": 4, "MAT4": 16}[entry["type"]]
  view = document["bufferViews"][entry["bufferView"]]
  offset = view.get("byteOffset", 0) + entry.get("byteOffset", 0)
  stride = view.get("byteStride", width * 4)
  return [struct.unpack_from("<" + "f" * width, binary, offset + i * stride)
          for i in range(entry["count"])]


def targetTpose(rig):
  """Align the arm and leg axes to the shared humanoid reference."""
  result = {}
  for bone in rig.data.bones:
    rotation = bone.matrix_local.to_quaternion()
    direction = None
    if bone.name.endswith(("Arm", "ForeArm", "Hand")):
      direction = Vector((1 if bone.name.startswith("Left") else -1, 0, 0))
    elif bone.name.endswith(("UpLeg", "Leg")):
      direction = Vector((0, 0, -1))
    if direction is not None:
      restDirection = (bone.tail_local - bone.head_local).normalized()
      rotation = restDirection.rotation_difference(direction) @ rotation
      assert ((rotation @ Vector((0, 1, 0))) - direction).length < 1e-4
    result[bone.name] = rotation
  return result


def sample(track, time, path):
  """Sample linear vector or shortest-arc quaternion tracks at one time."""
  times, values, interpolation = track
  right = bisect.bisect_right(times, time)
  left = max(0, right - 1)
  right = min(right, len(times) - 1)
  first, second = values[left], values[right]
  blend = ((time - times[left]) / (times[right] - times[left])
           if right != left and interpolation != "STEP" else 0)
  if path == "rotation":
    return quaternion(first).slerp(quaternion(second), blend)
  return Vector(first).lerp(Vector(second), blend)
