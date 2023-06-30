from main import main
from main import clone_request

clone_request_list = []
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.HDH.Driver.DMM'
info = clone_request(url=url, branch=None, commit=None)
clone_request_list.append(info)
url = 'https://github.com/HenrikDueholm/LV32.2020..PPL.ClassLoader'
info = clone_request(url=url, branch=None, commit=None)
clone_request_list.append(info)

path = "C:\Current projects\Python\Test"

main(clone_request_list, path=path, force=False, depth=1)
