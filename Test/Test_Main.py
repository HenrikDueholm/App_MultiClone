from App_MultiClone.Main import main
from App_MultiClone.Main import clone_info

clone_info_list = []
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM'
info = clone_info(url=url, branch=None, commit=None)
clone_info_list.append(info)
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader'
info = clone_info(url=url, branch=None, commit=None)
clone_info_list.append(info)

path = "C:\Current projects\Python\Test"

main(clone_info_list, path=path, force=True, depth=1)

