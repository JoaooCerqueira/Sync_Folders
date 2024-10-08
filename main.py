import time 
import os
import argparse
import shutil
import logging
import hashlib

# os: Para manipulação de arquivos e diretórios.
# shutil: Para copiar e remover arquivos e diretórios.
# time: Para intervalos de sincronização.
# argparse: Para leitura dos argumentos da linha de comando.
# logging: Para registrar as operações realizadas.

#tarefas a fazer:

# linha de comando: caminhos das pastas (pasta original, pasta replica), o intervalo de sincronização e o caminho do ficheiro de registo log
#
# 1. faz um while true para conseguir estar sempre a executar em tempo real
# 2. comecar por ver se o arquivo original tem o mesmo numero de arquivos.
# 3. se tiver mais 1 ou menos 1 faz o update na pasta replica
# 4. faz um for para cada artigo
# 5. se tiver o mesmo numero de arquivos verifica o tamanho e o timestamp e cada artigo.
# 6. se o tamanho e o timestamp forem diferentes atualiza
# 7. se forem igual verifica para cada artigo o MD5.
# 8. se forem diferentes atualiza
# 9. se forem iguais passa ao proximo arquivo
# 10. acaabando for faz se um time.sleep() durante o tempo que for inserido na linha de comandos
# 11. terminando o sleep volta a ponto 2

#calcular o MD5 do ficheiro
def calculate_MD5(file_path,chunk_size=8192):
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(chunk_size), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()

#criar as logs das operações de sincronização
def create_sync_log(logFilePath,replica_file,type):
    logging.basicConfig(filename=logFilePath, level=logging.INFO, format='%(asctime)s - %(message)s')
    match type:
        case "update":
            logging.info(f"Outdated file in the replica, updating: {replica_file}")
        case "insert":
            logging.info(f"Missing file in the replica, to be created: {replica_file}")
        case _:
            logging.info(f"The file or directory has been removed from the replica: {replica_file}")

#Sincronizaçao dos folders
def sync_folders(source,replica, log):
    for dirpath, _, filenames in os.walk(source):
        relative_path = os.path.relpath(dirpath, source)
        replica_path = os.path.normpath(os.path.join(replica, relative_path))

        if not os.path.exists(replica_path):
            os.makedirs(replica_path)
        
        for filename in filenames:
            source_file = os.path.join(dirpath, filename)
            replica_file = os.path.join(replica_path, filename)
            if not os.path.exists(replica_file):
                shutil.copy2(source_file, replica_file)
                create_sync_log(log,replica_file,"insert")
            else:
                if calculate_MD5(source_file) != calculate_MD5(replica_file):
                    shutil.copy2(source_file, replica_file)
                    create_sync_log(log,replica_file,"update")     

    for dirpath, _, filenames in os.walk(replica):
        relative_path = os.path.relpath(dirpath, replica)
        source_path = os.path.normpath(os.path.join(source, relative_path))

        for filename in filenames:
            replica_file = os.path.join(dirpath, filename)
            source_file = os.path.join(source_path, filename)
            if not os.path.exists(source_file):
                os.remove(replica_file)
                create_sync_log(log, replica_file, "remove")

        if not os.path.exists(source_path) and dirpath != replica:
            shutil.rmtree(dirpath)
            create_sync_log(log,dirpath, "remove")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcePath', type=str, help= "path to the source folder")
    parser.add_argument('replicaPath', type=str, help="path to the replica folder")
    parser.add_argument('time', type=int, help= "synchronization interval")
    parser.add_argument('logFilePath',type=str, help="path to the log file")
    args = parser.parse_args()
    
    if(os.path.exists(args.sourcePath)==False or os.path.exists(args.replicaPath)==False or os.path.isfile(args.logFilePath)==False):
        exit("The data passed by parameter is incorrect")

    while True:
        sync_folders(args.sourcePath,args.replicaPath,args.logFilePath)
        time.sleep(args.time)



if __name__ == "__main__":
    main()
