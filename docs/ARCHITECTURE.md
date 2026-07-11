# Architecture de NosMate Studio

## Vue générale

```text
Interface utilisateur
        |
        v
Workflow Library
        |
        v
Workflow Engine
        |
        v
Workflow Context
        |
        +-------------------+
        |                   |
        v                   v
Automation Runtime      VisionService
        |                   |
        |                   +--> Screenshot Provider
        |                   +--> Template Repository
        |                   +--> Template Matcher
        |
        +--> Keyboard Executor
        +--> Mouse Executor
        +--> Wait Executor