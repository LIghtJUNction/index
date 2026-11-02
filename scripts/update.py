"""Fetch public repositories and build a dependency-free static index."""
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import shutil
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


def fetch_repositories(owner, request=None):
    request = request or request_json
    repos = []
    page = 1
    while True:
        batch = request(f'https://api.github.com/users/{owner}/repos?type=owner&sort=full_name&per_page=100&page={page}')
        if not isinstance(batch, list):
            raise ValueError('GitHub returned an invalid repository list')
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def request_json(url):
    headers = {'Accept': 'application/vnd.github+json', 'User-Agent': 'github-project-index'}
    token = os.environ.get('GH_TOKEN') or os.environ.get('GITHUB_TOKEN')
    if token:
        headers['Authorization'] = f'Bearer {token}'
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return json.load(response)


def normalize(repos, owner):
    result = []
    for repo in repos:
        if repo.get('private') or repo['owner']['login'].lower() != owner.lower():
            continue
        result.append({
            'name': repo['name'],
            'url': f"https://github.com/{owner}/{repo['name']}",
            'description': repo.get('description') or '',
            'language': repo.get('language') or 'Other',
            'stars': repo['stargazers_count'],
            'fork': repo['fork'],
            'archived': repo['archived'],
            'updated': repo.get('pushed_at') or repo['updated_at'],
            'topics': sorted(repo.get('topics', [])),
        })
    return sorted(result, key=lambda repo: repo['name'].lower())


def refresh(owner):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9-]{0,38}', owner):
        raise ValueError('Invalid GitHub username')
    repos = normalize(fetch_repositories(owner), owner)
    if not repos:
        raise ValueError('Empty repository list; preserving the previous snapshot')
    target = ROOT / 'site/projects.json'
    previous = json.loads(target.read_text()) if target.exists() else {}
    if previous.get('owner') == owner and previous.get('projects') == repos:
        print(f'No changes ({len(repos)} public repositories)')
        return
    payload = {'owner': owner, 'synced_at': datetime.now(timezone.utc).isoformat(), 'projects': repos}
    temporary = target.with_suffix('.tmp')
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n')
    temporary.replace(target)
    print(f'Updated {len(repos)} public repositories')


def build():
    source = ROOT / 'site'
    data = json.loads((source / 'projects.json').read_text())
    if not data['projects']:
        raise ValueError('Cannot publish an empty index')
    output = ROOT / 'dist'
    output.mkdir(exist_ok=True)
    for name in ('index.html', 'style.css', 'app.js', 'projects.json'):
        shutil.copyfile(source / name, output / name)
    (output / '.nojekyll').touch()
    print(f'Built {len(data["projects"])} projects into dist/')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--owner', default='LIghtJUNction')
    parser.add_argument('--refresh', action='store_true')
    args = parser.parse_args()
    if args.refresh:
        refresh(args.owner)
    build()
