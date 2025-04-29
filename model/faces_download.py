import os
from icrawler.builtin import GoogleImageCrawler
from PIL import Image

def download_images(celebrity_name, num_images=100, output_dir='celebs_dataset'):
    celeb_folder = os.path.join(output_dir, celebrity_name.replace(' ', '_'))
    os.makedirs(celeb_folder, exist_ok=True)

    crawler = GoogleImageCrawler(storage={'root_dir': celeb_folder})
    crawler.crawl(keyword=celebrity_name, max_num=num_images * 2)  # Download extra for filtering

    valid_images = []
    for filename in os.listdir(celeb_folder):
        file_path = os.path.join(celeb_folder, filename)
        try:
            with Image.open(file_path) as img:
                img.verify()
            valid_images.append(file_path)
        except Exception as e:
            print(f"Removing corrupted file: {file_path} ({e})")
            os.remove(file_path)

    if len(valid_images) > num_images:
        for extra_file in valid_images[num_images:]:
            os.remove(extra_file)

    print(f"Finished! {min(len(valid_images), num_images)} images saved in {celeb_folder}")

def read_celebrities_from_txt(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        celebrities = [line.strip() for line in f if line.strip()]
    return celebrities

if __name__ == "__main__":
    celebrities_file = "celebrities.txt"  # <-- your TXT file
    celebrity_list = read_celebrities_from_txt(celebrities_file)

    for celeb in celebrity_list:
        print(f"Downloading for {celeb}...")
        download_images(celeb, num_images=100)
