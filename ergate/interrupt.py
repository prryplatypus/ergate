import signal


class DelayedKeyboardInterrupt:
    def __enter__(self):
        self.signals_received = []
        self.old_handlers = {
            signal.SIGTERM: signal.signal(signal.SIGTERM, self.handler),
            signal.SIGINT: signal.signal(signal.SIGINT, self.handler),
        }

    def handler(self, sig, frame) -> None:
        self.signals_received.append((sig, frame))
        signal_ = signal.Signals(sig)
        print(f"{signal_.name} received - delaying it")

    def __exit__(self, type, value, traceback) -> None:
        for sig, old_handler in self.old_handlers.items():
            signal.signal(sig, old_handler)

        for signal_ in self.signals_received:
            old_handler = self.old_handlers[signal.Signals(signal_[0])]
            old_handler(*signal_)
