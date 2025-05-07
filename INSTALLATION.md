# Project Symmetry Installation Guide

## UI Installation

### Requirements
Before starting the installation, make sure you have the following tools installed:

- **OpenGL ES 2.0** (or higher)
- **Windows**: ConPTY support (Windows 10 version 1809 or higher)
- **Ubuntu**: Version 20.04 or later
- **Node.js**: Latest version (e.g., 23.11.0)
- **Python**: Version 3.8 - 3.11 (NLP library requirements prevent 3.12)
- **npm**: Version 10.8.2
- **Electron**: Version 26.2.4


### Installation Steps

I. **Clone the Repository**

Open your terminal and run the following command to clone the repository:

```
git clone https://github.com/grey-box/Project-Symmetry-AI
```


II. **Navigate to ui and Install Dependencies**

```
cd ui
npm install
```

III. **Setting up the Python Environment**

This guide will help you set up a Python virtual environment and install the required dependencies on different operating systems (Windows, Linux, macOS).

   1. Create a Virtual Environment
   If you haven't already created a virtual environment, you can do so by running the following command:
   
   ```
   cd ../fastapi
   python -m venv venv
   ```
   2. Activate the Virtual Environment
   
   | **Operating System** | **Command**                                                                          |
   |----------------------|--------------------------------------------------------------------------------------|
   | **Windows**          | `cd venv\Scripts\` <br> `.\Activate` |
   | **Linux/MacOS**      | `source venv/bin/activate`                                                           |
   You should see (venv) on the left of your terminal now.
   3. Install Dependencies
      
   Once the virtual environment is activated, install the necessary dependencies from the requirements.txt file:
   
   ```
   pip install -r requirements.txt
   ```
   
   4. Install PyInstaller
      
   Project Symmetry requires a Python executable to run successfully. Install PyInstaller to create it.
   
   ```
   pip install pyinstaller
   ```

V. **Use Pyinstaller to Build an Executable**

```
cd app
pyinstaller -F main.py
```
This will create a Python executable in a new folder called dist. You may leave it there.

We no longer need to be inside the Python venv, you may deactivate it with:
```
deactivate
```
VI. **Navigate to the UI Folder and Run the App**

```
cd ../../ui
npm run start
```

### Packaging Symmetry
Project Symmetry is built on the Electron Framework, packaging it is simple.

I. **Navigate to the UI Folder**

From the root of the folder:
```
cd ui
```

II. **Package the Front-End**
```
npm run package
```

**For Windows/Linux**

- Within the UI folder a new folder "out" will be created. Inside, a folder named "project_symmetry-xxx-xxx" contains "project_symmetry.exe"

**For Mac**

- Within the UI folder a new folder "out" will be created. Inside will be a single project_symmetry-xxx-xxx.app file. Running this will work fine but, to complete the next step you'll have to right click the file and select "" to view the internal file structure.

III. **Insert the Python Executable**

By this point, you should have a Python executable. If not, see section 3.5 above. Please note that PyInstaller cannot
cross-compile. Meaning, a binary for a platform (Windows/Mac/Linux) must be generated on that platform.

1. Copy the "main.exe" executable in root/fastapi/app/dist. 

2. Paste it into root/ui/out/project_symmetry-xxx-xxx/resources (or project_symmetry-xxx-xxx.app/resources)

If you've followed all of the above steps, running project_symmetry.exe will start up Project Symmetry.
### Generating docs

1. Delete all the rst files in the docs folder, other than modules.rst and index.rst

2. Generate new rst files

```bash
cd api
sphinx-apidoc -o docs .
```

3. Use make.bat file to generate html

```bash
cd docs
./make.bat html
