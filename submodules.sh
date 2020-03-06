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


if [ $action == "push" ]; then
    sub_module_push src/utils/ $m_utils dev
else
    sub_module_pull src/utils/ $m_utils dev
fi
