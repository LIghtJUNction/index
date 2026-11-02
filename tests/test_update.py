import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts import update


def repository(name='example', **changes):
    return dict(name=name, owner={'login': 'LIghtJUNction'}, private=False,
                description=None, language=None, stargazers_count=2, fork=False,
                archived=False, pushed_at='2026-01-01T00:00:00Z',
                updated_at='2026-01-01T00:00:00Z', topics=[], **changes)


class UpdateTests(unittest.TestCase):
    def test_pagination(self):
        pages = iter([[repository(str(i)) for i in range(100)], [repository('last')]])
        urls = []
        def request(url):
            urls.append(url)
            return next(pages)
        self.assertEqual(len(update.fetch_repositories('LIghtJUNction', request)), 101)
        self.assertIn('page=2', urls[-1])

    def test_filter_private_and_other_owners(self):
        private = repository('private')
        private['private'] = True
        foreign = repository('foreign')
        foreign['owner']['login'] = 'someone-else'
        rows = update.normalize([private, foreign, repository()], 'LIghtJUNction')
        self.assertEqual([r['name'] for r in rows], ['example'])
        self.assertEqual(rows[0]['description'], '')
        self.assertEqual(rows[0]['language'], 'Other')

    def test_stable_order(self):
        rows = [repository('z'), repository('A')]
        self.assertEqual(update.normalize(rows, 'LIghtJUNction'),
                         update.normalize(rows[::-1], 'LIghtJUNction'))

    def test_invalid_api_response(self):
        with self.assertRaises(ValueError):
            update.fetch_repositories('owner', lambda _: {'message': 'error'})

    def test_refresh_idempotence_and_empty_preservation(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(update, 'ROOT', Path(temp)):
            target = Path(temp) / 'site/projects.json'
            target.parent.mkdir()
            with patch.object(update, 'fetch_repositories', return_value=[repository()]):
                update.refresh('LIghtJUNction')
                original = target.read_bytes()
                update.refresh('LIghtJUNction')
                self.assertEqual(target.read_bytes(), original)
            with patch.object(update, 'fetch_repositories', return_value=[]):
                with self.assertRaises(ValueError):
                    update.refresh('LIghtJUNction')
            self.assertEqual(target.read_bytes(), original)

    def test_build_only_publishes_site_files(self):
        with tempfile.TemporaryDirectory() as temp, patch.object(update, 'ROOT', Path(temp)):
            site = Path(temp) / 'site'
            site.mkdir()
            for name in ('index.html', 'app.js', 'style.css'):
                (site / name).write_text('example')
            (site / 'projects.json').write_text(json.dumps({'projects': [{}]}))
            (site / 'secret.txt').write_text('do not publish')
            update.build()
            self.assertEqual({p.name for p in (Path(temp) / 'dist').iterdir()},
                             {'index.html', 'app.js', 'style.css', 'projects.json', '.nojekyll'})


if __name__ == '__main__':
    unittest.main()
