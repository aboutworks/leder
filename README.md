Lehuye-Leder Toolkit

A powerful Blender add-on to streamline 3D modeling workflows, featuring material management, UV editing, origin adjustment, procedural generation, and point cloud processing tools.

![Blender Version](https://img.shields.io/badge/Blender-4.5%2B-brightgreen) ![OS Support](https://img.shields.io/badge/OS-Windows%2FmacOS%2FLinux-blue) ![Language](https://img.shields.io/badge/Language-English%2FChinese-orange)

📋 Table of Contents

- Core Features

- Installation

- Usage Guide

- Compatibility

- Known Limitations

- Changelog

- Feedback & Issues

✨ Core Features

All tools are organized in theLehuye-Leder category of Blender's 3D Viewport N-panel (press N to show/hide).

1. Material & UV Tools

- One-click removal of all materials from selected objects

- Precise UV assignment based on XY grid for texture mapping

- Quick access to Blender's built-in UV tools (Smart UV Project, Project from View)

2. Object Origin Tools

Flexible origin adjustment for accurate modeling and animation:

- Geometry Center: Align origin to the geometric center of the object

- Center of Mass: Align origin to the object's center of mass

- 3D Cursor Position: Snap origin to the current 3D cursor location

- Volume Center: Align origin to the volumetric center of the object

3. Batch Text/Name Tools

- Automated batch renaming of selected objects

- Customizable parameters: name body, number position (prefix/suffix), start number, and sorting order

4. Procedural Generation Tools

4.1 Maze Generation

- Generate configurable polygon mazes (walls only)

- Adjust cell edge count, length, wall thickness/height, and row/column count

4.2 Road Generation

- Support for 4 road types: Straight, Curve, Cross, T-Junction

- Two generation modes:

  - Linked Instance: Shared mesh data (low resource cost)

  - Independent Copy: Unique mesh data (for individual edits)

4.3 Stone Generation

- Procedurally place stones on surfaces (auto-create plane or use selected mesh)

- Customize stone count, base size, irregularity, scale range, and grayscale color

- Linked/independent copy modes for performance or flexibility

4.4 Basic Geometry Creation

- One-click creation of equilateral tetrahedron primitives

5. Point Cloud & Import Tools

- Dense point cloud processing: Generate grid faces from point cloud data

- DXF Import & 3D Conversion: Convert DXF files to 3D wall geometry with customizable floor height and wall thickness

📥 Installation

1. Download the latest release ZIP file from the Releases section.

2. Open Blender → Go to Edit → Preferences → Add-ons.

3. Click Install and select the downloaded ZIP file.

4. Find "Lehuye-Leder Toolkit" in the add-on list, check the box to enable it.

5. Access the tools via the 3D Viewport N-panel (press N key) → Lehuye-Leder category.

🔧 Usage Guide

General Workflow

1. Open the Lehuye-Leder panel in the 3D Viewport N-panel.

2. Select the tool category (e.g., Material & UV, Procedural Generation).

3. Adjust the parameters as needed (all parameters have tooltips for guidance).

4. Click the tool button to execute (most tools support Undo/Redo).

Example: Generate Stones on a Selected Object

1. Select a mesh object in the 3D Viewport.

2. Open the Procedural Generation → Stone Generator panel.

3. Set Distribution Mode to "Selected Object".

4. Adjust Stone Count, Irregularity, and other parameters.

5. Click Generate Stones on Faces → The stones will be placed randomly on the selected object's surfaces.

🖥️ Compatibility

- Blender Version: 4.5 or higher (tested on 4.5 LTS)

- Operating Systems: Windows 10/11, macOS 12+, Linux (Ubuntu 20.04+)

- Language Support: English (default), Simplified Chinese (auto-switch based on Blender's language setting)

⚠️ Known Limitations

- Stair generation tools are currently disabled (coming in v1.1.0).

- Model repair tools (OBJECT_OT_fix_model) are under development.

- Large-scale stone generation (5000+ instances) may have performance issues (optimization planned).

📝 Changelog

v1.0.0 (Initial Release)

- First official release with core toolset.

- Fixed KeyError for Principled BSDF node (compatible with multi-language Blender settings).

- Resolved class name spelling inconsistencies (e.g., MaterialPanel_uv).

- Improved UI panel organization and translation consistency.

💬 Feedback & Issues

We welcome your feedback and feature requests! If you encounter any bugs or problems, please report them via:

- GitHub Issues: https://github.com/your-username/lehuye-leder/issues (replace with your actual repo link)

- Email: your-email@example.com (replace with your contact email)

📄 License

This project is licensed under the MIT License - see theLICENSE file for details.
