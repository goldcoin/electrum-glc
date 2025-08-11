from electrum.plugin import hook

from .labels import LabelsPlugin


class Plugin(LabelsPlugin):

    @hook
    def load_wallet(self, wallet, window):
        self.start_wallet(wallet)

    def on_pulled(self, wallet):
        self.logger.info("labels pulled from server")
