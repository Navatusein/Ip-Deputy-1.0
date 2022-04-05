import os
import shutil
import requests

from zipfile import ZipFile


def check_new_version(url: str):
    version_request = requests.get(url)

    if not os.path.exists('version.txt'):
        return True

    with open(file='version.txt', mode='r') as version_file:
        version_local = version_file.read()

        if version_local != version_request.text:
            return True

    return False


def download_latest_version(url: str):
    latest_version_request = requests.get(url, allow_redirects=True)
    open('files/latest_version.zip', 'wb').write(latest_version_request.content)


def copy(source: str, destination: str):
    """Copy a directory structure overwriting existing files"""
    for root, dirs, files in os.walk(source):
        if not os.path.isdir(root):
            os.makedirs(root)

        for file in files:
            path = root.replace(source, '').lstrip(os.sep)
            destination_path = os.path.join(destination, path)

            if not os.path.isdir(destination_path):
                os.makedirs(destination_path)

            shutil.copyfile(os.path.join(root, file), os.path.join(destination_path, file))


def update():
    with ZipFile('files/latest_version.zip') as file:
        file_name = file.filelist[0].filename
        file.extractall('files/')

    copy(f'files/{file_name}/', f'{os.getcwd()}')

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'files/latest_version.zip')
    os.remove(path)

    path = os.path.join(os.path.abspath(os.path.dirname(__file__)), f'files/{file_name}')
    shutil.rmtree(path)


def main():
    if not check_new_version("https://raw.githubusercontent.com/Navatusein/IP-Deputy/master/version.txt"):
        print('Is no new version')

    print('Start updating')
    download_latest_version("https://github.com/Navatusein/IP-Deputy/archive/refs/heads/master.zip")
    update()

    print('Do you want install requirements.txt [y/n] ?')
    answer = input()

    correct_answers = ['y', 'yes']

    if answer in correct_answers:
        os.system(f'pip install -r requirements.txt')

    print('Updating finished!')


if __name__ == '__main__':
    main()
