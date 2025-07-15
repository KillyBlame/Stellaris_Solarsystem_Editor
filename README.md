Stellaris Solar System Editor

A user-friendly, "no-code" web editor for creating and editing solar systems for the game Stellaris. This tool aims to simplify the modding process for system initializers and localization files by providing an intuitive graphical user interface and reducing the need for manual script editing.
Table of Contents

    Stellaris Solar System Editor

        Table of Contents

        About the Project

        Features

        Usage

            Use Online

            Import Files

            Export Files

            Mod Setup in Stellaris

        Local Development

            Prerequisites

            Setup

        Future Development Ideas

        Contributing

        License

About the Project

The Stellaris Solar System Editor was developed to fill a gap in the Stellaris modding community: the need for an accessible tool to create and edit solar systems without programming knowledge. Existing solutions are either outdated, require manual script editing, or do not offer comprehensive editing functionality for existing systems. This project provides a visual interface that abstracts the complexity of Paradox script syntax, making the modding process accessible to all players.
Features

    Visual System Creation: Add and intuitively position stars, planets, and moons.

    Property Editing: Edit system, planet, and moon properties such as names, classes, sizes, orbit distances, and angles using user-friendly forms.

    Simple Visualization: A basic graphical representation helps you understand your system's layout.

    File Import: Upload existing Stellaris .txt system initializer and .yml localization files to edit them in the editor.

    File Export: Download the generated .txt system initializer and .yml localization files directly, ready for your Stellaris mod folder.

    Automatic Localization: The editor generates the necessary localization entries for system, planet, and moon names.

    Correct File Encoding: Ensures that exported .yml files have the required UTF-8 with BOM encoding.

Usage
Use Online

The editor is a pure HTML/CSS/JavaScript application and can be used directly in any modern web browser. You just need to open the index.html file.
Import Files

    In the "Import / Export" section, click "Select File" under "Stellaris .txt Code (Import)" to upload an existing .txt system initializer file from your computer.

    Repeat the process for "Stellaris .yml Code (Import)" to upload the associated localization file.

    The editor parses the contents and updates the user interface with the system details and celestial bodies.

Export Files

    After editing or creating your system, click "Download as .txt" to download the generated system initializer file.

    Click "Download as .yml" to download the associated localization file.

Mod Setup in Stellaris

To use your custom solar system in Stellaris, follow these steps:

    Create Mod Folder: If you don't have a mod folder yet, create one via the Stellaris Launcher (in the "Mods" tab under "Mod Tools").

    Place Files:

        Copy the downloaded .txt file (e.g., my_custom_system.txt) into the mod_name/common/solar_system_initializers/ folder within your Stellaris mod directory (typically under Documents\Paradox Interactive\Stellaris\mod\).

        Copy the downloaded .yml file (e.g., my_custom_system_l_german.yml) into the mod_name/localisation/ folder of your mod directory. Ensure that the .yml file is encoded with UTF-8 with BOM (the editor attempts to ensure this during download).

    Activate Mod: Activate your mod in the Stellaris Launcher before starting the game.

Local Development

If you wish to contribute to the development of the editor, you can clone the repository and run it locally.
Prerequisites

    A web browser (Chrome, Firefox, Edge, Safari, etc.)

    A text editor or IDE (e.g., VS Code)

Setup

    Clone Repository:

    git clone https://github.com/YourUsername/stellaris-solar-editor.git
    cd stellaris-solar-editor

    Open in Browser:
    Open the index.html file directly in your web browser. Alternatively, you can use a simple local web server (e.g., with Python: python -m http.server).

Future Development Ideas

This is an initial version of the editor. Here are some ideas for future improvements and features:

    Advanced Visual Editing:

        Drag-and-drop functionality in the visualization to intuitively adjust orbit distances and angles.

        Visual indicators for habitable zones and collisions.

        Support for binary and trinary systems with correct visual representation.

    Detailed Effects and Modifiers:

        User interface elements for defining more complex init_effect blocks (e.g., adding resources, modifiers, anomalies, primitive civilizations, megastructures).

        Management of tile_blockers and modifiers via an intuitive interface.

    Robust Validation:

        Real-time validation of user inputs to ensure generated scripts are syntactically correct and adhere to game rules.

        Integration with or replication of CWTools validation logic.

    Enhanced Import Capabilities:

        More robust parsing of complex .txt files containing more than just basic system and celestial details (e.g., flags, variables, complex effects).

    Mod Structure Management:

        Ability to create a new mod directly from within the application, including generating the .mod descriptor file.

        Optional integration with the Stellaris Launcher (if technically feasible and secure).

    Custom Planet Types/Entities:

        Ability to define/select custom planet classes or visual entities.

    Performance Optimizations:

        Improve visualization performance for very complex systems.

Contributing

Contributions are highly welcome! If you find bugs, suggest features, or want to contribute code, please open an issue or submit a pull request.
License

This project is licensed under the MIT License.
