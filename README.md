# Review Player

### Under development ###

A professional Python-based review player framework for VFX, animation, and post-production workflows.

This project is designed as a modern review/playback foundation similar to:

- RV
- DJV
- ShotGrid Create
- Internal studio review tools

The player supports:

- Video playback
- Image sequence playback
- OpenEXR workflows
- OpenColorIO (OCIO)
- Frame-accurate stepping
- Timeline scrubbing
- OpenGL display rendering

---

# Features

        Playback

        - MP4 playback
        - MOV playback
        - AVI playback
        - PNG sequence playback
        - JPEG sequence playback
        - EXR sequence playback

        Viewer

        - OpenGL-based viewer
        - Dynamic fit-to-window display
        - Aspect ratio preservation
        - Timeline scrubbing
        - Frame stepping
        - Loop playback


        Color Management

        - OpenColorIO integration
        - ACES-ready architecture
        - Input color space selection
        - Display transform selection
        - View transform selection

        Timeline

        - Frame-based timeline
        - Current frame indicator
        - Major/minor frame ticks
        - Interactive scrubbing

---

# Project Structure

        review_player/
        │
        ├── main.py
        │
        ├── ui/
        │   ├── main_window.py
        │   ├── viewer_widget.py
        │   └── timeline_widget.py
        │
        ├── playback/
        │   ├── media_player.py
        │   ├── video_reader.py
        │   ├── sequence_reader.py
        │   └── frame_cache.py
        │
        ├── ocio/
        │   └── ocio_processor.py
        │
        └── utils/
            └── path_utils.py

---

# Architecture Overview

        The project separates playback into multiple independent systems.

        Media Reader
            ↓
        Frame Cache
            ↓
        OCIO Processing
            ↓
        Viewer Rendering
            ↓
        Timeline/UI


This modular structure allows future scalability.

---

# Dependencies, Required Libraries

| Library | Purpose |
|-----|---|
| PySide6 | UI framework |
| PyOpenGL | OpenGL rendering |
| NumPy | Image buffer processing |
| PyAV | Video decoding |
| OpenImageIO | Image sequence reading |
| OpenColorIO | Color management |

---

# Installation

### Create Virtual Environment

```bash
python -m venv venv
```


### Activate Environment

### Linux

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install PySide6
pip install numpy
pip install av
pip install OpenImageIO
pip install opencolorio
pip install PyOpenGL
```

---

# OpenColorIO Setup

The review player requires an OCIO configuration file.

Example:

```bash
export OCIO=/path/to/config.ocio
```

---

# Recommended OCIO Config

Recommended:

ACES 1.3 Config

Official repository:

https://github.com/AcademySoftwareFoundation/OpenColorIO-Config-ACES

---

# Running The Player

```bash
python main.py
```

---

# Supported Formats

## Video / Image

| Format | Supported |
|---|---|
| mp4 | YES |
| mov | YES |
| avi | YES |
| png | YES |
| jpg | YES |
| jpeg | YES |
| exr | YES |

---

# Playback Controls

| Control | Action |
|---|---|
| Open | Load media |
| Play | Start playback |
| Stop | Stop playback |
| << | Previous frame |
| >> | Next frame |

---

# Current Limitations

This project is currently an early playback framework.

Known limitations:

- OpenGL uses glDrawPixels()
- No GPU texture rendering yet
- No threaded decoding
- Video decoding loads all frames into memory
- EXR playback currently converts float images to uint8 preview
- No HDR display pipeline yet
- No audio synchronization
- No annotation system

---

# EXR Support

The player supports:

- Single-layer EXR
- Multi-layer EXR
- RGB layer extraction

The EXR reader automatically searches for valid RGB layers such as:

```text
RGB
beauty.R beauty.G beauty.B
rgba.R rgba.G rgba.B
Ci.R Ci.G Ci.B
```

---

# OCIO Workflow

Typical workflow:

```text
EXR (ACEScg)
    ↓
OCIO Display Transform
    ↓
sRGB Monitor
```

---

# Recommended Professional Workflow

| Input | Display |
|---|---|
| ACEScg | Rec709 |
| Linear | sRGB |
| UtilityRaw | Raw |

---

# Future Roadmap

## Playback

- Threaded decoding
- Async frame prefetch
- Smart frame cache
- GPU upload pipeline

---

## Viewer

- OpenGL texture rendering
- GPU OCIO transforms
- Zoom
- Pan
- Fit modes
- Pixel inspection

---

## Timeline

- Timeline zoom
- Cached frame visualization
- Frame markers
- Notes/comments
- In/out ranges

---

## EXR Features

- Layer browser
- AOV switching
- Deep EXR support
- Metadata viewer
- Multi-part EXR support

---

## Review System

- Task integration
- Version integration
- Notes/comments
- Draw annotations
- Review sessions

---

# Professional Rendering Direction

Current prototype:

```text
CPU Image
    ↓
glDrawPixels()
```

Future architecture:

```text
CPU/GPU Decode
    ↓
OpenGL Texture
    ↓
OCIO GPU Shader
    ↓
Viewer
```

---

# Suggested Future Integrations

- Autodesk Flow Production Tracking (ShotGrid)
- USD pipelines
- FFmpeg render export
- Nuke review pipeline
- Editorial workflow
- RV-compatible controls

---

# Recommended Development Order

## Phase 1

- Stable playback
- EXR support
- Timeline
- OCIO

---

## Phase 2

- OpenGL textures
- GPU OCIO
- Cache system
- Threaded playback

---

## Phase 3

- Review annotations
- Notes/comments
- Version browser
- Task integration

---

# Author

Subin Gopi

---

# License

Internal Development / Prototype