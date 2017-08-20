# update_name_python3

## 仕様

- python3.6.2 以上で動作保証
  - 使用ライブラリ: [Python Twitter Tools](https://github.com/sixohsix/twitter)
- 名前変更はデフォルトでは下記で行う  
  NEW\_NAME(@screen_name)
- config/config.iniに下記を記入する必要あり
  - consumer\_key
  - consumer\_secret
  - access\_token
  - access\_token\_secret

## 注意

- Twitter Stream APIを使用しているため、予定されているStream APIの廃止がされたら動かない
- MIT License
