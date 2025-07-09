# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Only include files that MUST be bundled with the EXE
data_files = [
    ('UL_PEF_logo.png', '.'),  # Only if used before USB is available
]

def find_opencv_binaries():
    try:
        import cv2
        cv2_path = os.path.dirname(cv2.__file__)
        return [(os.path.join(cv2_path, '*.dll'), 'opencv')]
    except ImportError:
        return []

# Add this to your Analysis in the .spec file
binaries = [
    # OpenCV
    (os.path.join(os.path.dirname(__import__('cv2').__file__), '*.dll'), 'cv2'),
    
    # VLC
    (r'C:\Program Files\VideoLAN\VLC\*.dll', 'vlc') if os.path.exists(r'C:\Program Files\VideoLAN\VLC') else None,
    
    # Tkinter
    (os.path.join(os.path.dirname(__import__('tkinter').__file__), '*.dll'), 'tk')
]

a = Analysis(
    ['Okolje_za_pripravo.py', 'usb_monitor.py'],
    pathex=[],
	binaries=[
		# Auto-detect OpenCV
		(os.path.join(os.path.dirname(__import__('cv2').__file__), '*.dll'), 'opencv'),
		
		# Optional VLC
		(r'C:\Program Files\VideoLAN\VLC\*.dll', 'vlc') if os.path.exists(r'C:\Program Files\VideoLAN\VLC') else None,
	],
    datas=data_files,
	hiddenimports=[
		# Existing essential imports
		'pkg_resources.py2_warn',
		'setuptools',
		'multiprocessing',
		'multiprocessing.spawn',
		
		# Memory-critical additions
		'numpy.core._methods',       # Prevents numpy memory leaks
		'numpy.lib.format',          # Required for array handling
		'cv2.cv2',                   # OpenCV binary compatibility
		'PIL._imagingtk',            # Tkinter image handling
		'PIL._imaging',              # Core image processing
		'vlc',                       # VideoLAN core bindings
		
		# Threading/process control
		'concurrent.futures',        # For thread pool cleanup
		'threading',                 # Explicit thread management
		
		# USB/IO operations
		'ctypes.wintypes',           # Windows USB detection
		'win32file',                  # Drive monitoring (if using pywin32)
		'win32api',
		
		'psutil',
		'psutil._psutil_windows',
		'sys',
		'gc',
		
		'tracemalloc',
		'vlc.plugins',  # VLC internal
		'tkinter._tkinter'  # Tk's C extension
		
		'PIL',
		'tkinter',
		'numpy',
		'numpy.core._methods',
		'numpy.lib.format',
		
		# Windows specific
		'ctypes',
		#'win32api' if sys.platform == 'win32' else None,
		#'win32file' if sys.platform == 'win32' else None,
		
	],
    hookspath=['hooks'],  # Create this folder for custom hooks
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Okolje_za_pripravo',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Keep True for debugging, set False later
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None
)