#!/bin/bash

function sub_module_update () {
dir_module=$1
url_repo=$2
branch=$3

    # 添加remote
    # git remote add "m-${dir_module}" $url_repo

    if [ -d mvlib ]; then
        git subtree pull --prefix=$dir_module $url_repo $branch --squash
    else
        read -p "是否载入子模块 [y/N]" continue
        if [ ${continue}_ == "y_" ]; then
            git subtree add --prefix=$dir_module $url_repo $branch --squash
        fi
    fi
}

sub_module_update src/utils/ git@gitee.com:brt2/utils.git dev
sub_module_update src/mvlib/ git@gitee.com:brt2/mvlib.git dev
