# Polyglot Combiner

<img width="1918" height="1012" alt="image" src="https://github.com/user-attachments/assets/d1e05b97-621c-4079-b84b-027c2c8c3fe2" />


[![Made with Python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A user-friendly desktop application for creating **polyglot files**—single files that are valid in two or more different formats. For example, create a runnable Python script that is also a valid ZIP archive, or a viewable JPG image that contains a hidden payload of files.

This tool provides a simple GUI to combine a primary "host" file with a set of secondary "payload" files, bundling them into a single, dual-use output file.

---

## Key Features

*   **Polyglot Creation**: Easily create common polyglot types, such as `SCRIPT+ZIP`, `PDF+ZIP`, or `IMAGE+ZIP`.
*   **Intuitive GUI**: A clean and simple interface built with Tkinter that guides you through the creation process.
*   **Built-in ZIP Utilities**:
    *   **Quick ZIP**: A handy tool to create standard ZIP archives from a list of files.
    *   **ZIP Inspector**: Open, view, extract from, and delete files within any ZIP-compatible archive (including your created polyglots!).
*   **File Previews**: Get instant previews for common file types like images (JPG, PNG, GIF), text files, and basic metadata for PDFs.
*   **Customizable Theming**: Personalize your experience with multiple built-in themes:
    *   Light
    *   Dark
    *   PythonPlus (a classic dark blue and yellow theme)

---

### What is a Polyglot File?

> A polyglot is a file that is a valid form of multiple different file types. This application primarily focuses on creating files that have a valid "host" format (like a script or an image) and also contain a valid ZIP archive structure appended to them.
>
> **Example: A `Script+ZIP` Polyglot**
> *   When you run the file (`python my_script.py`), it executes as a normal Python script.
> *   When you open the *same file* with an archive manager like 7-Zip or WinRAR, it opens as a ZIP file, revealing the payload files you embedded.

---

## Installation

This application is built with Python's standard Tkinter library, but requires a few optional packages for full functionality (like image and PDF previews).

### Prerequisites

*   Python 3.6+

### Dependencies

*   **Pillow** (for image previews): `pip install Pillow`
*   **PyPDF2** (for PDF previews): `pip install PyPDF2`

### Running the Application

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/polyglot-combiner.git
    cd polyglot-combiner
    ```

2.  **(Recommended) Create a `requirements.txt` file:**
    Create a file named `requirements.txt` with the following content:
    ```
    Pillow
    PyPDF2
    ```
    Then install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the script:**
    ```bash
    python your_script_name.py
    ```
    *(Replace `your_script_name.py` with the actual name of the Python file).*

---

## Usage

The application is designed to be straightforward.

1.  **Step 1: Choose Combination**
    *   Select the type of polyglot you want to create from the dropdown menu (e.g., "PDF + Images", "Python (.py) + Payload").

2.  **Step 2: Select Primary File**
    *   Click "Choose..." to select the main host file (e.g., the PDF or the Python script). A preview will be shown if available.

3.  **Step 3: Add Secondary Files**
    *   Click "Add..." for each file type you want to include in the payload. You can select multiple files at once. These files will be bundled into the hidden ZIP archive.

4.  **Step 4: Set Output and Create**
    *   Click "Save As..." to choose a name and location for your new polyglot file.
    *   Click **Create** to generate the file.
    *   Click **Experiment** to create the file and a `.zip` copy for easy inspection.

### Theming

You can change the application's appearance by navigating to **Settings -> Preferences...** and selecting your desired theme. The change is applied instantly.

### Configuration

The application saves your last-used combination, window size, and theme choice to a configuration file located at `~/.polyglot_combiner.json` in your user home directory.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
