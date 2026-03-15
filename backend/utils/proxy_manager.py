import random
from pathlib import Path
from typing import Optional
from backend.utils.logger import log
from config.settings import settings


class ProxyManager:
    """
    Proxy listesini yükler, sırayla veya rastgele rotate eder.
    proxies.txt formatı (her satır):
        http://user:pass@host:port
        socks5://host:port
    """

    def __init__(self):
        self._proxies: list[str] = []
        self._index: int = 0
        self._load()

    def _load(self):
        path = Path(settings.proxy_file)
        if not path.exists():
            log.warning(f"Proxy dosyası bulunamadı: {path}")
            return

        lines = path.read_text(encoding="utf-8").splitlines()
        self._proxies = [l.strip() for l in lines if l.strip() and not l.startswith("#")]
        log.info(f"{len(self._proxies)} proxy yüklendi.")

    def get(self) -> Optional[str]:
        if not self._proxies:
            return None

        if settings.proxy_rotation:
            proxy = random.choice(self._proxies)
        else:
            proxy = self._proxies[self._index % len(self._proxies)]
            self._index += 1

        log.debug(f"Seçilen proxy: {proxy}")
        return proxy

    def remove(self, proxy: str):
        """Başarısız proxy'yi listeden çıkar."""
        if proxy in self._proxies:
            self._proxies.remove(proxy)
            log.warning(f"Proxy listeden kaldırıldı: {proxy} ({len(self._proxies)} kaldı)")

    @property
    def count(self) -> int:
        return len(self._proxies)


proxy_manager = ProxyManager()
