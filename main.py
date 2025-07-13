import os
import time
import browser_cookie3
import json  # НОВЫЙ ИМПОРТ — ФИКС
import tempfile  # НОВЫЙ ИМПОРТ — ФИКС
from http.cookiejar import MozillaCookieJar
import git  # Для git операций
from datetime import datetime

# Список соцсетей и их доменов (детально: добавь любые — ключ: имя файла/секрета, значение: список доменов для фильтра куки)
SOCIAL_NETWORKS = {
    'youtube': ['.youtube.com', '.google.com', '.googlevideo.com'],  # YouTube + связанные (для видео)
    'instagram': ['.instagram.com', '.facebook.com'],  # Instagram использует FB куки
    'facebook': ['.facebook.com', '.fbcdn.net'],  # FB + CDN
    'tiktok': ['.tiktok.com', '.tiktokv.com'],  # TikTok + видео-домены
    'twitter': ['.twitter.com', '.x.com', '.twimg.com'],  # Twitter/X + изображения
    'reddit': ['.reddit.com', '.redd.it'],  # Reddit + короткие ссылки
    'linkedin': ['.linkedin.com', '.licdn.com'],  # LinkedIn + CDN
    # Добавь другие, e.g.:
    # 'pinterest': ['.pinterest.com', '.pinimg.com'],
    # 'snapchat': ['.snapchat.com'],
    # 'vk': ['.vk.com'],  # Для VK, если нужно
    # 'ok': ['.ok.ru'],  # Одноклассники
}

# GitHub настройки (замени на свои — детально: REPO_PATH — полный путь к папке repo на Mac, e.g., /Users/yourname/cookies-extractor/cookies-repo)
REPO_PATH = '/Users/baer/Downloads/cookies-repo-folder'  # Измени на реальный путь (pwd в Terminal покажет)
GITHUB_TOKEN = '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'  # Твой PAT — для безопасности храни в os.environ['GITHUB_TOKEN'] = 'token' перед запуском
REMOTE_URL = f'https://{GITHUB_TOKEN}@github.com/kingear-mi/c.git'  # Замени yourusername

def extract_cookies(browser='chrome'):
    """Извлекает все куки из браузера. Детально: Поддерживает Chrome или Safari."""
    if browser == 'chrome':
        cookies = browser_cookie3.chrome()
    elif browser == 'safari':
        cookies = browser_cookie3.safari()
    else:
        raise ValueError("Поддерживается только Chrome или Safari.")
    print(f"Извлечено {len(cookies)} куки из {browser}.")
    return cookies

def convert_to_netscape(json_cookies, temp_path):
    """Конвертирует JSON-куки в Netscape формат для yt-dlp. Детально: Создаёт temp файл с domain name value..."""
    with open(temp_path, 'w') as f:
        f.write('# Netscape HTTP Cookie File\n')
        for domain, cookies in json_cookies.items():
            for name, value in cookies.items():
                # Простая конверсия — domain, path ("/"), secure (False), expires (0), name, value
                f.write(f"{domain}\tTRUE\t/\tFALSE\t0\t{name}\t{value}\n")
    print(f"Сконвертировано в {temp_path} для yt-dlp.")

def upload_to_github():
    """Автоматически добавляет все файлы, коммитит и пушит на GitHub. Детально: git.Repo — объект repo, add один файл, commit с timestamp, push на origin."""
    try:
        repo = git.Repo(REPO_PATH)
        repo.git.add('cookies.json')  # Только один файл
        if repo.is_dirty():  # Если есть изменения
            commit_msg = f"Автообновление куки: {datetime.now().isoformat()}"
            repo.index.commit(commit_msg)
            origin = repo.remote(name='origin')
            origin.push()
            print(f"Успешно запушено на GitHub: {commit_msg}. Проверь repo.")
        else:
            print("Нет изменений — ничего не пушим.")
    except Exception as e:
        print(f"Ошибка Git: {str(e)}. Проверь REPO_PATH, token и remote URL.")

def main():
    """Главный цикл: Извлекает, сохраняет все куки в один JSON, конвертирует в Netscape, пушит, ждёт 5 мин."""
    while True:
        print(f"\nНачало цикла: {datetime.now().isoformat()}")
        try:
            cookies = extract_cookies(browser='chrome')  # Или 'safari'
            all_cookies = {}  # Словарь для JSON {domain: {name: value}}
            total_count = 0
            for site, domains in SOCIAL_NETWORKS.items():
                site_count = 0
                domain_dict = {}
                for cookie in cookies:
                    if any(d in cookie.domain for d in domains):
                        domain_dict[cookie.name] = cookie.value  # name:value пары
                        site_count += 1
                        total_count += 1
                if site_count > 0:
                    all_cookies[f"{site}.com"] = domain_dict  # Ключ как домен
                print(f"Добавлено {site_count} куки для {site}. Если 0 — проверь логин.")
            with open('cookies.json', 'w', encoding='utf-8') as f:
                json.dump(all_cookies, f, indent=2, ensure_ascii=False)
            print(f"Всего сохранено {total_count} куки в cookies.json.")
            # Конвертация для yt-dlp (temp Netscape)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.txt') as temp_file:
                convert_to_netscape(all_cookies, temp_file.name)
                repo = git.Repo(REPO_PATH)
                repo.git.add(temp_file.name)  # Добавляем temp файл
                if repo.is_dirty():
                    commit_msg = f"Автообновление Netscape куки: {datetime.now().isoformat()}"
                    repo.index.commit(commit_msg)
                    origin = repo.remote(name='origin')
                    origin.push()
                    print(f"Успешно запушено Netscape: {commit_msg}.")
                os.unlink(temp_file.name)  # Удаляем temp после push
            upload_to_github()  # Пушим JSON
        except Exception as e:
            print(f"Ошибка в цикле: {str(e)}. Продолжаем...")
        print("Ожидание 5 минут...")
        time.sleep(300)  # 5 мин

if __name__ == "__main__":
    main()