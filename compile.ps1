$mainname = 'motioninput_api'
$outputname = 'Release'
$outputpath = $outputname + '\' + $mainname + '.dist'
$virtual_env_name = 'venv_compile'
$librarysourcepath = $virtual_env_name + '\Lib\site-packages'


if(!(Test-Path $virtual_env_name)){
    python -m venv $virtual_env_name
    $cmd = "./$virtual_env_name/Scripts/pip3.exe install -r requirements.txt"
    Invoke-Expression $cmd
}

if(Test-Path $outputname){
    $decision = Read-Host "$outputname directory already exists. Do you want to overwrite it? [y/n]"
    if(!($decision -eq 'y')){
        exit
    }
    Remove-Item ($outputname + '/') -Recurse
}

$wdc = ""
$linktime = 'no'

$cmd = "./$virtual_env_name/Scripts/python.exe -m nuitka $wdc --lto=$linktime --windows-disable-console --assume-yes-for-downloads --standalone --nofollow-import-to='openvino' --plugin-enable=numpy --output-dir=$outputname '$mainname.py'"
Invoke-Expression $cmd

$mediapipe = $outputpath + '\mediapipe'
$mediapipepython = $mediapipe + '\python'
Remove-Item $mediapipe -Recurse
Copy-Item -Path "data" $outputpath -Recurse
Copy-Item -Path "$librarysourcepath\mediapipe" $outputpath -Recurse
Copy-Item -Path "_framework_bindings.pyd" $mediapipepython
Copy-Item -Path "$librarysourcepath\openvino" $outputpath -Recurse
Copy-Item -Path "$librarysourcepath\_sounddevice_data" $outputpath -Recurse
Copy-Item -Path "$librarysourcepath\vgamepad" $outputpath -Recurse
