from App_MultiClone.Main import main
from App_MultiClone.Main import CloneInfo

CloneInfo_List = []
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM'
info = CloneInfo(url=url, branch=None, commit=None)
CloneInfo_List.append(info)
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader'
info = CloneInfo(url=url, branch=None, commit=None)
CloneInfo_List.append(info)

path = "C:\Current projects\Python\Test"

main(CloneInfo_List, path=path, force=True, depth=1)

