# apirotater-publish.ps1
# Script for building and publishing the APIRotater package

$ErrorActionPreference = "Stop"

# Function to display colored messages on screen
function Write-ColorText {
    param (
        [string]$Text,
        [string]$Color = "White"
    )
    Write-Host $Text -ForegroundColor $Color
}

# Check version files
$initFile = "apirotater/__init__.py"
$setupFile = "setup.py"

if (-not (Test-Path $initFile) -or -not (Test-Path $setupFile)) {
    Write-ColorText "Error: Files not found. Make sure you are in the correct directory." "Red"
    exit 1
}

# Get current version from files
$currentVersion = (Select-String -Path $initFile -Pattern '__version__ = "(.*)"').Matches.Groups[1].Value

# Ask for new version
Write-ColorText "Current version: $currentVersion" "Cyan"
$newVersion = Read-Host "Enter the version to release (leave blank to use current version $currentVersion)"

# If no input, use current version
if ([string]::IsNullOrWhiteSpace($newVersion)) {
    $newVersion = $currentVersion
    Write-ColorText "Using current version: $newVersion" "Yellow"
} else {
    # Validate version format (simple check)
    if ($newVersion -notmatch '^\d+\.\d+\.\d+$') {
        Write-ColorText "Warning: Version format should typically be X.Y.Z (e.g., 0.4.2)" "Yellow"
        $confirm = Read-Host "Continue with version $newVersion anyway? (Y/N)"
        if ($confirm -ne "Y" -and $confirm -ne "y") {
            exit 1
        }
    }
    
    # Update version in files
    Write-ColorText "Updating version to $newVersion in files..." "Cyan"
    
    # Update __init__.py
    (Get-Content $initFile) -replace '__version__ = ".*"', "__version__ = `"$newVersion`"" | Set-Content $initFile
    
    # Update setup.py
    (Get-Content $setupFile) -replace 'version=".*"', "version=`"$newVersion`"" | Set-Content $setupFile
    
    Write-ColorText "Version updated to $newVersion" "Green"
}

# Check if versions match now
$version = (Select-String -Path $initFile -Pattern '__version__ = "(.*)"').Matches.Groups[1].Value
$setupVersion = (Select-String -Path $setupFile -Pattern 'version="(.*)"').Matches.Groups[1].Value

if ($version -ne $setupVersion) {
    Write-ColorText "Error: Version information still does not match after update!" "Red"
    Write-ColorText "Version in __init__.py: $version" "Yellow"
    Write-ColorText "Version in setup.py: $setupVersion" "Yellow"
    exit 1
}

# Clean previous builds
Write-ColorText "Cleaning previous builds..." "Cyan"
if (Test-Path "dist") {
    Remove-Item -Path "dist" -Recurse -Force
}
if (Test-Path "build") {
    Remove-Item -Path "build" -Recurse -Force
}
if (Test-Path "*.egg-info") {
    Remove-Item -Path "*.egg-info" -Recurse -Force
}

# Build
Write-ColorText "Building package..." "Cyan"
python setup.py sdist bdist_wheel
if ($LASTEXITCODE -ne 0) {
    Write-ColorText "Build error!" "Red"
    exit 1
}

# Check
Write-ColorText "Checking package..." "Cyan"
twine check dist/*
if ($LASTEXITCODE -ne 0) {
    Write-ColorText "There are issues with the package! Please check." "Red"
    $answer = Read-Host "Do you want to continue anyway? (Y/N)"
    if ($answer -ne "Y" -and $answer -ne "y") {
        exit 1
    }
}

# Upload
Write-ColorText "Uploading APIRotater version $newVersion to PyPI..." "Green"
Write-ColorText "This operation will ask for your PyPI credentials." "Yellow"

$answer = Read-Host "Do you want to upload to PyPI? (Y/N)"
if ($answer -eq "Y" -or $answer -eq "y") {
    twine upload dist/*
    if ($LASTEXITCODE -eq 0) {
        Write-ColorText "Upload successful! APIRotater $newVersion has been published." "Green"
        Write-ColorText "You can install it with: pip install -U apirotater" "Cyan"
    } else {
        Write-ColorText "An error occurred during upload. Please check the error messages." "Red"
    }
} else {
    Write-ColorText "Upload cancelled." "Yellow"
}

Write-ColorText "Process completed." "Green"