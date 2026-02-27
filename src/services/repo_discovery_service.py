from config import Config

class RepoDiscoveryService:
    """
    Al recibir 'question'.
    """
    def pick_repos(self, question: str):
        repos = Config.AZURE_CORE_REPOS[:]
        if not repos:
            return []

        q = (question or "").lower()

        def score(repo_key: str) -> int:
            # repo_key = "Proyecto/Repo"
            s = 0
            name = repo_key.lower()
            # match simple por tokens
            for tok in q.split():
                if len(tok) >= 4 and tok in name:
                    s += 10
            # boost si es "core"
            if "core" in name:
                s += 3
            return s

        ranked = sorted(repos, key=score, reverse=True)
        return ranked[: Config.MAX_REPOS]
