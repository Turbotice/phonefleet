# Phonefleet

Python application to remotely control the sensors of a smartphone fleet.


## Setup the Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows - PowerShell

You may need to install the *Python* executable from the Microsoft Store.

```powershell
python3.exe -m venv venv
venv\Scripts\Activate.ps1
pip.exe install -r requirements.txt
```

Note: setup in Windows is particularly slow - be patient.

You may need to set the execution policy to allow running scripts. You can do this by running the following command in PowerShell:

```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

If using the WSL, just run the Linux commands.

## Running the Application

### Linux / macOS

```bash
source venv/bin/activate
python app.py
```

### Windows - PowerShell

```powershell
venv\Scripts\Activate.ps1
python.exe app.py
```

### Options

Enable hot reload for development:
```bash
python app.py reload
```

Enable native window mode:
```bash
python app.py native
```

Running in native mode may require the `pywebview` package to be installed. You can install it with:

```bash
pip install pywebview
```

## Device Metadata

You can edit the device metadata in the `data/default_inventory.csv` file.

When a MAC address is found in the `data/default_inventory.csv` file, the application will display the metadata when hovering the MAC address in the *device* view.

## Acknowledgements

- [NiceGUI](https://nicegui.io/) - GUI framework used for the application.
- [Ag-Grid](https://www.ag-grid.com/) - Data grid used for displaying device information.
