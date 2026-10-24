import unittest
from update_github import refresh_one, repository_key, visible_count

class GitHubMetricsTests(unittest.TestCase):
    def test_strict_threshold(self):
        for value in (0, 29, 30, -1, '75', None, True):
            self.assertIsNone(visible_count({'stars': value}))
        self.assertEqual(visible_count({'stars': 31}), 31)

    def test_failure_preserves_value_and_timestamp(self):
        previous = {'stars': 75, 'updated_at': '2026-10-24T00:00:00+00:00'}
        def failure(repo):
            raise TimeoutError()
        self.assertEqual(refresh_one('owner/repo', previous, failure), (previous, 'TimeoutError'))

    def test_decrease_hides_badge(self):
        entry, error = refresh_one('owner/repo', {'stars': 31}, lambda _: 30)
        self.assertIsNone(error)
        self.assertIsNone(visible_count(entry))

    def test_only_repository_urls(self):
        self.assertEqual(repository_key('https://github.com/TangJiakai/ReaRec'), 'tangjiakai/rearec')
        self.assertIsNone(repository_key('https://example.com/TangJiakai/ReaRec'))
        self.assertIsNone(repository_key('https://github.com/TangJiakai'))
