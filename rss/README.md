## Rules:

- Each request starts a new pipeline
- I/O should be kept separate from core logic, and ideally at the beginning and end of each pipeline
- Core logic should be composed of pure functions
- The domain should be modeled via detailed type definitions for all inputs and outputs
- Prefer type aliases that use ubiquitous domain language over primitive types

Sources:
- (add Scott Wlaschin talks)
