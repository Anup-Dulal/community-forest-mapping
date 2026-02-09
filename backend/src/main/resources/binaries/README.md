# Native Unrar Binaries

This directory contains platform-specific unrar binaries required for RAR5 archive extraction.

## Required Binaries

You need to download and place the following binaries in their respective directories:

### 1. Windows x64
- **File**: `windows-x64/unrar.exe`
- **Source**: https://www.rarlab.com/rar/unrarw64.exe
- **Instructions**:
  1. Download unrarw64.exe from RARLAB
  2. Extract the unrar.exe binary
  3. Place it in `binaries/windows-x64/unrar.exe`

### 2. macOS Intel (x86_64)
- **File**: `macos-x64/unrar`
- **Source**: https://www.rarlab.com/rar/rarosx-6.2.4.tar.gz
- **Instructions**:
  1. Download rarosx tar.gz from RARLAB
  2. Extract the unrar binary
  3. Place it in `binaries/macos-x64/unrar`
  4. Make it executable: `chmod +x binaries/macos-x64/unrar`

### 3. macOS Apple Silicon (ARM64/aarch64)
- **File**: `macos-aarch64/unrar`
- **Source**: https://www.rarlab.com/rar/rarmacos-arm-6.2.4.tar.gz
- **Instructions**:
  1. Download rarmacos-arm tar.gz from RARLAB
  2. Extract the unrar binary
  3. Place it in `binaries/macos-aarch64/unrar`
  4. Make it executable: `chmod +x binaries/macos-aarch64/unrar`

## Alternative: Install via Package Manager

### macOS (Homebrew)
```bash
brew install unrar
# Then copy the binary:
cp $(which unrar) src/main/resources/binaries/macos-aarch64/unrar
```

### Windows (Chocolatey)
```powershell
choco install unrar
# Then copy unrar.exe to binaries/windows-x64/
```

## Verification

After placing the binaries, verify they work:

```bash
# macOS
./binaries/macos-aarch64/unrar

# Windows
.\binaries\windows-x64\unrar.exe
```

You should see the unrar help/version information.

## License

The unrar binaries are distributed by RARLAB and are subject to their license terms.
See: https://www.rarlab.com/license.htm

## Notes

- These binaries are NOT included in the repository due to licensing and size considerations
- The application will gracefully degrade if binaries are not available (RAR5 support disabled, ZIP and RAR4 continue working)
- Binaries are extracted to a temporary location at runtime and cleaned up on shutdown
