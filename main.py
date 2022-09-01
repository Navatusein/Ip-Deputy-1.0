import datetime
import json
import os
import shutil
import requests

from zipfile import ZipFile




def check_new_version(url: str):
    version_request = requests.get(url)

    if not os.path.exists('version'):
        return True, True, True

    with open(file='version', mode='r') as version_file:
        version_file_data = json.load(version_file)
        version_request_data = json.loads(version_request.text)

    code_update = version_file_data['CodeUpdate'] != version_request_data['CodeUpdate']
    requirements_update = version_file_data['RequirementsUpdate'] != version_request_data['RequirementsUpdate']
    database_update = version_file_data['DatabaseUpdate'] != version_request_data['DatabaseUpdate']

    return code_update, requirements_update, database_update


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
    code_update, requirements_update, database_update = check_new_version("https://raw.githubusercontent.com/"
                                                                          "Navatusein/IP-Deputy/master/version")

    if not code_update and not requirements_update and not database_update:
        os.system('python3')
        return

    if code_update:
        print('Update code')
        download_latest_version("https://github.com/Navatusein/IP-Deputy/archive/refs/heads/master.zip")
        update()

    if requirements_update:
        print('Update requirements')
        os.system(f'pip install -r requirements.txt')

    if database_update:
        os.system(f"alembic revision --autogenerate -m '{datetime.datetime.now().date()}'")
        os.system(f'alembic upgrade head')

        # alembic revision --autogenerate -m ''
        # alembic upgrade head

    print('Updating finished!')


if __name__ == '__main__':
    main()
