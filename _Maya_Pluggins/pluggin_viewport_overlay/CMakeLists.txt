# Allow passing either the .app/Contents folder or the top‐level install path
if(NOT DEFINED MAYA_SDK)
  if(DEFINED ENV{MAYA_SDK})
    set(MAYA_SDK $ENV{MAYA_SDK})
  else()
    message(FATAL_ERROR "Please set -DMAYA_SDK or the MAYA_SDK env var to /Applications/Autodesk/maya2024/Maya.app/Contents")
  endif()
endif()

# On macOS the frameworks live here:
set(MAYA_FRAMEWORK_DIR "${MAYA_SDK}/Frameworks")

find_library(OpenMaya
  FRAMEWORK OpenMaya
  HINTS ${MAYA_FRAMEWORK_DIR}
)
find_library(OpenMayaUI
  FRAMEWORK OpenMayaUI
  HINTS ${MAYA_FRAMEWORK_DIR}
)
find_library(OpenMayaRender
  FRAMEWORK OpenMayaRender
  HINTS ${MAYA_FRAMEWORK_DIR}
)
