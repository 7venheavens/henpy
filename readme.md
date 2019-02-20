Design document for henpy

henpy is split into two main portions
- A query system that acquires tag information for JAV given a specific code
- An SQLalchemy based system for managing and querying tag information

The query system and tag management system have been deliberately kept separate to allow for easier generalization of henpy to other systems
