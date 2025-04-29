# How to run the server once installed

## 1. Open the terminal/command prompt

On Windows, you can use Command Prompt or PowerShell. On macOS and Linux, you can use the Terminal application.

## 2. Navigate to the project directory

Use the `cd` command to change to the directory where you installed the project. For example:

```bash
cd path/to/EEG-task-data-server-main
```

This should be the directory with all the code within it.

## 3. Activate the virtual environment

Next, activate the virtual environment - all of the necessary dependencies are installed in the virtual environment. The command to activate the virtual environment depends on your operating system:

### On Windows

```bash
\venv\Scripts\activate
```

### On macOS and Linux

```bash
source venv/bin/activate
```

## 4. Run the server

Once the virtual environment is activated, you can run the server using the following command:

```bash
local-data-storage
```
