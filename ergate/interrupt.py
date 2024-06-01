import signal

from .log import LOG


class DelayedKeyboardInterrupt:
    def __enter__(self) -> None:
        self.signals_received: list[tuple] = []
        self.old_handlers = {
            signal.SIGTERM: signal.signal(signal.SIGTERM, self.handler),
            signal.SIGINT: signal.signal(signal.SIGINT, self.handler),
        }

    def handler(self, sig, frame) -> None:
        self.signals_received.append((sig, frame))
        signal_ = signal.Signals(sig)
        LOG.info("%s received - delaying it", signal_.name)

    def __exit__(self, type, value, traceback) -> None:
        for sig, old_handler in self.old_handlers.items():
            signal.signal(sig, old_handler)

        for signal_ in self.signals_received:
            old_handler = self.old_handlers[signal.Signals(signal_[0])]
            if not callable(old_handler):
                continue
            old_handler(*signal_)
