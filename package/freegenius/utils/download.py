import ollama
from ollama import pull
from tqdm import tqdm
from freegenius import getDownloadedOllamaModels

class Downloader:

    @staticmethod
    def downloadOllamaModel(model, force=False) -> bool:
        if force or not model in getDownloadedOllamaModels():

            print(f"Downloading '{model}' ...")
            
            try:
                #https://github.com/ollama/ollama-python/blob/main/examples/pull-progress/main.py
                current_digest, bars = '', {}
                for progress in pull(model, stream=True):
                    digest = progress.get('digest', '')
                    if digest != current_digest and current_digest in bars:
                        bars[current_digest].close()

                    if not digest:
                        print(progress.get('status'))
                        continue

                    if digest not in bars and (total := progress.get('total')):
                        bars[digest] = tqdm(total=total, desc=f'pulling {digest[7:19]}', unit='B', unit_scale=True)

                    if completed := progress.get('completed'):
                        bars[digest].update(completed - bars[digest].n)

                    current_digest = digest
            except ollama.ResponseError as e:
                print('Error:', e.error)
                return False
        return True