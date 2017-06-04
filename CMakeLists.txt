atlas_subdir(pixel-NN)

find_package(ROOT COMPONENTS MathCore RIO Core Tree Hist Matrix)

atlas_depends_on_subdirs(
  PUBLIC
  Control/AthContainers
  PhysicsAnalysis/D3PDTools/EventLoop
  xAOD/xAODTracking
  xAOD/xAODEventInfo
  PRIVATE
  Control/xAODRootAccess
  )

atlas_add_root_dictionary(pixel-NN-Lib pixel-NN-Lib-CINT-Dict
  ROOT_HEADERS pixel-NN/*.h Root/*.h
  )
  

atlas_add_library(pixel-NN-Lib
	pixel-NN/*.h Root/*.cxx ${pixel-NN-Lib-CINT-Dict}

	PUBLIC_HEADERS
	pixel-NN

	INCLUDE_DIRS
	${ROOT_INCLUDE_DIRS}

	LINK_LIBRARIES
	${ROOT_LIBRARIES}
	AthContainers
	xAODTracking
	xAODEventInfo
	xAODRootAccess
	EventLoop
)
		
