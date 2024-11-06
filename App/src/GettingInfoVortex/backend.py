from App.libs import json, p7z, os


def unzip_7z_file(path):
    with p7z.SevenZipFile(path, mode='r') as z:
        z.extract(targets=['collection.json'])

    get_json_data_from_collections()

    os.remove('collection.json')


def get_7z_file(path):
    sevenz_files = [f for f in os.listdir(path) if f.startswith("collection_") and f.endswith(".7z")]
    if sevenz_files:
        sevenz_files.sort(key=lambda x: int(x.split("_")[1].split(".")[0]))
        latest_sevenz = os.path.join(path, sevenz_files[-1])
        return latest_sevenz, sevenz_files[-1]
    else:
        return None


def get_json_data_from_collections(path=None, json_file='collection.json'):

    with open(json_file if path is None else path, 'r', encoding='utf-8') as json_arq:
        json_data = json.load(json_arq)

    collection_name = json_data['info']['name']
    data = list()
    for mod in json_data['mods']:
        modid = mod['source']['modId']
        source = mod['source']['type']
        mod_name = mod['name']
        version = mod['version']
        logicalfilename = mod['source']['logicalFilename'] if 'logicalFilename' in mod['source'] else ''
        data.append({
            'name': mod_name,
            'version': version,
            'source': source,
            'modId': modid,
            'logicalFilename': logicalfilename,
            'link': f'https://www.nexusmods.com/skyrimspecialedition/mods/{modid}'
        })

    write_json(data=data, json_name=f'vortex_collection_({collection_name}).json', mode='w')


def get_named_collections(path) -> list:
    data = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file == 'collection.json':
                # root = str(root).replace('--', '')
                path_to_dir = str(os.path.join(root, file))
                dir_name = str(os.path.basename(root))
                data.append({
                    "caminho_completo": path_to_dir,
                    "nome_pasta": dir_name,
                    "nome_arquivo": file
                })
                get_json_data_from_collections(path=path_to_dir, json_file=file)
    return data


def get_unnamed_collections(path) -> list:
    data = []
    for root, dirs, _ in os.walk(path):
        for dir in dirs:
            if dir.startswith('vortex_collection'):
                path_to_dir = str(os.path.join(root, dir, 'export'))
                path_to_dir, zipfile = get_7z_file(path_to_dir)
                unzip_7z_file(path_to_dir)
                data.append({
                    "caminho_completo": path_to_dir,
                    "nome_pasta": zipfile,
                    "nome_arquivo": 'collection.json'
                })

    return data


def get_mods_from_collections():
    path = 'E:\\Vortex_Mods'
    unamed_collections = get_unnamed_collections(path)
    named_collections = get_named_collections(path)
    collections = unamed_collections + named_collections
    write_json(data=collections, json_name='vortex_list_collections.json', mode='w')


def get_mods_from_backup_json():
    try:
        with open('E:\\mods_vortex_backup.json', 'r', encoding='utf-8') as json_file:
            json_data = json.load(json_file)
            data = list()
            for mod in json_data:
                mod_name = mod['name']
                modid = mod['modId']
                source = mod['source']
                vortexid = mod['vortexId']
                link = f'https://www.nexusmods.com/skyrimspecialedition/mods/{modid}'
                data.append({
                    'name': mod_name,
                    'modId': modid,
                    'source': source,
                    'vortexId': vortexid,
                    'link': link
                })
        write_json(data=data, json_name='vortex_mods_backup.json', mode='w')
    except FileNotFoundError:
        print('ERRO!!!')
        print('\t- O Arquivo "mods_vortex_backup.json" não existe!\n\t\tPor favor, crie outro arquivo de backup no vortex!')
    else:
        os.remove('E:\\mods_vortex_backup.json')


def write_json(data, json_name, mode):
    with open('E:\\' + json_name, mode=mode) as json_file:
        json.dump(data, json_file, indent=4)


if __name__ == '__main__':
    get_mods_from_collections()
    get_mods_from_backup_json()
