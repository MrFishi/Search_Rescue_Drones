[PX4 Autopilot User Guide](https://docs.px4.io/main/en/) 
Top-level PX4 documentation home covering the full platform: hardware setup, configuration, flight modes, safety, and development for all supported vehicle types.

[PX4 Simulation Overview](https://docs.px4.io/main/en/simulation/)
Covers SITL/HITL simulation concepts, supported simulators (Gazebo, SIH), MAVLink API, UDP port configuration, and how to launch PX4 SITL with make targets.

[PX4 Hardware In The Loop (HITL) Simulation](https://docs.px4.io/main/en/simulation/hitl)
How to run PX4 firmware on real Pixhawk hardware while simulating vehicle dynamics externally — useful for testing hardware-level behaviour without propellers attached.

[Mapbox](https://www.mapbox.com/) 
Location platform providing APIs and SDKs for maps, satellite imagery, terrain data, and geospatial tools — used here to source real-world terrain and satellite data for building accurate Gazebo simulation worlds.

[Gazebo Terrain Generator](https://github.com/saiaravind19/gazebo_terrain_generator) 
Python tool that generates real-world 3D Gazebo Harmonic worlds from satellite imagery and elevation (DEM) data via a web UI — used to create accurate bush/forest terrain for SAR simulation.