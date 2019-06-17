"""
Inspired from the MRF logic from Pleroma, see https://docs-develop.pleroma.social/mrf.html
To support pluggable / customizable moderation using a programming language if
our exposed features aren't enough.
"""

import logging

import persisting_theory

logger = logging.getLogger("funkwhale.mrf")


class MRFException(Exception):
    pass


class Discard(MRFException):
    pass


class Skip(MRFException):
    pass


class Registry(persisting_theory.Registry):
    look_into = "mrf_policies"

    def __init__(self, name=""):
        self.name = name

        super().__init__()

    def apply(self, payload, **kwargs):
        updated = False
        for rule_name, rule in self.items():
            logger.debug("[MRF.%s] Applying mrf rule %s…", self.name, rule_name)
            try:
                new_payload = rule(payload, **kwargs)
            except Skip as e:
                logger.debug(
                    "[MRF.%s] Skipped rule %s because %s", self.name, rule_name, str(e)
                )
                continue
            except Discard as e:
                logger.info(
                    "[MRF.%s] Discarded message per rule %s because %s",
                    self.name,
                    rule_name,
                    str(e),
                )
                return (None, False)
            except Exception:
                logger.exception(
                    "[MRF.%s] Error while applying rule %s!", self.name, rule_name
                )
                continue
            if new_payload:
                updated = True
                payload = new_payload

        return payload, updated


inbox = Registry("inbox")
