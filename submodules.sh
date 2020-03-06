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

function load_app () {
app=$1

    repo_serial_http="https://gitee.com/brt2/tmv-serial.git"
    repo_mvtool_http="https://gitee.com/brt2/tmv-mvtool.git"
    repo_viewer_http="https://gitee.com/brt2/tmv-viewer.git"
    repo_ocrkit_http="https://gitee.com/brt2/tmv-ocrkit.git"
    repo_triage_http="https://gitee.com/brt2/tmv-triage.git"
    repo_heroje_http="https://gitee.com/brt2/tmv-herosys.git"

    if [ -d ./src/app/${app} ]; then
        echo "子目录已存在 --> ./src/app/${app}"
    else
        if [ $app == "serial" ]; then
            git clone $repo_serial_http ./src/app/${app}
        elif [ $app == "mvtool" ]; then
            git clone $repo_mvtool_http ./src/app/${app}
        elif [ $app == "ocrkit" ]; then
            git clone $repo_heroje_http ./src/app/${app}
            git clone $repo_viewer_http ./src/app/${app}
            git clone $repo_ocrkit_http ./src/app/${app}
        else
            git clone "https://gitee.com/brt2/tmv-${app}.git" ./src/app/${app}
        fi
    fi

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
    test -d $dir_venv || ${py} -m venv $dir_venv
    source ${dir_venv}/${ACTIVATE_RPATH}

    # 安装框架依赖
    pypi="${py} -m pip install -i https://mirrors.aliyun.com/pypi/simple"
    $pypi -U pip  # 更新pip模块
    $pypi -r requirements.txt
    $pypi -r requirements-dev.txt

    # 安装app依赖
    app_requirements="./src/app/${app}/requirements.txt"
    test -f $app_requirements && $pypi -r $app_requirements
}

if [ $action == "push" ]; then
    sub_module_push src/utils/ $m_utils dev
elif [ $action == "pull" ]; then
    sub_module_pull src/utils/ $m_utils dev
else
    # if [ $action == "viewer" ]; then
    load_app $action
fi
