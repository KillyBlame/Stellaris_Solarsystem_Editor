Stellaris Solar System Editor

A user-friendly, "no-code" web editor for creating and editing solar systems for the game Stellaris. This tool simplifies the modding process for system initializers and localization files by providing an intuitive graphical user interface, reducing the need for manual script editing.

Table of Contents


About the Project
Features
Usage

Use Online
Import Files
Export Files
Mod Setup in Stellaris



Local Development
Design Principles
Future Development Ideas
Contributing
License


About the Project

The Stellaris Solar System Editor was developed to fill a gap in the Stellaris modding community: the need for an accessible tool to create and edit solar systems without programming knowledge. Existing solutions are either outdated, require manual script editing, or do not offer comprehensive editing functionality for existing systems. This project provides a visual interface that abstracts the complexity of Clausewitz script syntax, making the modding process accessible to all players.

The editor is a single-file HTML/JavaScript application with no external dependencies — no frameworks, no CDN libraries, no build step. Open it in a browser and start editing.

Features

System Management


Multiple systems per project: Create and manage several system initializers in one session; all systems are exported into a single initializer file.
System properties: Identifier, display name, star class, usage type (Custom Empire / Empire Init / Fallen Empire Init / Misc System Init / Origin / Neighbor-only), mandatory-neighbor flag, and optional home-system resource generation.
Neighbor system linking: Define neighbor_system blocks with distance, hyperlane distance, hyperlane jumps, orientation angles, and spawn chance — including automatic re-linking of neighbor references when importing files that contain multiple systems.


Celestial Bodies


Stars, planets, and moons with full property editing: names, classes, sizes, orbit distances, and orbit angles (fixed values, ranges, or presets with smart-angle calculation).
Multi-star systems: A star configuration wizard sets up binary and trinary systems with vanilla-correct structure — P-type (circumbinary) planets placed after the star chain, S-type planets nested inside a star's planet = {} block.
Asteroid belts: Add and edit asteroid belts (radius and type) directly via a dedicated modal.
Planet flags: Starting planet, home planet, guaranteed habitable, terraforming candidate, planet ring, and change_orbit pointer resets.
Auto-naming: Bodies can use Stellaris' automatic name generation instead of fixed names.


Deposits & Modifiers


Built-in databases of vanilla deposit and planet modifier IDs, sourced from the actual game files — including yield annotations for deposits with unconditional produces blocks.
Filterable selection lists for deposits and modifiers (works across browsers, including Safari), plus free-text input for custom IDs.
Legacy modifier format toggle for compatibility with older modifier = syntax versus init_effect-based add_modifier.


Visualization


Canvas-based system view with zoom (mouse wheel) and pan, orbit rendering, asteroid belts, moons grouped around their planets, and labels at higher zoom levels.


Import


Robust .txt import of existing system initializer files, including files containing multiple systems. The parser uses brace matching (not regex), so nested structures are handled correctly.
Imported bodies, deposits, modifiers, belts, and neighbor definitions are loaded into the editor for further editing.


Export


.txt system initializer download (all systems in one file), plus in-browser preview and copy-to-clipboard.
.yml localization download (initializers_names_l_english.yml) with correct UTF-8 with BOM encoding; localization export can optionally be skipped.
Complete mod folder generation: One click creates the full mod structure — descriptor.mod, common/solar_system_initializers/, and localisation/english/ — written directly to disk via the File System Access API (Chrome/Edge), with a pure-JavaScript ZIP download (own CRC32 implementation, no libraries) as fallback for all other browsers.


Usage

Use Online

The editor is a pure HTML/CSS/JavaScript application and runs directly in any modern web browser. Just open the HTML file — no installation, no server required. (For full mod-folder generation to disk, a Chromium-based browser is needed; other browsers receive a ZIP file instead.)

Import Files


In the "Import / Export" section, select an existing .txt system initializer file from your computer.
The editor parses the contents — including multi-system files — and populates the system list and celestial body editors.
Names found in name = "..." lines are used as display names and exported to the localization file; localization .yml files themselves are not imported.


Export Files

You have three options:


Download as .txt — the generated system initializer file (plus the matching .yml localization file, unless skipped).
Copy / Preview — inspect the generated script in the browser or copy it to the clipboard.
Generate Mod Folder — creates the complete, ready-to-use mod structure including descriptor.mod, either written directly into your Stellaris mod directory or as a ZIP download.


Mod Setup in Stellaris

If you use Generate Mod Folder, the structure is created for you — just point it at (or unzip it into) your Stellaris mod directory (typically Documents\Paradox Interactive\Stellaris\mod\) and activate the mod in the launcher.

For manual setup:


Copy the .txt file into mod_name/common/solar_system_initializers/.
Copy the .yml file into mod_name/localisation/english/. The editor ensures the required UTF-8 with BOM encoding.
Activate your mod in the Stellaris Launcher before starting the game.


Local Development

Prerequisites


A web browser (Chrome, Firefox, Edge, Safari, etc.)
A text editor or IDE (e.g., VS Code)
Optional: Node.js for syntax validation (node --check on the extracted JavaScript)


Setup

git clone https://github.com/YourUsername/stellaris-solar-editor.git
cd stellaris-solar-editor

Open the HTML file directly in your web browser. Alternatively, use a simple local web server (e.g., python -m http.server).

Design Principles


Single-file architecture: The entire editor lives in one HTML file. No external libraries, no CDN dependencies, no build tooling.
Vanilla correctness: All exported structures follow vanilla Stellaris conventions — nested bodies always use moon = {} regardless of class, cumulative orbit_distance chains in list order, change_orbit as pointer reset, stars exported as planet = {} blocks with a star class.
No invented IDs: Every deposit, modifier, and class ID in the built-in databases is traceable to actual vanilla game files or the Stellaris wiki.
Brace-matching parsing: Nested Clausewitz structures are parsed with a brace-matching parser rather than regular expressions.


Future Development Ideas


Drag-and-drop functionality in the visualization to intuitively adjust orbit distances and angles.
Visual indicators for habitable zones and orbit collisions.
UI support for more complex init_effect blocks (anomalies, primitive civilizations, megastructures).
Real-time validation of user inputs against game rules (CWTools-style checks).
Import of additional script constructs (flags, variables, complex effects).
Custom planet classes / visual entities.
Performance optimizations for very complex systems.


Contributing

Contributions are highly welcome! If you find bugs, suggest features, or want to contribute code, please open an issue or submit a pull request.

License

This project is licensed under the MIT License.
