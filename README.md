# Stabilization Tool

Welcome to the **Stabilization Tool**, an advanced application designed to stabilise videos and generate detailed reports on the parameters used in the stabilisation process. This tool don't allows you to improve video quality, but it reduce unwanted shifts. Also provides the ability to document the parameters used for complete post-process analysis.

## Project Description

The application offers two main functionalities:

1. **Video Stabilization**: Uses advanced algorithms to correct camera movements, making videos more stable and professional. Users can choose between different types of stabilisation, such as local, global and perspective, depending on their specific needs.

2. **Report Generation**: After stabilisation, the application can generate a report in HTML format detailing the parameters used, such as stabilisation type, maximum displacement values, coordinates and dimensions of the region of interest (ROI), and other technical parameters.

This project was developed by **Giuseppe Tomarchio** as part of an academic activity for the **University of Catania**.

## System Requirements

- Python 3.11.1
- Tkinter (included in the standard Python distribution)
- OpenCV (for the underlying logic of video stabilization algorithms)
- Numpy (core library for numerical computing in Python)
- Pillow (image processing library that extends the capabilities of the Python Imaging Library (PIL))
- cpuinfo (to obtain CPU information)

## Installation

To start using the project, follow these steps:

1. **Clone the repository or download the files:**

    ```bash
    git clone https://github.com/tuo-nome-utente/stabilization-tool.git
    cd stabilisation-tool
    ```

2. **Create a virtual environment:** It is advisable to use a virtual environment to manage project dependencies. You can create a virtual environment as follows:

    ```bash
    python -m venv venv
    ```

3. **Activate the virtual environment:**

    ```bash
    # windows
    venv\Scripts\activate

    # macOS and Linux
    source venv/bin/activate
    ```

4. **Install the requirements**
Once the virtual environment is activated, install the necessary dependencies using pip:

    ```bash
    pip install -r requirements.txt
    ```

## Execution
After installing all dependencies, you can run the application:

```bash
python main.py
```

Or if you want to use the command-line version:

```bash
python main-nogui.py
```

## Licence
This project is distributed under the GPLv3 licence. You may modify and redistribute it under the same terms. Please consult the LICENSE file for further details.
