from tqdm import tqdm

a = [1, 2, 3]
with tqdm(total=len(a)) as pbar:
    for i in a:
        pbar.set("tt")
        pbar.update(1)
