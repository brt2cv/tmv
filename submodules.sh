#!/bin/bash
# Usage: submodule [push|pull]

test -z $1 && action="pull" || action=$1

m_utils="git@gitee.com:brt2/utils.git"
# git remote add "m-${dir_module}" $m_utils

function sub_module_pull () {
dir_module=$1
url_repo=$2
branch=$3

    if [ -d $dir_module ]; then
        git subtree pull --prefix=$dir_module $url_repo $branch --squash
    else
        read -p "是否载入子模块 [y/N]" continue
        if [ ${continue}_ == "y_" ]; then
            git subtree add --prefix=$dir_module $url_repo $branch --squash
        fi
    fi
}

function sub_module_push () {
dir_module=$1
url_repo=$2
branch=$3

    git subtree push --prefix=$dir_module $url_repo $branch
}

#####################################################################
function pip_init () {
    # 安装依赖
    if [ "$(uname -s)" == "Linux" ]; then
        py="python3"
        ACTIVATE_RPATH="bin/activate"
    else  # Windows
        py="python"
        ACTIVATE_RPATH="Scripts/activate"
    fi

    # 创建venv目录
    dir_venv="env"
    has_framework="true"
    if ! [ -d $dir_venv ]; then
        ${py} -m venv $dir_venv
        has_framework="false"
    fi

    # 激活venv环境
    source ${dir_venv}/${ACTIVATE_RPATH}

    # 安装框架依赖
    pypi="${py} -m pip install -i https://mirrors.aliyun.com/pypi/simple"
    if [[ $has_framework == "false" ]]; then
        $pypi -U pip  # 更新pip模块
        $pypi -r requirements.txt
        $pypi -r requirements-dev.txt
    fi
}

# git-clone下载源码
repo_serial_http="https://gitee.com/brt2/tmv-serial.git"

repo_mvlib_http="https://gitee.com/brt2/mvlib.git"
repo_mvtool_http="https://gitee.com/brt2/tmv-mvtool.git"
repo_triage_http="https://gitee.com/brt2/tmv-triage.git"

repo_heroje_hid_device_http="https://gitee.com/brt2/heroje-hid_device.git"
repo_viewer_http="https://gitee.com/brt2/tmv-viewer.git"

repo_tesseract_http="https://gitee.com/brt2/tesseract.git"
repo_vkb_http="https://gitee.com/brt2/tmv-vkb.git"
repo_ocrkit_http="https://gitee.com/brt2/tmv-ocrkit.git"

function clone_and_pip_install () {
http_git=$1
clone_to=$2

    # git clone http://***.git
    test -d $clone_to || git clone $http_git $clone_to

    # 安装app依赖
    app_requirements="${clone_to}/requirements.txt"
    test -f $app_requirements && $pypi -r $app_requirements

# 检查依赖项
# depend_on=$*
# echo $depend_on
#     for item in $depend_on
#         clone_and_pip_install $item
}

function load_app () {
app=$1

    pip_init

    if [ -d ./src/app/${app} ]; then
        echo "子目录已存在 --> ./src/app/${app}"
    else
        if [ $app == "serial" ]; then
            clone_and_pip_install $repo_serial_http ./src/app/${app}
        elif [ $app == "mvtool" ]; then
            clone_and_pip_install $repo_mvlib_http ./src/plugins/mvlib
            clone_and_pip_install $repo_mvtool_http ./src/app/${app}
        elif [ $app == "ocrkit" ]; then
            clone_and_pip_install $repo_heroje_hid_device_http ./src/plugins/heroje_hid_device
            clone_and_pip_install $repo_viewer_http ./src/app/viewer

            clone_and_pip_install $repo_tesseract_http ./src/plugins/tesseract
            clone_and_pip install $repo_vkb_http ./src/plugins/vkb
            clone_and_pip_install $repo_ocrkit_http ./src/app/${app}
        else
            # git clone "https://gitee.com/brt2/tmv-${app}.git" ./src/app/${app}
            echo "[Error] 未知的app名称，请检查"
            exit
        fi
    fi
}

if [ $action == "push" ]; then
    sub_module_push src/utils/ $m_utils dev
elif [ $action == "pull" ]; then
    sub_module_pull src/utils/ $m_utils dev
else
    load_app $action
fi
